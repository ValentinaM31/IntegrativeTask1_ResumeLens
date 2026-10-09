"""Compare the complete public API with real CLI execution for all eight samples."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from resumelens import process_complete_resume, parse_candidate_dsl

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = json.loads((ROOT / 'data/expected_samples.json').read_text(encoding='utf-8'))['cases']
    with tempfile.TemporaryDirectory(prefix='resumelens-workflow-') as folder:
        for case in cases:
            source = ROOT / case['file']
            with source.open(encoding='utf-8-sig', newline='') as stream:
                result = process_complete_resume(stream.read())
            destination = Path(folder) / source.stem
            process = subprocess.run([sys.executable, '-m', 'resumelens.workflow_cli', str(source), '-o', str(destination)],
                                     cwd=folder, capture_output=True, text=True, encoding='utf-8')
            if process.returncode != 0:
                raise ValueError('Workflow CLI failed for ' + source.stem + ': ' + process.stderr)
            for filename, field in [('first_stage.json', 'first_stage'), ('classification.json', 'classification')]:
                if json.loads((destination / filename).read_text(encoding='utf-8')) != result[field]:
                    raise ValueError('API/CLI differ: ' + source.stem + '/' + filename)
            dsl = (destination / 'candidate.rl').read_text(encoding='utf-8')
            if dsl != result['dsl'] or parse_candidate_dsl(dsl) != result['validated_candidate']:
                raise ValueError('API/CLI candidate specification differs: ' + source.stem)
            if (destination / 'candidate.html').read_text(encoding='utf-8') != result['html']:
                raise ValueError('API/CLI HTML differs: ' + source.stem)
            if result['classification']['accepted_profiles'] != sorted(case['accepted_profiles_expected_later']):
                raise ValueError('Unexpected accepted profiles: ' + source.stem)
    print(f'Complete API/CLI acceptance: {len(cases)} samples agree in all four output files.')


if __name__ == '__main__':
    main()
