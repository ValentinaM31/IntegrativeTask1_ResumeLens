"""Exercise disagreement scoring, corpus preservation and read-only reproduction."""
import copy
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from resumelens import process_complete_resume
from tools.evaluate_workflow import (DATASET, evaluate_workflow, load_cases, main,
                                     render_report, score_workflow_case)


class WorkflowEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_cases()
        cls.case = cls.dataset['cases'][0]
        cls.result = process_complete_resume(cls.case['text'])

    def test_exact_case_and_contact_position_difference(self):
        self.assertTrue(score_workflow_case(self.case, self.result)['all_annotations_exact'])
        changed = copy.deepcopy(self.result)
        changed['first_stage']['candidate']['emails'][0]['start'] += 1
        row = score_workflow_case(self.case, changed)
        self.assertFalse(row['all_annotations_exact'])
        self.assertEqual(row['candidate_fields']['emails']['fp'], 1)
        self.assertEqual(row['candidate_fields']['emails']['fn'], 1)

    def test_translation_link_change_is_detected_with_same_symbols(self):
        changed = copy.deepcopy(self.result)
        changed['first_stage']['normalization_evidence'][0]['extracted_index'] = 999
        row = score_workflow_case(self.case, changed)
        self.assertTrue(row['canonical_skills']['exact'])
        self.assertFalse(row['normalization_links']['exact'])
        self.assertFalse(row['all_annotations_exact'])

    def test_exclusions_and_profiles_are_scored_separately(self):
        case = next(case for case in self.dataset['cases'] if case['id'] == 'negated_framework')
        result = process_complete_resume(case['text'])
        result['first_stage']['excluded_mentions'].clear()
        result['classification']['accepted_profiles'] = ['FULL_STACK_DEVELOPER']
        row = score_workflow_case(case, result)
        self.assertEqual(row['excluded_mentions']['fn'], 1)
        self.assertEqual(row['accepted_profiles']['fp'], 1)
        self.assertFalse(row['all_annotations_exact'])

    def test_corrupted_annotations_are_rejected_before_processing(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'dataset'
            shutil.copytree(DATASET, target)
            path = target / 'annotations.json'
            annotations = json.loads(path.read_text(encoding='utf-8'))
            annotations['cases'][0]['expected']['candidate']['name'] = 'Invented name'
            path.write_text(json.dumps(annotations), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Annotations changed'):
                load_cases(target)

    def test_original_fourteen_cases_execute_and_round_trip(self):
        report = evaluate_workflow(self.dataset)
        self.assertEqual(report['cases'], 14)
        self.assertEqual(report['passed'], 14)
        self.assertEqual(report['summary']['normalization_links_exact'], 14)
        self.assertEqual(report['summary']['export_round_trip'], 14)
        self.assertIn('not a newly blind', render_report(report))

    def test_pipeline_failures_remain_visible_in_report(self):
        dataset = {**self.dataset, 'cases': [self.case]}
        def failed_processor(*args, **kwargs):
            raise OSError('Simulated export failure')
        for processor in (failed_processor, lambda *args, **kwargs: {}):
            with self.subTest(processor=processor):
                report = evaluate_workflow(dataset, processor)
                self.assertEqual(report['passed'], 0)
                row = report['results'][0]
                self.assertFalse(row['pipeline_valid'])
                self.assertFalse(row['export_round_trip'])
                self.assertIsNotNone(row['pipeline_error'])
                self.assertIn('Recorded differences', render_report(report))

    def test_check_detects_stale_reports_without_rewriting(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'results.json').write_text('{}', encoding='utf-8')
            (target / 'results.md').write_text('KEEP', encoding='utf-8')
            before = {p.name: p.read_bytes() for p in target.iterdir()}
            with redirect_stderr(StringIO()), redirect_stdout(StringIO()):
                code = main(['--check', '--output-dir', str(target)])
            self.assertEqual(code, 2)
            self.assertEqual({p.name: p.read_bytes() for p in target.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
