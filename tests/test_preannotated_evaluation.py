"""Check frozen labels, exact scoring, honest error reporting and reproduction."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from resumelens import process_complete_resume
from tools.evaluate_preannotated import (CANDIDATE_FIELDS, DEFAULT_DATASET, ROOT,
                                        canonical_json, compare_sets, digest,
                                        evaluate, load_dataset, metric,
                                        render_markdown, score_case,
                                        summarize, validate_cases)


def empty_prediction(profiles=(), mentions=(), symbols=(), name=None):
    return {'first_stage': {'extracted_skills': list(mentions), 'excluded_mentions': [],
                           'normalized_skills': list(symbols),
                           'candidate': {'name': name, **{field: [] for field in CANDIDATE_FIELDS}}},
            'classification': {'accepted_profiles': list(profiles)}}


class PreannotatedEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()

    def copied_dataset(self, root):
        target = root / 'corpus'
        shutil.copytree(DEFAULT_DATASET, target)
        return target

    def test_annotations_and_input_bytes_match_the_pre_run_freeze(self):
        dataset = self.dataset
        self.assertEqual(len(dataset['cases']), 18)
        self.assertEqual(sum(case['group'] == 'supported' for case in dataset['cases']), 14)
        self.assertEqual(sum(case['group'] == 'stress' for case in dataset['cases']), 4)
        self.assertEqual(dataset['annotations_sha256'],
                         '16bc5bbe5ec874806d1e6ceac77e9d6b30da0350312d584034501aa52344928e')
        self.assertEqual(dataset['changed_runtime_sources'], [])
        self.assertEqual(digest(canonical_json(dataset['annotations'])), dataset['annotations_sha256'])
        case = next(case for case in dataset['cases'] if case['id'] == 'E13_unicode_bom_crlf')
        raw = (DEFAULT_DATASET / case['input']).read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        self.assertIn('\r\n', case['text'])
        self.assertNotIn('\ufeff', case['text'])
        for item in case['expected']['positive_mentions']:
            self.assertEqual(case['text'][item['start']:item['end']], item['raw'])

    def test_annotation_edits_are_rejected_before_processing(self):
        with tempfile.TemporaryDirectory() as folder:
            base = self.copied_dataset(Path(folder))
            path = base / 'annotations.json'
            value = json.loads(path.read_text(encoding='utf-8'))
            value['cases'][0]['expected']['accepted_profiles'] = []
            path.write_bytes(json.dumps(value).encode('utf-8'))
            with patch('tools.evaluate_preannotated.process_complete_resume') as processor:
                with self.assertRaisesRegex(ValueError, 'Annotations changed after freezing'):
                    load_dataset(base)
                processor.assert_not_called()

    def test_input_byte_edits_are_rejected_even_when_decode_would_match(self):
        with tempfile.TemporaryDirectory() as folder:
            base = self.copied_dataset(Path(folder))
            case = self.dataset['cases'][0]
            path = base / case['input']
            path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes())
            with self.assertRaisesRegex(ValueError, 'Input bytes changed after freezing'):
                load_dataset(base)

    def test_changed_runtime_requires_explicit_later_regression_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT / 'src/resumelens', root / 'src/resumelens')
            path = root / 'src/resumelens/extraction.py'
            path.write_bytes(path.read_bytes() + b'\n# Simulated later rule revision.\n')
            original = (DEFAULT_DATASET / 'protocol.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'Runtime source differs from the freeze'):
                load_dataset(source_root=root)
            later = load_dataset(source_root=root, allow_changed_rules=True)
            self.assertEqual(later['changed_runtime_sources'], ['src/resumelens/extraction.py'])
            self.assertEqual((DEFAULT_DATASET / 'protocol.json').read_bytes(), original)
            # Metadata changes to a later-regression comparison; labels are kept.
            sample = {**later, 'cases': later['cases'][:1]}
            report = evaluate(sample)
            self.assertFalse(report['runtime_unchanged_since_freeze'])
            self.assertEqual(report['comparison_kind'], 'later_regression_comparison')

    def test_duplicate_identifiers_and_invalid_spans_are_rejected(self):
        for mutation in ('duplicate', 'bad_span', 'contradictory_symbol', 'contradictory_profile'):
            with self.subTest(mutation=mutation):
                cases = copy.deepcopy(self.dataset['cases'])
                if mutation == 'duplicate':
                    cases[1]['id'] = cases[0]['id']
                elif mutation == 'bad_span':
                    cases[0]['expected']['positive_mentions'][0]['end'] += 1
                elif mutation == 'contradictory_symbol':
                    cases[0]['expected']['normalized_skills'] = []
                else:
                    cases[0]['expected']['accepted_profiles'] = []
                with self.assertRaises(ValueError):
                    validate_cases(cases, self.dataset['protocol'])

    def test_stale_imported_package_is_detected_even_when_checkout_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            imported = Path(folder) / 'resumelens'
            shutil.copytree(ROOT / 'src/resumelens', imported)
            path = imported / 'classification.py'
            path.write_bytes(path.read_bytes() + b'\n# Simulated stale installed package.\n')
            with patch('tools.evaluate_preannotated.files', return_value=imported):
                with self.assertRaisesRegex(ValueError, 'Runtime source differs from the freeze'):
                    load_dataset()
                later = load_dataset(allow_changed_rules=True)
            self.assertEqual(later['changed_runtime_sources'], ['imported:src/resumelens/classification.py'])

    def test_exact_positions_distinguish_repeated_mentions(self):
        expected = {(0, 6, 'Python'), (8, 14, 'Python')}
        actual = {(0, 6, 'Python'), (9, 15, 'Python')}
        score = compare_sets(expected, actual)
        self.assertEqual((score['tp'], score['fp'], score['fn']), (1, 1, 1))
        self.assertEqual(score['missed'], [[8, 14, 'Python']])
        self.assertEqual(score['false_positive'], [[9, 15, 'Python']])
        self.assertFalse(score['exact'])

    def test_unknown_positive_is_a_span_miss_without_an_invented_enum(self):
        case = next(case for case in self.dataset['cases'] if case['id'] == 'E15_unknown_rust')
        known = [item for item in case['expected']['positive_mentions'] if item['canonical'] is not None]
        predicted = empty_prediction(profiles=case['expected']['accepted_profiles'], mentions=known,
                                     symbols=case['expected']['normalized_skills'], name=case['expected']['candidate']['name'])
        score = score_case(case, predicted)
        self.assertEqual(score['positive_mentions']['fn'], 1)
        self.assertEqual(score['canonical_skills']['fn'], 0)
        self.assertTrue(score['canonical_skills']['exact'])
        self.assertEqual(score['unknown_positive_misses'], [[24, 28, 'Rust']])
        self.assertFalse(score['all_annotations_exact'])

    def test_profile_confusion_counts_false_acceptance_and_false_rejection(self):
        positive = self.dataset['cases'][1]
        negative = self.dataset['cases'][2]
        rows = [score_case(positive, empty_prediction()),
                score_case(negative, empty_prediction(profiles=['MACHINE_LEARNING_ENGINEER']))]
        total = summarize(rows)
        profile = total['profile_confusion']['MACHINE_LEARNING_ENGINEER']
        self.assertEqual((profile['tp'], profile['fp'], profile['fn'], profile['tn']), (0, 1, 1, 0))
        self.assertEqual(total['accepted_profiles']['exact_cases'], 0)

    def test_empty_denominators_and_micro_counts_are_not_macro_averages(self):
        self.assertEqual(metric(0, 0, 0), {'tp': 0, 'fp': 0, 'fn': 0, 'precision': None, 'recall': None, 'f1': None})
        counts = [metric(1, 1, 0), metric(9, 0, 0)]
        total = metric(sum(row['tp'] for row in counts), sum(row['fp'] for row in counts), sum(row['fn'] for row in counts))
        self.assertAlmostEqual(total['precision'], 10 / 11)
        self.assertNotEqual(total['precision'], sum(row['precision'] for row in counts) / 2)

    def test_pipeline_errors_are_recorded_and_later_cases_still_run(self):
        sample = {**self.dataset, 'cases': self.dataset['cases'][:2]}
        calls = []

        def processor(text, name=None):
            calls.append(text)
            if len(calls) == 1:
                raise RuntimeError('Injected processing failure')
            return process_complete_resume(text, name=name)

        report = evaluate(sample, processor=processor)
        self.assertEqual(len(calls), 2)
        self.assertEqual(report['summary']['overall']['pipeline_valid'], 1)
        self.assertEqual(report['cases'][0]['pipeline_error'], 'RuntimeError: Injected processing failure')
        self.assertEqual(report['cases'][0]['positive_mentions']['fn'], 5)
        self.assertTrue(report['cases'][1]['all_annotations_exact'])

    def test_stored_reports_match_execution_with_observed_errors_retained(self):
        report = evaluate(self.dataset)
        stored = json.loads((DEFAULT_DATASET / 'results.json').read_text(encoding='utf-8'))
        self.assertEqual(report, stored)
        self.assertEqual(render_markdown(report), (DEFAULT_DATASET / 'results.md').read_text(encoding='utf-8'))
        self.assertEqual(report['summary']['overall']['pipeline_valid'], 18)
        self.assertEqual(report['summary']['overall']['all_annotations_exact'], 14)
        self.assertEqual(report['summary']['overall']['positive_mentions']['fp'], 3)
        self.assertEqual(report['summary']['overall']['positive_mentions']['fn'], 3)
        self.assertEqual(report['summary']['stress']['cases'], 4)
        for profile in report['summary']['overall']['profile_confusion'].values():
            self.assertEqual(profile['tp'] + profile['fp'] + profile['fn'] + profile['tn'], 18)

    def test_real_cli_checks_reports_and_can_write_to_an_external_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            command = [sys.executable, str(ROOT / 'tools/evaluate_preannotated.py'), '--dataset', str(DEFAULT_DATASET)]
            checked = subprocess.run(command + ['--check'], cwd=root, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn('18 frozen synthetic cases', checked.stdout)
            output = root / 'reports'
            written = subprocess.run(command + ['--output-dir', str(output)], cwd=root, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(written.returncode, 0, written.stderr)
            self.assertEqual(json.loads((output / 'results.json').read_text(encoding='utf-8')),
                             json.loads((DEFAULT_DATASET / 'results.json').read_text(encoding='utf-8')))
            self.assertEqual((output / 'results.md').read_text(encoding='utf-8'),
                             (DEFAULT_DATASET / 'results.md').read_text(encoding='utf-8'))
            # Stale reports fail verification rather than being silently replaced.
            before = (output / 'results.md').read_bytes() + b'edited\n'
            (output / 'results.md').write_bytes(before)
            stale = subprocess.run(command + ['--check', '--output-dir', str(output)], cwd=root,
                                   capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(stale.returncode, 2)
            self.assertEqual((output / 'results.md').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
