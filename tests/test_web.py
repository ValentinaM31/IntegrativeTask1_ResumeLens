"""Real local HTTP integration, downloaded bundles and input validation."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import base64
import http.client
from importlib.resources import files
from io import BytesIO, StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from resumelens import process_complete_resume, parse_candidate_dsl, save_bundle
from resumelens.first_stage import validate_result
from resumelens.web import (MAX_REQUEST_BYTES, MAX_TEXT_BYTES, create_server,
                            main, process_web_request)

ROOT = Path(__file__).resolve().parents[1]


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port
        cls.origin = 'http://127.0.0.1:' + str(cls.port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method='GET', path='/', body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def post(self, payload, headers=None):
        return self.request('POST', '/api/process', json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                            headers or {'Content-Type': 'application/json', 'Origin': self.origin})

    def test_packaged_page_assets_and_example(self):
        for path, name, mime in [('/', 'index.html', 'text/html'), ('/app.js', 'app.js', 'text/javascript'),
                                 ('/app.css', 'app.css', 'text/css'), ('/example.txt', 'example.txt', 'text/plain')]:
            with self.subTest(path=path):
                status, headers, body = self.request(path=path)
                self.assertEqual(status, 200)
                self.assertEqual(body, files('resumelens').joinpath('ui').joinpath(name).read_bytes())
                self.assertIn(mime, headers['Content-Type'])
                self.assertEqual(headers['Cache-Control'], 'no-store')
                self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
                self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])

    def test_eight_samples_http_api_and_zip_match_saved_bundles(self):
        cases = json.loads((ROOT / 'data/expected_samples.json').read_text(encoding='utf-8'))['cases']
        for case in cases:
            with self.subTest(sample=case['file']):
                with (ROOT / case['file']).open(encoding='utf-8-sig', newline='') as stream:
                    text = stream.read()
                expected = process_complete_resume(text)
                status, _, raw = self.post({'text': text})
                self.assertEqual(status, 200, raw)
                data = json.loads(raw)
                self.assertEqual(data['result'], expected)
                self.assertEqual(data['result']['classification']['accepted_profiles'],
                                 sorted(case['accepted_profiles_expected_later']))
                with tempfile.TemporaryDirectory() as folder:
                    save_bundle(expected, folder)
                    saved = {p.name: p.read_bytes() for p in Path(folder).iterdir()}
                with ZipFile(BytesIO(base64.b64decode(data['bundle_zip'], validate=True))) as archive:
                    self.assertEqual(set(archive.namelist()), set(saved))
                    for filename, content in saved.items():
                        self.assertEqual(archive.read(filename), content)
                        self.assertEqual(data['downloads'][filename].encode('utf-8'), content)
                self.assertEqual(parse_candidate_dsl(data['downloads']['candidate.rl']), expected['validated_candidate'])

    def test_bom_crlf_unicode_and_original_evidence(self):
        text = 'Name: Ana 😀\r\nEmail: ana@example.com\r\nSkills: Python, SQL, ETL, Git.\r\n'
        status, _, raw = self.post({'text': '\ufeff' + text})
        self.assertEqual(status, 200, raw)
        result = json.loads(raw)['result']
        self.assertEqual(result, process_complete_resume(text))
        validate_result(result['first_stage'], text)
        self.assertEqual(result['validated_candidate']['name'], 'Ana 😀')
        self.assertIn('DATA_ENGINEER', result['classification']['accepted_profiles'])

    def test_fallback_name_and_explicit_name_precedence(self):
        for text, name, expected in [('Skills: Git', ' María ', 'María'),
                                      ('Name: Alex\nSkills: Git', 'Other', 'Alex'),
                                      ('Skills: Git', '   ', None)]:
            with self.subTest(text=text, name=name):
                status, _, raw = self.post({'text': text, 'name': name})
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(raw)['result']['validated_candidate']['name'], expected)

    def test_empty_invalid_types_and_unknown_fields(self):
        for payload in [None, [], {}, {'text': 42}, {'text': ''}, {'text': '\ufeff \r\n'},
                        {'text': 'Name: Ana', 'name': 5}, {'text': 'Name: Ana', 'name': 'a' * 201},
                        {'text': 'Name: Ana', 'path': 'some-file.txt'}]:
            with self.subTest(payload=payload):
                status, _, raw = self.post(payload)
                self.assertEqual(status, 400)
                self.assertEqual(set(json.loads(raw)), {'error'})

    def test_text_size_uses_utf8_bytes(self):
        accepted = process_web_request({'text': 'a' * MAX_TEXT_BYTES})
        self.assertEqual(accepted['result']['classification']['accepted_profiles'], [])
        for text in ['a' * (MAX_TEXT_BYTES + 1), 'α' * (MAX_TEXT_BYTES // 2 + 1)]:
            status, _, raw = self.post({'text': text})
            self.assertEqual(status, 400)
            self.assertIn('64 KiB', json.loads(raw)['error'])

    def test_malformed_json_utf8_and_nonobject_requests(self):
        for body in [b'{', b'\xff', b'"text"', b'{"text":"\\ud800"}']:
            status, _, raw = self.request('POST', '/api/process', body, {'Content-Type': 'application/json'})
            self.assertEqual(status, 400)
            self.assertIn('error', json.loads(raw))

    def test_content_type_required(self):
        status, _, raw = self.request('POST', '/api/process', b'Name: Ana', {'Content-Type': 'text/plain'})
        self.assertEqual(status, 415)
        self.assertIn('application/json', json.loads(raw)['error'])

    def test_oversized_body_rejected_before_processing(self):
        status, _, raw = self.request('POST', '/api/process', b'',
                                      {'Content-Type': 'application/json', 'Content-Length': str(MAX_REQUEST_BYTES + 1)})
        self.assertEqual(status, 413)
        self.assertIn('512 KiB', json.loads(raw)['error'])

    def test_invalid_length_and_chunked_body(self):
        for headers, expected in [({'Content-Length': 'bad'}, 411),
                                  ({'Content-Length': '-1'}, 400), ({'Transfer-Encoding': 'chunked'}, 400)]:
            status, _, _ = self.request('POST', '/api/process', b'', {'Content-Type': 'application/json', **headers})
            self.assertEqual(status, expected)

    def test_external_origin_and_host_are_rejected(self):
        for headers in [{'Origin': 'https://example.com'}, {'Origin': 'null'}, {'Host': 'example.com'}]:
            status, _, raw = self.post({'text': 'Name: Ana'}, {'Content-Type': 'application/json', **headers})
            self.assertEqual(status, 403)
            self.assertIn('error', json.loads(raw))
        status, _, _ = self.request(headers={'Host': 'example.com'})
        self.assertEqual(status, 403)

    def test_unknown_routes_and_traversal_cannot_read_files(self):
        for path in ['/pyproject.toml', '/../README.md', '/%2e%2e/README.md', '/api/results', '/ui/example.txt']:
            self.assertEqual(self.request(path=path)[0], 404)
        self.assertEqual(self.request('POST', '/wrong', b'{}', {'Content-Type': 'application/json'})[0], 404)

    def test_validation_failure_returns_no_result_or_download(self):
        with patch('resumelens.workflow.generate_candidate_dsl', return_value='candidate {'):
            status, _, raw = self.post({'text': 'Name: Ana'})
        self.assertEqual(status, 400)
        self.assertEqual(set(json.loads(raw)), {'error'})

    def test_unexpected_failure_has_no_traceback_or_resume_content(self):
        with patch('resumelens.web.process_complete_resume', side_effect=RuntimeError('private resume content')):
            status, _, raw = self.post({'text': 'Name: Ana'})
        self.assertEqual(status, 500)
        self.assertNotIn(b'private resume content', raw)
        self.assertNotIn(b'Traceback', raw)

    def test_parallel_candidates_have_independent_results(self):
        texts = [f'Name: Candidate {i}\nSkills: Python, SQL, ETL, Git.' for i in range(8)]
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(lambda text: self.post({'text': text}), texts))
        for i, (status, _, raw) in enumerate(responses):
            self.assertEqual(status, 200, raw)
            self.assertEqual(json.loads(raw)['result']['validated_candidate']['name'], f'Candidate {i}')

    def test_download_archive_is_repeatable_without_shared_state(self):
        first = process_web_request({'text': 'Name: Ana'})
        original_zip = first['bundle_zip']
        first['downloads'].clear()
        first['result']['validated_candidate']['name'] = 'Other'
        second = process_web_request({'text': 'Name: Ana'})
        self.assertEqual(second['bundle_zip'], original_zip)
        self.assertEqual(second['result']['validated_candidate']['name'], 'Ana')


class WebCliTests(unittest.TestCase):
    def test_invalid_port_and_port_conflict_report_error(self):
        server = create_server(0)
        try:
            for port in [-1, 65536, server.server_port]:
                with self.subTest(port=port), redirect_stdout(StringIO()), redirect_stderr(StringIO()) as error:
                    self.assertEqual(main(['--port', str(port), '--no-browser']), 2)
                    self.assertIn('Error:', error.getvalue())
        finally:
            server.server_close()

    def test_control_c_closes_server_without_opening_browser_when_disabled(self):
        stdout = StringIO()
        with patch('resumelens.web.ThreadingHTTPServer.serve_forever', side_effect=KeyboardInterrupt), \
                patch('resumelens.web.webbrowser.open') as browser, redirect_stdout(stdout):
            self.assertEqual(main(['--port', '0', '--no-browser']), 0)
        browser.assert_not_called()
        self.assertIn('http://127.0.0.1:', stdout.getvalue())

    def test_browser_opens_local_url(self):
        with patch('resumelens.web.ThreadingHTTPServer.serve_forever', side_effect=KeyboardInterrupt), \
                patch('resumelens.web.webbrowser.open', return_value=True) as browser, redirect_stdout(StringIO()):
            self.assertEqual(main(['--port', '0']), 0)
        self.assertTrue(browser.call_args.args[0].startswith('http://127.0.0.1:'))

    def test_module_help_outside_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            process = subprocess.run([sys.executable, '-m', 'resumelens.web', '--help'], cwd=folder,
                                     capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn('--no-browser', process.stdout)


if __name__ == '__main__':
    unittest.main()
