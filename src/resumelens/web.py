"""Local browser interface; reuse the validated workflow without storing resumes."""
import argparse
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from io import BytesIO
import json
import socket
import sys
from threading import Lock
from urllib.parse import urlsplit
import webbrowser
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from textx import TextXError
from .workflow import process_complete_resume, _bundle_payloads

MAX_TEXT_BYTES = 64 * 1024
MAX_REQUEST_BYTES = 512 * 1024
_PROCESSING_LOCK = Lock()
ASSETS = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/app.css': ('app.css', 'text/css; charset=utf-8'),
    '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
    '/example.txt': ('example.txt', 'text/plain; charset=utf-8'),
}


def process_web_request(payload):
    """Return the complete workflow and validated downloads for one JSON request."""
    if not isinstance(payload, dict) or set(payload) - {'text', 'name'}:
        raise ValueError('Provide a JSON object with text and an optional name.')
    text, name = payload.get('text'), payload.get('name')
    if not isinstance(text, str):
        raise ValueError('Resume text must be a string.')
    # Match utf-8-sig file decoding without changing CRLF or character offsets.
    text = text.removeprefix('\ufeff')
    if not text.strip():
        raise ValueError('Paste a resume or load a nonempty UTF-8 TXT file.')
    if len(text.encode('utf-8')) > MAX_TEXT_BYTES:
        raise ValueError('Resume text exceeds the 64 KiB limit.')
    if name is not None:
        if not isinstance(name, str) or len(name) > 200:
            raise ValueError('The optional name must be a string of at most 200 characters.')
        name = name.strip() or None
    # Serialize cached model/parser access while static requests remain threaded.
    with _PROCESSING_LOCK:
        result = process_complete_resume(text, name)
        payloads = _bundle_payloads(result)
    archive = BytesIO()
    with ZipFile(archive, 'w') as bundle:
        for filename, content in payloads.items():
            item = ZipInfo(filename, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = ZIP_DEFLATED
            bundle.writestr(item, content.encode('utf-8'))
    return {'result': result, 'downloads': payloads,
            'bundle_zip': base64.b64encode(archive.getvalue()).decode('ascii')}


class ResumeLensHandler(BaseHTTPRequestHandler):
    """Serve only packaged assets and one local JSON processing endpoint."""
    server_version = 'ResumeLens'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, format, *args):
        # Do not write resume text, submitted names or browser request data to logs.
        pass

    @property
    def origin(self):
        return 'http://127.0.0.1:' + str(self.server.server_port)

    def _send(self, status, content, mime='application/json; charset=utf-8'):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header('Connection', 'close')
        self.end_headers()
        self.close_connection = True
        self.wfile.write(content)

    def _local_request(self):
        if self.headers.get('Host') != self.origin.removeprefix('http://'):
            self._send(403, {'error': 'Open the interface using the printed 127.0.0.1 URL.'})
            return False
        origin = self.headers.get('Origin')
        if origin is not None and origin != self.origin:
            self._send(403, {'error': 'Requests must come from the local ResumeLens interface.'})
            return False
        return True

    def do_GET(self):
        if not self._local_request():
            return
        asset = ASSETS.get(urlsplit(self.path).path)
        if asset is None:
            self._send(404, {'error': 'Not found.'})
            return
        filename, mime = asset
        self._send(200, files('resumelens').joinpath('ui').joinpath(filename).read_bytes(), mime)

    def do_POST(self):
        if not self._local_request():
            return
        if urlsplit(self.path).path != '/api/process':
            self._send(404, {'error': 'Not found.'})
            return
        if self.headers.get_content_type() != 'application/json':
            self._send(415, {'error': 'Use application/json with UTF-8 encoding.'})
            return
        if self.headers.get('Transfer-Encoding'):
            self._send(400, {'error': 'Chunked requests are not supported.'})
            return
        try:
            length = int(self.headers.get('Content-Length', ''))
        except ValueError:
            self._send(411, {'error': 'A valid Content-Length is required.'})
            return
        if length < 0:
            self._send(400, {'error': 'Content-Length must be nonnegative.'})
            return
        if length > MAX_REQUEST_BYTES:
            self._send(413, {'error': 'The request exceeds the 512 KiB limit.'})
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError('The request body is incomplete.')
            payload = json.loads(raw.decode('utf-8-sig'))
            response = process_web_request(payload)
        except (ValueError, TextXError) as error:
            self._send(400, {'error': str(error)})
        except TimeoutError:
            self._send(408, {'error': 'The request timed out.'})
        except Exception:
            self._send(500, {'error': 'Processing failed. Check the installation and try again.'})
        else:
            self._send(200, response)


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        # Windows must reject an occupied port instead of sharing a reused address.
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def create_server(port=8765):
    """Bind to loopback only; port 0 selects a free port for automated checks."""
    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError('Port must be an integer between 0 and 65535.')
    return LocalHTTPServer(('127.0.0.1', port), ResumeLensHandler)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run the local ResumeLens browser interface.')
    parser.add_argument('--port', type=int, default=8765, help='Local port (default: 8765).')
    parser.add_argument('--no-browser', action='store_true', help='Print the URL without opening a browser.')
    args = parser.parse_args(argv)
    try:
        server = create_server(args.port)
    except (OSError, ValueError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 2
    with server:
        url = 'http://127.0.0.1:' + str(server.server_port)
        print('ResumeLens UI: ' + url, flush=True)
        print('Keep this terminal open. Press Ctrl+C to stop.', flush=True)
        if not args.no_browser:
            try:
                webbrowser.open(url)
            except webbrowser.Error:
                print('Open the printed URL manually.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
