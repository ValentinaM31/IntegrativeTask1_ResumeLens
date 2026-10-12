"""Score frozen synthetic labels without deriving expectations from predictions."""
import argparse
import copy
import hashlib
from importlib.resources import files
import json
from pathlib import Path, PurePosixPath
import re
import sys
from resumelens import process_complete_resume
from resumelens.workflow import _bundle_payloads

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / 'data' / 'preannotated-evaluation'
CANDIDATE_FIELDS = ('emails', 'phones', 'links', 'education', 'experience')
PROFILE_IDS = ('FULL_STACK_DEVELOPER', 'MACHINE_LEARNING_ENGINEER',
               'BACKEND_DEVELOPER', 'DATA_ENGINEER')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def span_set(items):
    return {(item['start'], item['end'], item['raw']) for item in items}


def metric(tp, fp, fn):
    return {'tp': tp, 'fp': fp, 'fn': fn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}


def compare_sets(expected, actual):
    ordered = lambda values: [list(value) if isinstance(value, tuple) else value for value in sorted(values)]
    return {**metric(len(expected & actual), len(actual - expected), len(expected - actual)),
            'exact': expected == actual, 'false_positive': ordered(actual - expected),
            'missed': ordered(expected - actual)}


def profiles_from_labels(symbols, reference_profiles):
    """Logical label consistency check; never executes the recognition machines."""
    values = set(symbols)
    return sorted(profile['id'] for profile in reference_profiles
                  if all(values.intersection(group) for group in profile['required_groups'])
                  and (not profile.get('required_pair_alternatives')
                       or any(set(pair) <= values for pair in profile['required_pair_alternatives'])))


def validate_cases(cases, protocol):
    if not isinstance(cases, list) or not cases:
        raise ValueError('Annotations require a nonempty case list')
    identifiers = set()
    inputs = set()
    aliases = {alias.casefold(): item['canonical']
               for item in protocol['annotation_reference_catalog'] for alias in item['aliases']}
    for case in cases:
        identifier = case['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9_]+', identifier):
            raise ValueError('Invalid case identifier')
        if identifier in identifiers or case['input'] in inputs:
            raise ValueError('Duplicate case identifier or input')
        identifiers.add(identifier)
        inputs.add(case['input'])
        if case['group'] not in ('supported', 'stress'):
            raise ValueError('Invalid evaluation group: ' + identifier)
        if not isinstance(case['text'], str) or not case['text'].strip():
            raise ValueError('Empty evaluation input: ' + identifier)
        if case['name_override'] is not None and not isinstance(case['name_override'], str):
            raise ValueError('Invalid name override: ' + identifier)
        expected = case['expected']
        if expected['candidate']['name'] is not None and not isinstance(expected['candidate']['name'], str):
            raise ValueError('Invalid expected candidate name: ' + identifier)
        lists = [expected['positive_mentions'], expected['excluded_mentions']]
        lists.extend(expected['candidate'][field] for field in CANDIDATE_FIELDS)
        for items in lists:
            if not isinstance(items, list):
                raise ValueError('Annotation evidence must be a list: ' + identifier)
            for item in items:
                start, end, raw = item['start'], item['end'], item['raw']
                if (type(start) is not int or type(end) is not int or not isinstance(raw, str)
                        or not 0 <= start < end <= len(case['text'])
                        or case['text'][start:end] != raw):
                    raise ValueError('Invalid exact annotation span: ' + identifier)
            if len(items) != len(span_set(items)):
                raise ValueError('Duplicate evidence annotation: ' + identifier)
        if span_set(expected['positive_mentions']) & span_set(expected['excluded_mentions']):
            raise ValueError('Positive and excluded labels overlap: ' + identifier)
        for item in expected['positive_mentions']:
            if item['canonical'] != aliases.get(item['raw'].casefold()):
                raise ValueError('Annotation canonical symbol disagrees with frozen catalog: ' + identifier)
        derived = sorted({item['canonical'] for item in expected['positive_mentions'] if item['canonical'] is not None})
        if expected['normalized_skills'] != derived:
            raise ValueError('Expected symbols disagree with positive annotations: ' + identifier)
        if expected['accepted_profiles'] != profiles_from_labels(derived, protocol['annotation_reference_profiles']):
            raise ValueError('Profile labels disagree with frozen requirements: ' + identifier)


