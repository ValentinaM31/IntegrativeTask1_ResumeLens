"""Score the original fourteen workflow cases as a separate regression dataset."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))

from resumelens import parse_candidate_dsl, process_complete_resume, save_bundle
from resumelens.first_stage import validate_result
from resumelens.workflow import _bundle_payloads
from tools.evaluate_preannotated import (digest, load_dataset,
                                        score_case, summarize)

DATASET = ROOT / 'data/workflow-evaluation'


def load_cases(base=DATASET, allow_changed_rules=False):
    dataset = load_dataset(base, allow_changed_rules=allow_changed_rules)
    if len(dataset['cases']) != 14:
        raise ValueError('The original workflow selection must contain fourteen cases')
    original_path = Path(base) / 'history/original_additional_cases.json'
    original = original_path.read_bytes()
    if digest(original) != dataset['protocol']['original_additional_cases_sha256']:
        raise ValueError('The preserved original additional cases changed')
    additional = {case['id']: case for case in json.loads(original)['cases']}
    samples = json.loads((Path(base) / 'history/original_samples.json').read_text(encoding='utf-8'))['cases']
    sample_ids = {Path(case['file']).stem for case in samples}
    if {case['id'] for case in dataset['cases']} != sample_ids | set(additional):
        raise ValueError('The original case selection changed')
    for case in dataset['cases']:
        expected = case['expected']
        links = [{'extracted_index': index, 'canonical': item['canonical']}
                 for index, item in enumerate(expected['positive_mentions'])
                 if item['canonical'] is not None]
        if expected['normalization_evidence'] != links:
            raise ValueError('Annotation links disagree with positive mentions: ' + case['id'])
        if case['id'] in additional:
            prior = additional[case['id']]
            if case['text'] != prior['text'] or expected['accepted_profiles'] != sorted(prior['profiles']):
                raise ValueError('Original additional input/profile expectations changed: ' + case['id'])
        else:
            prior = next(item for item in samples if Path(item['file']).stem == case['id'])
            if (expected['accepted_profiles'] != sorted(prior['accepted_profiles_expected_later'])
                    or expected['normalized_skills'] != prior['normalized_skills']):
                raise ValueError('Original sample expectations changed: ' + case['id'])
    return dataset


def score_workflow_case(case, result=None, error=None):
    row = score_case(case, result, error)
    expected = case['expected']['normalization_evidence']
    actual = result['first_stage']['normalization_evidence'] if result else []
    row['normalization_links'] = {'exact': result is not None and expected == actual,
                                  'expected': expected, 'actual': actual}
    row['candidate_name'] = {'expected': case['expected']['candidate']['name'],
                             'actual': result['first_stage']['candidate']['name'] if result else None}
    row['all_annotations_exact'] = row['all_annotations_exact'] and row['normalization_links']['exact']
    return row


def evaluate_workflow(dataset, processor=process_complete_resume):
    rows = []
    with tempfile.TemporaryDirectory() as temporary:
        for case in dataset['cases']:
            result = None
            try:
                result = processor(case['text'], name=case['name_override'])
                validate_result(result['first_stage'], case['text'])
                _bundle_payloads(result)
                destination = save_bundle(result, Path(temporary) / case['id'])
                candidate = parse_candidate_dsl((destination / 'candidate.rl').read_text(encoding='utf-8'))
                round_trip = (candidate == result['validated_candidate']
                              and (destination / 'candidate.html').read_text(encoding='utf-8') == result['html']
                              and json.loads((destination / 'first_stage.json').read_text(encoding='utf-8')) == result['first_stage']
                              and json.loads((destination / 'classification.json').read_text(encoding='utf-8')) == result['classification'])
            except Exception as error:
                diagnostic = type(error).__name__ + ': ' + str(error)
                try:
                    row = score_workflow_case(case, result, diagnostic)
                except (KeyError, TypeError, ValueError):
                    row = score_workflow_case(case, error=diagnostic)
                row['pipeline_valid'] = False
                row['all_annotations_exact'] = False
                row['export_round_trip'] = False
            else:
                row = score_workflow_case(case, result)
                row['export_round_trip'] = round_trip
            row['passed'] = row['all_annotations_exact'] and row['export_round_trip']
            rows.append(row)
    summary = summarize(rows)
    summary['normalization_links_exact'] = sum(row['normalization_links']['exact'] for row in rows)
    summary['export_round_trip'] = sum(row['export_round_trip'] for row in rows)
    summary['passed'] = sum(row['passed'] for row in rows)
    return {'report_version': '1.0', 'dataset_id': dataset['annotations']['dataset_id'],
            'provenance': dataset['annotations']['provenance'],
            'baseline_commit': dataset['protocol']['baseline_commit'],
            'annotations_sha256': dataset['annotations_sha256'],
            'annotation_freeze_utc': dataset['protocol']['frozen_at_utc'],
            'runtime_unchanged_since_freeze': not dataset['changed_runtime_sources'],
            'changed_runtime_sources': dataset['changed_runtime_sources'],
            'method': 'Exact decoded-text spans, candidate name/field evidence, exclusions, canonical skills, ordered normalization links and profile sets. Temporary JSON/DSL/HTML export round trips. Zero metric denominators are null.',
            'cases': len(rows), 'passed': summary['passed'], 'summary': summary, 'results': rows}


def render_report(report):
    total = report['summary']
    lines = ['# Original fourteen-case workflow regression', '', report['provenance'], '',
             f'Baseline: `{report["baseline_commit"]}`. Annotation SHA-256: `{report["annotations_sha256"]}`.', '',
             f'Fully matching cases and exports: **{report["passed"]}/{report["cases"]}**. Valid pipelines: **{total["pipeline_valid"]}/{report["cases"]}**.', '',
             '| Unit | Exact cases | TP | FP | FN |', '|---|---:|---:|---:|---:|']
    for key in ('positive_mentions', 'excluded_mentions', 'canonical_skills', 'accepted_profiles'):
        value = total[key]
        lines.append(f'| {key} | {value["exact_cases"]}/{report["cases"]} | {value["tp"]} | {value["fp"]} | {value["fn"]} |')
    for field, value in total['candidate_fields'].items():
        lines.append(f'| candidate {field} | {value["exact_cases"]}/{report["cases"]} | {value["tp"]} | {value["fp"]} | {value["fn"]} |')
    for label, key in [('Candidate name', 'candidate_name_exact'), ('Normalization links', 'normalization_links_exact'), ('Export round trip', 'export_round_trip')]:
        lines.append(f'| {label} | {total[key]}/{report["cases"]} | n/a | n/a | n/a |')
    lines += ['', '## Every case', '', '| Case | Labels exact | Export exact |', '|---|---|---|']
    for row in report['results']:
        lines.append(f'| {row["id"]} | {str(row["all_annotations_exact"]).lower()} | {str(row["export_round_trip"]).lower()} |')
    lines += ['', '## Recorded differences', '']
    failures = [row for row in report['results'] if not row['passed']]
    if not failures:
        lines += ['No differences were observed against the fixed annotations in this execution.', '']
    for row in failures:
        lines += [f'### {row["id"]}', '', '```json', json.dumps(row, ensure_ascii=False, indent=2), '```', '']
    lines += ['## Limits', '',
              'This integrates previously executed cases. Eight cases reuse known reference outputs; the six additional cases retain their original texts and profile expectations. Expanded candidate/span/link annotations were added during integration. This is AI-assisted synthetic regression, not a newly blind or independently human-annotated evaluation.', '',
              'The original 23-case extraction evaluation and the separate 18-case preannotated evaluation retain their own datasets and figures. These results are not population-accuracy estimates. See `docs/workflow-evaluation.md` for provenance, scoring and reproduction.', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=DATASET)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--check', action='store_true', help='Verify stored reports without rewriting them')
    parser.add_argument('--allow-changed-rules', action='store_true', help='Mark a later comparison against unchanged annotations')
    args = parser.parse_args(argv)
    try:
        report = evaluate_workflow(load_cases(args.dataset, args.allow_changed_rules))
        markdown = render_report(report)
        output = args.output_dir or args.dataset
        if args.check:
            if (json.loads((output / 'results.json').read_text(encoding='utf-8')) != report
                    or (output / 'results.md').read_text(encoding='utf-8') != markdown):
                raise ValueError('Stored evaluation differs; inspect differences before regenerating')
        else:
            output.mkdir(parents=True, exist_ok=True)
            (output / 'results.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
            (output / 'results.md').write_bytes(markdown.encode('utf-8'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 2
    print(f'Workflow regression: {report["passed"]}/{report["cases"]} cases match all annotations and exports.')
    print('Differences remain in the reports; expectations are not rewritten.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
