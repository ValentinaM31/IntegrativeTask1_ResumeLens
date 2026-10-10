# Local browser interface

The fourth increment supplies the application's interactive UI. It reuses the
complete processing API from the preceding increment. The four professional
profiles remain part of one pipeline; no recognition rules, grammar or JSON 1.0
contract are changed. Package version is 1.4.0. No runtime dependency is added.

## Install and start on Windows

From the repository root in IntelliJ's PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m resumelens.web
```

The command prints `http://127.0.0.1:8765` and attempts to open the default browser.
Keep the terminal open and visit that exact URL. Press Ctrl+C in the terminal to
stop the server. After installation, `.\.venv\Scripts\resumelens-ui.exe` is an
equivalent entry point. On Linux use `.venv/bin/python -m resumelens.web`.

If the port is occupied, use `--port 8766` and visit the newly printed URL. Use
`--no-browser` when opening the URL manually. Opening `ui/index.html` directly
from disk does not run the application: processing requires the Python server.
The address deliberately uses `127.0.0.1`, rather than `localhost` or a LAN host.

## User flow

1. Load a `.txt` file encoded in UTF-8, or paste the resume into the text area.
   The maximum decoded text size is 64 KiB in UTF-8 bytes. A UTF-8 BOM is accepted.
   The **Try an example** button loads a packaged synthetic Full Stack resume.
2. Optionally supply a candidate name when the text has no explicit name.
   A name extracted from the resume takes precedence. Blank fallback names are
   treated as absent; the field is limited to 200 characters.
3. Select **Process resume**. Input controls are disabled while loading or processing.
   The application executes regex extraction, FST translations, all four profile
   recognizers, DSL generation, textX validation and HTML rendering.
4. Review the four independent profile decisions. Rejected profiles display
   missing groups or a missing compatible language/framework pair. Several profiles
   can be accepted. The candidate report appears below these decisions.
5. Expand the processing details to inspect extraction evidence, warnings,
   exclusions, canonical symbols, actual recognition sequences and candidate DSL.
6. Download `first_stage.json`, `classification.json`, `candidate.rl` and
   `candidate.html` separately, or choose **Download all files** for
   `resumelens_bundle.zip`, which contains exactly those four files.
7. Editing input/name, loading another file, clearing the form or a failed request
   removes previous results and download links. Process again to obtain new outputs.

Downloads use the browser's normal save behavior. They do not overwrite repository
files or automatically create an `outputs/` directory. The downloaded HTML report
can be opened independently after stopping the server.

## Architecture and input fidelity

`web.py` uses Python's `ThreadingHTTPServer`, bound only to `127.0.0.1`. Fixed GET
routes serve four packaged resources: `/`, `/app.css`, `/app.js`, `/example.txt`.
`POST /api/process` accepts UTF-8 JSON with `text` and optional `name`, returning
the complete workflow result, four validated text downloads and a base64 ZIP.
The request body limit is 512 KiB to allow JSON escaping of 64 KiB text.
Unexpected fields and invalid types, encoding, JSON or size are rejected.
Cached parser/model access is serialized with a lock; static resource requests
remain threaded. Requests have a ten-second socket timeout.
On Windows, binding uses exclusive address ownership so an occupied port produces
an error instead of sharing another server's address. Choose another `--port` if
an old connection temporarily prevents immediate reuse after stopping the server.

The browser strictly decodes file bytes with `TextDecoder('utf-8', {fatal: true})`.
Loaded file text is retained separately from the text area's LF display. Until
edited, original CRLF reaches the API unchanged; offsets therefore refer to the
decoded file without its BOM. Editing/pasting instead processes the current text
area's LF-normalized text. Evidence offsets are Python character positions, not
JavaScript UTF-16 indices; the UI displays the original evidence/offsets without
attempting JavaScript substring highlighting.

Downloads use the workflow's existing bundle-consistency validation. ZIP entries
use fixed names and timestamps for reproducibility; content equals CLI bundle
content for the same input and fallback name. No classification or HTML is returned
when processing/DSL validation fails.

The server keeps no candidate history and writes no resumes, outputs or request
data to disk. The page keeps the current input/result in memory; browser downloads
are user initiated. Clear/reload removes that page state and revokes download URLs.
Reloading starts a new session with an empty form.

Candidate values use DOM `textContent`; the report uses the existing escaped HTML
renderer and an iframe sandbox without script permissions. No remote assets or
external network requests are required. Requests with a different Origin or Host
are rejected; the page is not permitted to be embedded by another site. The UI is
intended as a local course application, not a public production hosting service.

## Reproduction and acceptance

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/check_web_acceptance.py
.\.venv\Scripts\python.exe tools/check_workflow_acceptance.py
```

The full suite contains 109 tests: the preceding 89 plus 20 real HTTP/entry-point
tests. The web acceptance tool starts/stops its own server on an available port and
compares all eight samples with the public API, validating the four ZIP contents.
It does not require a running UI, a browser automation library or administrator access.
The earlier Windows symlink-permission skip remains acceptable.

Manually verify the actual browser after installation:

| Action | Expected outcome |
|---|---|
| Try an example, then process | Alex Sample report, four decisions, Full Stack accepted |
| Upload sample 08 | Three accepted profiles, repeated contacts and records retained |
| Upload a UTF-8 BOM/CRLF file | Valid output; JSON offsets describe the decoded original file |
| Paste a resume without a name and supply a fallback | Supplied name appears in the report |
| Edit input/name after processing | Old results and downloads disappear |
| Upload invalid UTF-8, PDF, empty or oversized TXT | English error; controls recover; no stale result |
| Download all files and each individual file | ZIP has four files, identical to individual downloads |
| Use narrow window or keyboard navigation | Single-column layout, labeled inputs and visible focus |
| Clear, then reload | Empty input/name and no previous results |
| Stop the server, then process existing page text | Connection error and controls restored |

Chrome for Testing 153.0.8010.12 on Linux was used for automated interaction and
desktop/mobile-width screenshots. Browser QA tooling is separate from runtime and
the unittest suite. Real Windows browser behavior, macOS and other browser engines
still require verification. Limits of extraction, catalog and team-defined profile
patterns remain documented in [evaluation.md](evaluation.md). Final academic
poster/presentation and overall repository-history checks belong to the fifth increment.

## References

- Python [http.server](https://docs.python.org/3.12/library/http.server.html): local
  request handling and the threaded server.
- MDN [TextDecoder](https://developer.mozilla.org/en-US/docs/Web/API/TextDecoder/TextDecoder):
  strict UTF-8 decoding and BOM behavior.
- Python [zipfile](https://docs.python.org/3.12/library/zipfile.html): in-memory ZIP entries.
- Microsoft [socket address ownership](https://learn.microsoft.com/en-us/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse):
  exclusive binding for Windows port conflicts.
- Existing [complete workflow](complete-workflow.md),
  [candidate language](candidate-language.md) and [module design](module-design.md).