def load_dataset(base=DEFAULT_DATASET, source_root=ROOT, allow_changed_rules=False):
    base = Path(base)
    protocol = json.loads((base / 'protocol.json').read_text(encoding='utf-8'))
    annotations = json.loads((base / 'annotations.json').read_text(encoding='utf-8'))
    if protocol['protocol_version'] != '1.0' or annotations['annotation_version'] != '1.0':
        raise ValueError('Unsupported annotation/protocol version')
    annotation_hash = digest(canonical_json(annotations))
    if annotation_hash != protocol['annotations_sha256']:
        raise ValueError('Annotations changed after freezing; preserve the original dataset and version a new one')
    cases = copy.deepcopy(annotations['cases'])
    if {case['input'] for case in cases} != set(protocol['input_sha256']):
        raise ValueError('Input manifest differs from annotation cases')
    for case in cases:
        relative = PurePosixPath(case['input'])
        if (relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != 'inputs'
                or not re.fullmatch(r'[A-Za-z0-9_]+\.txt', relative.parts[1])):
            raise ValueError('Invalid evaluation input path')
        raw = (base / Path(*relative.parts)).read_bytes()
        if digest(raw) != protocol['input_sha256'][case['input']]:
            raise ValueError('Input bytes changed after freezing: ' + case['input'])
        case['text'] = raw.decode('utf-8-sig')  # Preserve CRLF; remove only the BOM.
    validate_cases(cases, protocol)
    changed = []
    imported = files('resumelens')
    for relative, frozen_hash in protocol['runtime_source_sha256'].items():
        source = Path(source_root) / relative
        if not source.is_file() or digest(source.read_bytes().replace(b'\r\n', b'\n')) != frozen_hash:
            changed.append(relative)
        # A stale installation must not be mistaken for the checked-out baseline.
        packaged = imported.joinpath(relative.removeprefix('src/resumelens/'))
        try:
            imported_hash = digest(packaged.read_bytes().replace(b'\r\n', b'\n'))
        except OSError:
            imported_hash = None
        if imported_hash != frozen_hash:
            changed.append('imported:' + relative)
    if changed and not allow_changed_rules:
        raise ValueError('Runtime source differs from the freeze; use --allow-changed-rules only for a later regression comparison')
    return {'base': base, 'annotations': annotations, 'protocol': protocol, 'cases': cases,
            'annotations_sha256': annotation_hash, 'changed_runtime_sources': sorted(changed)}


def score_case(case, result=None, error=None):
    expected = case['expected']
    first = result['first_stage'] if result is not None else {
        'extracted_skills': [], 'excluded_mentions': [], 'normalized_skills': [],
        'candidate': {'name': None, **{field: [] for field in CANDIDATE_FIELDS}}}
    actual_profiles = result['classification']['accepted_profiles'] if result is not None else []
    score = {'id': case['id'], 'input': case['input'], 'group': case['group'], 'tags': case['tags'],
             'positive_mentions': compare_sets(span_set(expected['positive_mentions']), span_set(first['extracted_skills'])),
             'excluded_mentions': compare_sets(span_set(expected['excluded_mentions']), span_set(first['excluded_mentions'])),
             'canonical_skills': compare_sets(set(expected['normalized_skills']), set(first['normalized_skills'])),
             'accepted_profiles': compare_sets(set(expected['accepted_profiles']), set(actual_profiles)),
             'unknown_positive_misses': [list(value) for value in sorted(
                 span_set([item for item in expected['positive_mentions'] if item['canonical'] is None])
                 - span_set(first['extracted_skills']))],
             'candidate_name_exact': result is not None and expected['candidate']['name'] == first['candidate']['name'],
             'candidate_fields': {field: compare_sets(span_set(expected['candidate'][field]), span_set(first['candidate'][field]))
                                  for field in CANDIDATE_FIELDS},
             'expected_profiles': expected['accepted_profiles'], 'actual_profiles': sorted(actual_profiles),
             'pipeline_valid': result is not None, 'pipeline_error': error}
    checks = [score[key]['exact'] for key in ('positive_mentions', 'excluded_mentions', 'canonical_skills', 'accepted_profiles')]
    checks.extend(row['exact'] for row in score['candidate_fields'].values())
    score['all_annotations_exact'] = score['pipeline_valid'] and score['candidate_name_exact'] and all(checks)
    return score


