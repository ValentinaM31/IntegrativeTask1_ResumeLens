"""End-to-end compatibility, validated rendering and complete CLI bundles."""
import copy
from contextlib import redirect_stderr, redirect_stdout
from html.parser import HTMLParser
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from textx import TextXSyntaxError
from resumelens import (process_resume, process_complete_resume, parse_candidate_dsl,
                        render_candidate_html, save_bundle)
from resumelens.workflow import BUNDLE_FILES
from resumelens.first_stage import validate_result
from resumelens.workflow_cli import main

ROOT = Path(__file__).resolve().parents[1]


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_data(self, data):
        self.text.append(data)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = ('Name: Ana\nEmail: ana@example.com\nSkills: Python, SQL, ETL, Git.\n'
                     'Education:\nBSc Computing\nMSc Data\nExperience:\nJob one\nJob two')
        self.result = process_complete_resume(self.text)

    def test_eight_samples_preserve_existing_stage_outputs(self):
        cases = json.loads((ROOT / 'data/expected_samples.json').read_text(encoding='utf-8'))['cases']
        for case in cases:
            with self.subTest(sample=case['file']):
                path = ROOT / case['file']
                # Persisted synthetic examples use LF, regardless of checkout line endings.
                # Production API/CLI reads preserve the original text instead.
                text = path.read_text(encoding='utf-8-sig')
                result = process_complete_resume(text)
                self.assertEqual(result['pipeline_version'], '1.0')
                self.assertEqual(result['first_stage'], process_resume(text))
                self.assertEqual(result['classification'], json.loads(
                    (ROOT / 'data/classification' / (path.stem + '.json')).read_text(encoding='utf-8')))
                self.assertEqual(result['validated_candidate'], json.loads(
                    (ROOT / 'data/dsl/valid' / (path.stem + '.json')).read_text(encoding='utf-8')))
                self.assertEqual(result['dsl'],
                    (ROOT / 'data/dsl/valid' / (path.stem + '.rl')).read_text(encoding='utf-8'))
                self.assertEqual(result['html'], render_candidate_html(result['dsl']))
                bundle = ROOT / 'data/workflow' / path.stem
                for filename, field in [('first_stage.json', 'first_stage'), ('classification.json', 'classification')]:
                    self.assertEqual(json.loads((bundle / filename).read_text(encoding='utf-8')), result[field])
                self.assertEqual((bundle / 'candidate.rl').read_text(encoding='utf-8'), result['dsl'])
                self.assertEqual((bundle / 'candidate.html').read_text(encoding='utf-8'), result['html'])

                # CRLF must retain exact evidence offsets while producing the same report.
                crlf_text = text.replace('\n', '\r\n')
                crlf_result = process_complete_resume(crlf_text)
                self.assertEqual(crlf_result['first_stage'], process_resume(crlf_text))
                validate_result(crlf_result['first_stage'], crlf_text)
                for field in ('classification', 'dsl', 'validated_candidate', 'html'):
                    self.assertEqual(crlf_result[field], result[field])
                lf_skills = result['first_stage']['extracted_skills']
                crlf_skills = crlf_result['first_stage']['extracted_skills']
                self.assertEqual(len(crlf_skills), len(lf_skills))
                for lf_skill, crlf_skill in zip(lf_skills, crlf_skills):
                    for boundary in ('start', 'end'):
                        offset = lf_skill[boundary]
                        self.assertEqual(crlf_skill[boundary], offset + text[:offset].count('\n'))
                    self.assertEqual(crlf_text[crlf_skill['start']:crlf_skill['end']], lf_skill['raw'])

    def test_results_are_fresh_and_repeatable(self):
        expected = copy.deepcopy(self.result)
        self.result['first_stage']['candidate']['emails'].clear()
        self.result['validated_candidate']['skills'].clear()
        self.result['classification']['accepted_profiles'].clear()
        self.assertEqual(process_complete_resume(self.text), expected)

    def test_empty_resume_and_fallback_name(self):
        with self.assertRaises(ValueError):
            process_complete_resume('')
        self.assertEqual(process_complete_resume('Skills: Git', name='Fallback')['validated_candidate']['name'], 'Fallback')
        self.assertEqual(process_complete_resume(self.text, name='Fallback')['validated_candidate']['name'], 'Ana')

    def test_missing_name_and_no_accepted_profile_have_explicit_html(self):
        result = process_complete_resume('A resume without known qualifications.')
        self.assertIsNone(result['validated_candidate']['name'])
        self.assertIn('Unnamed candidate', result['html'])
        self.assertIn('No profile meets all required groups.', result['html'])
        self.assertIn('No cataloged qualifications recorded.', result['html'])
        self.assertEqual(result['html'].count('None recorded.'), 3)

    def test_repeated_records_contacts_and_three_profiles_render(self):
        text = (ROOT / 'data/samples/08_multiple_records.txt').read_text(encoding='utf-8')
        result = process_complete_resume(text)
        candidate = result['validated_candidate']
        self.assertEqual(len(candidate['accepted_profiles']), 3)
        self.assertEqual(len(candidate['education']), 2)
        self.assertEqual(len(candidate['experience']), 2)
        self.assertEqual(len(candidate['contacts']), 2)
        for field in ['education', 'experience']:
            for record in candidate[field]:
                self.assertIn(record, result['html'])
        for profile in candidate['accepted_profiles']:
            self.assertIn(profile.replace('_', ' '), result['html'])

    def test_html_escapes_untrusted_text_and_preserves_unicode(self):
        name = 'Ana María <script>alert("x")</script> & Co'
        text = f'Name: {name}\nEducation: <img src=x onerror=alert(1)>\nExperience: Línea α & β'
        html = process_complete_resume(text)['html']
        parser = ReportParser()
        parser.feed(html)
        self.assertIn(name, parser.text)
        self.assertIn('<img src=x onerror=alert(1)>', parser.text)
        self.assertIn('Línea α & β', parser.text)
        self.assertNotIn('script', parser.tags)
        self.assertNotIn('img', parser.tags)
        self.assertNotIn('a', parser.tags)
        self.assertIn('&lt;script&gt;', html)

    def test_report_structure_is_standalone(self):
        parser = ReportParser()
        parser.feed(self.result['html'])
        self.assertEqual(parser.tags.count('h1'), 1)
        self.assertEqual(parser.tags.count('h2'), 5)
        self.assertEqual(parser.tags.count('main'), 1)
        self.assertIn('<html lang="en">', self.result['html'])
        self.assertIn('<meta charset="utf-8">', self.result['html'])
        self.assertIn('name="viewport"', self.result['html'])
        self.assertNotIn('script', parser.tags)
        self.assertNotIn('link', parser.tags)

    def test_renderer_rejects_syntax_errors_before_producing_html(self):
        for source in ['candidate {', self.result['dsl'].replace('skill PYTHON;', 'skill RUST;')]:
            with self.assertRaises(TextXSyntaxError):
                render_candidate_html(source)

    def test_renderer_rejects_invented_or_missing_accepted_profiles(self):
        for source in [self.result['dsl'].replace('profile DATA_ENGINEER;', ''),
                       self.result['dsl'].replace('profile DATA_ENGINEER;', 'profile FULL_STACK_DEVELOPER;')]:
            with self.assertRaises(ValueError):
                render_candidate_html(source)

    def test_bundle_contents_and_utf8_newlines(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'nested' / 'bundle'
            before = copy.deepcopy(self.result)
            self.assertEqual(save_bundle(self.result, destination), destination)
            self.assertEqual(sorted(p.name for p in destination.iterdir()), sorted(BUNDLE_FILES))
            self.assertEqual(json.loads((destination / 'first_stage.json').read_text(encoding='utf-8')), self.result['first_stage'])
            self.assertEqual(json.loads((destination / 'classification.json').read_text(encoding='utf-8')), self.result['classification'])
            self.assertEqual(parse_candidate_dsl((destination / 'candidate.rl').read_text(encoding='utf-8')), self.result['validated_candidate'])
            self.assertEqual((destination / 'candidate.html').read_text(encoding='utf-8'), self.result['html'])
            for filename in BUNDLE_FILES:
                self.assertNotIn(b'\r\n', (destination / filename).read_bytes())
            self.assertEqual(self.result, before)

    def test_existing_last_bundle_file_blocks_all_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            sentinel = destination / 'candidate.html'
            sentinel.write_text('KEEP', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                save_bundle(self.result, destination)
            self.assertEqual([p.name for p in destination.iterdir()], ['candidate.html'])
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'KEEP')

    def test_force_replaces_bundle_files_but_retains_unrelated_files(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            for filename in BUNDLE_FILES:
                (destination / filename).write_text('OLD', encoding='utf-8')
            (destination / 'notes.txt').write_text('KEEP', encoding='utf-8')
            save_bundle(self.result, destination, force=True)
            self.assertEqual((destination / 'candidate.html').read_text(encoding='utf-8'), self.result['html'])
            self.assertEqual((destination / 'notes.txt').read_text(encoding='utf-8'), 'KEEP')

    def test_directory_collision_blocks_all_writes_even_with_force(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            (destination / 'candidate.html').mkdir()
            with self.assertRaises(IsADirectoryError):
                save_bundle(self.result, destination, force=True)
            self.assertEqual([p.name for p in destination.iterdir()], ['candidate.html'])

    def test_inconsistent_bundle_is_rejected_without_creating_destination(self):
        mutations = [lambda r: r.update(pipeline_version='9.0'),
                     lambda r: r['first_stage'].update(schema_version='9.0'),
                     lambda r: r['first_stage']['candidate'].update(name='Other'),
                     lambda r: r['classification']['accepted_profiles'].clear(),
                     lambda r: r['validated_candidate']['skills'].clear(),
                     lambda r: r.update(html='<html>Other</html>')]
        with tempfile.TemporaryDirectory() as folder:
            for i, mutate in enumerate(mutations):
                with self.subTest(mutation=i):
                    result = copy.deepcopy(self.result)
                    mutate(result)
                    destination = Path(folder) / str(i)
                    with self.assertRaises(ValueError):
                        save_bundle(result, destination)
                    self.assertFalse(destination.exists())

    def test_invalid_dsl_and_missing_fields_cannot_create_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'bundle'
            with self.assertRaises(TextXSyntaxError):
                save_bundle({**self.result, 'dsl': 'candidate {'}, destination)
            with self.assertRaises(ValueError):
                save_bundle({}, destination)
            self.assertFalse(destination.exists())

    def test_changed_evidence_and_translation_links_block_export(self):
        mutations = [
            lambda r: r['first_stage']['extracted_skills'][0].update(start=999, end=1005),
            lambda r: r['first_stage']['candidate']['emails'][0].update(raw='other@example.com'),
            lambda r: r['first_stage']['normalization_evidence'][0].update(extracted_index=999),
            lambda r: r.update(source_text='Different source'),
            lambda r: r.pop('source_text'),
            lambda r: r.update(source_text=None),
        ]
        with tempfile.TemporaryDirectory() as folder:
            for index, mutate in enumerate(mutations):
                with self.subTest(mutation=index):
                    result = copy.deepcopy(self.result)
                    mutate(result)
                    destination = Path(folder) / str(index)
                    with self.assertRaises(ValueError):
                        save_bundle(result, destination)
                    self.assertFalse(destination.exists())

    def test_source_text_is_retained_in_memory_and_not_exported(self):
        self.assertEqual(self.result['source_text'], self.text)
        with tempfile.TemporaryDirectory() as folder:
            save_bundle(self.result, folder)
            first = json.loads((Path(folder) / 'first_stage.json').read_text(encoding='utf-8'))
            self.assertNotIn('source_text', first)
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()), sorted(BUNDLE_FILES))

    def test_symlink_output_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'bundle'
            destination.mkdir()
            external = Path(folder) / 'external.html'
            external.write_text('KEEP', encoding='utf-8')
            target = destination / 'candidate.html'
            try:
                target.symlink_to(external)
            except OSError:
                self.skipTest('Creating symlinks requires permissions on this platform')
            with self.assertRaises(ValueError):
                save_bundle(self.result, destination, force=True)
            self.assertEqual(external.read_text(encoding='utf-8'), 'KEEP')
            self.assertFalse((destination / 'first_stage.json').exists())


class WorkflowCliTests(unittest.TestCase):
    def run_cli(self, arguments):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_bom_crlf_manual_name_and_original_positions(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            text = 'Skills: Python, SQL, ETL, Git.\r\nEducation: Maestría α\r\n'
            source.write_bytes(b'\xef\xbb\xbf' + text.encode('utf-8'))
            destination = Path(folder) / 'bundle'
            code, stdout, stderr = self.run_cli([str(source), '-o', str(destination), '--name', 'Ana'])
            self.assertEqual(code, 0)
            self.assertEqual(stderr, '')
            self.assertIn('DATA_ENGINEER', stdout)
            first = json.loads((destination / 'first_stage.json').read_text(encoding='utf-8'))
            self.assertEqual(first, process_resume(text, 'Ana'))
            for evidence in first['extracted_skills']:
                self.assertEqual(text[evidence['start']:evidence['end']], evidence['raw'])
            self.assertIn('Maestría α', (destination / 'candidate.html').read_text(encoding='utf-8'))

    def test_missing_wrong_extension_invalid_encoding_and_empty_input(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            destination = Path(folder) / 'bundle'
            cases = [('missing.txt', None), ('resume.pdf', b'Name: Ana'),
                     ('resume.txt', b'\xff'), ('resume.txt', b'')]
            for filename, payload in cases:
                with self.subTest(filename=filename, payload=payload):
                    source = Path(folder) / filename
                    if payload is not None:
                        source.write_bytes(payload)
                    code, stdout, stderr = self.run_cli([str(source), '-o', str(destination)])
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, '')
                    self.assertIn('Error:', stderr)
                    self.assertFalse(destination.exists())

    def test_default_overwrite_rejection_and_force(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            source.write_text('Name: Ana', encoding='utf-8')
            destination = Path(folder) / 'bundle'
            args = [str(source), '-o', str(destination)]
            self.assertEqual(self.run_cli(args)[0], 0)
            before = {p.name: p.read_bytes() for p in destination.iterdir()}
            source.write_text('Name: Other', encoding='utf-8')
            self.assertEqual(self.run_cli(args)[0], 2)
            self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()}, before)
            self.assertEqual(self.run_cli(args + ['--force'])[0], 0)
            self.assertIn('Other', (destination / 'candidate.html').read_text(encoding='utf-8'))

    def test_input_alias_is_protected_even_with_force(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            source.write_text('Name: Ana', encoding='utf-8')
            destination = Path(folder) / 'bundle'
            destination.mkdir()
            try:
                os.link(source, destination / 'first_stage.json')
            except OSError:
                self.skipTest('Hard links are unavailable on this filesystem')
            code, stdout, stderr = self.run_cli([str(source), '-o', str(destination), '--force'])
            self.assertEqual(code, 2)
            self.assertIn('differ from input', stderr)
            self.assertEqual(source.read_text(encoding='utf-8'), 'Name: Ana')

    def test_validation_failure_returns_error_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            source.write_text('Name: Ana', encoding='utf-8')
            destination = Path(folder) / 'bundle'
            with patch('resumelens.workflow.generate_candidate_dsl', return_value='candidate {'):
                code, stdout, stderr = self.run_cli([str(source), '-o', str(destination)])
            self.assertEqual(code, 2)
            self.assertIn('Error:', stderr)
            self.assertFalse(destination.exists())

    def test_module_entry_point_from_outside_project(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.txt'
            source.write_text('Name: Ana\nSkills: Python, SQL, ETL, Git.', encoding='utf-8')
            destination = Path(folder) / 'bundle'
            process = subprocess.run([sys.executable, '-m', 'resumelens.workflow_cli', str(source), '-o', str(destination)],
                                     cwd=folder, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(sorted(p.name for p in destination.iterdir()), sorted(BUNDLE_FILES))


if __name__ == '__main__':
    unittest.main()
