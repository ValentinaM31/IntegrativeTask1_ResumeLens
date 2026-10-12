"""Record an actual complete test run and its source fingerprints for the poster."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    paths = [path for directory in ('src/resumelens', 'tests')
             for path in (ROOT / directory).rglob('*')
             if path.is_file() and '__pycache__' not in path.parts
             and path.suffix in ('.py', '.json', '.tx', '.html', '.css', '.js', '.txt')]
    report = {'status': 'passed' if result.wasSuccessful() else 'failed',
              'verified_at_utc': datetime.now(timezone.utc).isoformat(),
              'platform': sys.platform, 'python': sys.version.split()[0],
              'tests_run': result.testsRun,
              'passed': result.testsRun - len(result.skipped) - len(result.errors) - len(result.failures),
              'skipped': len(result.skipped), 'errors': len(result.errors), 'failures': len(result.failures),
              'skip_reasons': [reason for _, reason in result.skipped],
              'failure_details': [str(test) + ': ' + trace for test, trace in result.failures + result.errors],
              'source_sha256': {path.relative_to(ROOT).as_posix(): hashlib.sha256(
                  path.read_bytes().replace(b'\r\n', b'\n')).hexdigest() for path in sorted(paths)}}
    destination = ROOT / 'docs/poster/verification.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