def summarize(rows):
    result = {'cases': len(rows), 'pipeline_valid': sum(row['pipeline_valid'] for row in rows),
              'all_annotations_exact': sum(row['all_annotations_exact'] for row in rows),
              'candidate_name_exact': sum(row['candidate_name_exact'] for row in rows),
              'unknown_positive_misses': sum(len(row['unknown_positive_misses']) for row in rows)}
    for key in ('positive_mentions', 'excluded_mentions', 'canonical_skills', 'accepted_profiles'):
        counts = {name: sum(row[key][name] for row in rows) for name in ('tp', 'fp', 'fn')}
        result[key] = {**metric(**counts), 'exact_cases': sum(row[key]['exact'] for row in rows)}
    result['candidate_fields'] = {}
    for field in CANDIDATE_FIELDS:
        counts = {name: sum(row['candidate_fields'][field][name] for row in rows) for name in ('tp', 'fp', 'fn')}
        result['candidate_fields'][field] = {**metric(**counts), 'exact_cases': sum(row['candidate_fields'][field]['exact'] for row in rows)}
    result['profile_confusion'] = {}
    for profile in PROFILE_IDS:
        tp = sum(profile in row['expected_profiles'] and profile in row['actual_profiles'] for row in rows)
        fp = sum(profile not in row['expected_profiles'] and profile in row['actual_profiles'] for row in rows)
        fn = sum(profile in row['expected_profiles'] and profile not in row['actual_profiles'] for row in rows)
        tn = len(rows) - tp - fp - fn
        result['profile_confusion'][profile] = {**metric(tp, fp, fn), 'tn': tn}
    return result


def evaluate(dataset, processor=process_complete_resume):
    rows = []
    for case in dataset['cases']:
        try:
            result = processor(case['text'], name=case['name_override'])
            _bundle_payloads(result)  # Cross-stage integrity, independent of label accuracy.
        except Exception as error:
            rows.append(score_case(case, error=type(error).__name__ + ': ' + str(error)))
        else:
            rows.append(score_case(case, result))
    changed = dataset['changed_runtime_sources']
    protocol = dataset['protocol']
    return {'report_version': '1.0', 'dataset_id': dataset['annotations']['dataset_id'],
            'provenance': dataset['annotations']['provenance'], 'baseline_commit': protocol['baseline_commit'],
            'annotations_sha256': dataset['annotations_sha256'], 'frozen_at_utc': protocol['frozen_at_utc'],
            'runtime_unchanged_since_freeze': not changed, 'changed_runtime_sources': changed,
            'comparison_kind': 'frozen_baseline_comparison' if not changed else 'later_regression_comparison',
            'independence_limit': protocol['independence_limit'],
            'method': 'Exact decoded-text spans, unique canonical symbols and accepted-profile sets; micro metrics. Candidate field spans scored separately. Empty metric denominators are null.',
            'summary': {'overall': summarize(rows), **{group: summarize([row for row in rows if row['group'] == group])
                                                     for group in ('supported', 'stress')}},
            'cases': rows}


