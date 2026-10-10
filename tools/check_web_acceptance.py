"""Compare real local HTTP processing/downloads with the public API for eight TXT files."""
import base64
from http.client import HTTPConnection
from io import BytesIO
import json
from pathlib import Path
from threading import Thread
from zipfile import ZipFile
from resumelens import process_complete_resume
from resumelens.web import create_server
from resumelens.workflow import BUNDLE_FILES

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = json.loads((ROOT / 'data/expected_samples.json').read_text(encoding='utf-8'))['cases']
    server = create_server(0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for case in cases:
            with (ROOT / case['file']).open(encoding='utf-8-sig', newline='') as stream:
                text = stream.read()
            expected = process_complete_resume(text)
            connection = HTTPConnection('127.0.0.1', server.server_port, timeout=10)
            try:
                connection.request('POST', '/api/process', json.dumps({'text': text}).encode('utf-8'),
                                   {'Content-Type': 'application/json'})
                response = connection.getresponse()
                data = json.loads(response.read())
                if response.status != 200 or data['result'] != expected:
                    raise ValueError('HTTP/API differ for ' + case['file'])
            finally:
                connection.close()
            if expected['classification']['accepted_profiles'] != sorted(case['accepted_profiles_expected_later']):
                raise ValueError('Unexpected profiles for ' + case['file'])
            with ZipFile(BytesIO(base64.b64decode(data['bundle_zip'], validate=True))) as archive:
                if sorted(archive.namelist()) != sorted(BUNDLE_FILES):
                    raise ValueError('Unexpected ZIP contents')
                for filename in BUNDLE_FILES:
                    if archive.read(filename) != data['downloads'][filename].encode('utf-8'):
                        raise ValueError('ZIP/download differ for ' + filename)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f'Local HTTP/API acceptance: {len(cases)} samples agree; all four ZIP files verified.')


if __name__ == '__main__':
    main()
