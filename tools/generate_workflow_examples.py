"""Execute all four stages and preserve eight complete HTML bundles."""
import json
from pathlib import Path
from resumelens import process_complete_resume, save_bundle

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'workflow'


def main():
    cases = json.loads((ROOT / 'data/expected_samples.json').read_text(encoding='utf-8'))['cases']
    report = []
    for case in cases:
        source = ROOT / case['file']
        # Only stored synthetic fixtures use universal-newline (LF) text.
        # The production API/CLI and acceptance check preserve raw CRLF inputs.
        result = process_complete_resume(source.read_text(encoding='utf-8-sig'))
        if result['classification']['accepted_profiles'] != sorted(case['accepted_profiles_expected_later']):
            raise ValueError('Unexpected workflow profiles for ' + case['file'])
        destination = DEST / source.stem
        save_bundle(result, destination, force=True)
        report.append({'source': case['file'], 'bundle': destination.relative_to(ROOT).as_posix(),
                       'accepted_profiles': result['classification']['accepted_profiles'], 'dsl_validated': True})
    (DEST / 'validation.json').write_text(json.dumps(
        {'status': 'executed_complete_workflow', 'cases': report}, indent=2) + '\n', encoding='utf-8')
    print(f'Complete workflow: {len(report)} validated DSL and HTML bundles generated.')


if __name__ == '__main__':
    main()