def render_markdown(report):
    number = lambda value: 'n/a' if value is None else f'{value:.4f}'
    lines = ['# Preannotated synthetic evaluation', '',
             'Labels and inputs were frozen before this dataset was executed. Texts and labels are AI-assisted synthetic work; no external human annotator or real-resume accuracy is claimed.', '',
             f'Baseline: `{report["baseline_commit"]}`. Annotation SHA-256: `{report["annotations_sha256"]}`.', '',
             f'Runtime unchanged since freeze: **{str(report["runtime_unchanged_since_freeze"]).lower()}**. Comparison: `{report["comparison_kind"]}`.', '',
             '## Positive skill mentions', '',
             '| Group | Cases | TP | FP | FN | Precision | Recall | F1 | Exact cases |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for group in ('supported', 'stress', 'overall'):
        total = report['summary'][group]
        value = total['positive_mentions']
        lines.append(f'| {group} | {total["cases"]} | {value["tp"]} | {value["fp"]} | {value["fn"]} | {number(value["precision"])} | {number(value["recall"])} | {number(value["f1"])} | {value["exact_cases"]}/{total["cases"]} |')
    overall = report['summary']['overall']
    lines += ['', '## Separate outcomes', '', '| Unit | TP | FP | FN | Precision | Recall | F1 | Exact cases |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for key in ('excluded_mentions', 'canonical_skills', 'accepted_profiles'):
        value = overall[key]
        lines.append(f'| {key} | {value["tp"]} | {value["fp"]} | {value["fn"]} | {number(value["precision"])} | {number(value["recall"])} | {number(value["f1"])} | {value["exact_cases"]}/{overall["cases"]} |')
    lines += ['', f'Pipeline/schema/DSL/HTML integrity: **{overall["pipeline_valid"]}/{overall["cases"]}**. All annotation units exact: **{overall["all_annotations_exact"]}/{overall["cases"]}**.', '',
              f'Unknown positive technology spans missed: **{overall["unknown_positive_misses"]}**. Unknown annotations have no invented canonical enum; span misses and canonical agreement are different units.', '',
              '## Candidate data', '', '| Field | TP | FP | FN | Exact cases |', '|---|---:|---:|---:|---:|',
              f'| name (exact value) | n/a | n/a | n/a | {overall["candidate_name_exact"]}/{overall["cases"]} |']
    for field, value in overall['candidate_fields'].items():
        lines.append(f'| {field} | {value["tp"]} | {value["fp"]} | {value["fn"]} | {value["exact_cases"]}/{overall["cases"]} |')
    lines += ['', 'These sparse fields are coverage checks, not estimates of contact/record accuracy on real resumes.', '',
              '## Profile decisions', '', '| Profile | TP | FP | FN | TN |', '|---|---:|---:|---:|---:|']
    for profile, value in overall['profile_confusion'].items():
        lines.append(f'| {profile} | {value["tp"]} | {value["fp"]} | {value["fn"]} | {value["tn"]} |')
    lines += ['', '## Every case', '', '| Case | Group | Mention TP/FP/FN | Actual profiles | All labels exact |',
              '|---|---|---|---|---|']
    for row in report['cases']:
        value = row['positive_mentions']
        lines.append(f'| {row["id"]} | {row["group"]} | {value["tp"]}/{value["fp"]}/{value["fn"]} | {", ".join(row["actual_profiles"]) or "none"} | {str(row["all_annotations_exact"]).lower()} |')
    lines += ['', '## Observed disagreements', '']
    for row in report['cases']:
        if not row['all_annotations_exact']:
            lines += [f'### {row["id"]}', '', f'Input: `{row["input"]}`; tags: {", ".join(row["tags"])}.', '']
            if row['pipeline_error']:
                lines += [f'Pipeline error: `{row["pipeline_error"]}`.', '']
            for key in ('positive_mentions', 'excluded_mentions', 'canonical_skills', 'accepted_profiles'):
                value = row[key]
                if not value['exact']:
                    details = json.dumps({'false_positive': value['false_positive'], 'missed': value['missed']}, ensure_ascii=False)
                    lines += [f'{key}: `{details}`.', '']
            if not row['candidate_name_exact']:
                lines += ['Candidate name differs from its annotation.', '']
            for field, value in row['candidate_fields'].items():
                if not value['exact']:
                    lines += [f'Candidate {field}: `{json.dumps(value, ensure_ascii=False)}`.', '']
    lines += ['## Interpretation and reuse', '',
              'Micro precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2TP/(2TP+FP+FN); zero denominators are n/a. Positions refer to decoded UTF-8-sig text, preserving CRLF. Repeated raw words at different positions are distinct mentions.', '',
              'Internal pipeline validity does not establish correct interpretation of a resume. Dataset construction was informed by prior project behavior. Selected supported/stress cases are not representative of a population; later reuse is regression. Expectations, unsupported cases and observed errors are retained rather than adjusted to match outputs.', '',
              'See `docs/preannotated-evaluation.md` for protocol, formulas, limitations and reproduction.', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Evaluate frozen, preannotated synthetic resumes')
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--output-dir', type=Path, help='Write results.json/results.md here instead of the dataset directory')
    parser.add_argument('--check', action='store_true', help='Compare with stored reports without writing; known errors may remain')
    parser.add_argument('--allow-changed-rules', action='store_true', help='Explicitly mark a later regression comparison; never reset the freeze')
    args = parser.parse_args(argv)
    try:
        dataset = load_dataset(args.dataset, allow_changed_rules=args.allow_changed_rules)
        report = evaluate(dataset)
        output = args.output_dir or args.dataset
        markdown = render_markdown(report)
        if args.check:
            stored = json.loads((output / 'results.json').read_text(encoding='utf-8'))
            if stored != report or (output / 'results.md').read_text(encoding='utf-8') != markdown:
                raise ValueError('Stored evaluation differs; review the case disagreements before regenerating reports')
        else:
            output.mkdir(parents=True, exist_ok=True)
            (output / 'results.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
            (output / 'results.md').write_bytes(markdown.encode('utf-8'))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 2
    total = report['summary']['overall']
    print(f"Evaluated {total['cases']} frozen synthetic cases; {total['all_annotations_exact']} fully match annotations; {total['pipeline_valid']} valid pipelines.")
    print('Known annotation disagreements are reported, not hidden by changing expected labels.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
