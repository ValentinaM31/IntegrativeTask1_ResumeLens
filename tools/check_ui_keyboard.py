"""Run optional real-browser keyboard checks against a temporary local server."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread

from resumelens.web import create_server


def main():
    node = shutil.which('node')
    if node is None:
        print('Browser checks require Node.js. See README.md for setup.', file=sys.stderr)
        return 2
    script = Path(__file__).with_name('ui_keyboard_checks.cjs')
    with create_server(0) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            env = dict(os.environ, RESUMELENS_UI_URL=f'http://127.0.0.1:{server.server_port}')
            result = subprocess.run([node, str(script)], env=env, check=False)
            return result.returncode
        finally:
            server.shutdown()
            thread.join(timeout=5)


if __name__ == '__main__':
    raise SystemExit(main())
