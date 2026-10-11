# Keyboard navigation and accessible feedback

The local interface supports a complete input, processing, result and download
flow with Tab, Shift+Tab, Enter and Space. These changes affect the interface;
the processing API, JSON contracts, profile rules, DSL and report contents are
unchanged. Python runtime dependencies and package version 1.4.0 are unchanged.

## Focus and feedback

| Action | Focus and feedback |
|---|---|
| First Tab after opening the page | A visible Skip to resume input link; Enter bypasses the header |
| Load an example or valid TXT | Loading status and busy form; then focus on Resume text |
| Select an invalid file | Error describes the issue; focus returns to the file chooser, associated with that error |
| Submit empty or oversized text | Focus returns to Resume text with `aria-invalid` and the error in its description |
| Start loading or processing | Input controls disabled; focus moves from the disabled control to the input heading |
| Complete processing | Focus moves to the named results heading, whose description includes the result summary; the next Tab reaches ZIP download |
| Navigate elsewhere while an operation is pending | Completion preserves that focus; Go to results remains available after success |
| Receive a network/server/example error | Controls recover; focus moves to the error, with a following Return to resume input link |
| Edit resume input or clear the form | Previous results, download URLs and expanded panels are removed; Clear focuses Resume text |

The polite status region and assertive error region exist from initial page
load. Their roles are stable and messages use text content. The busy attribute
belongs to the form, while the live regions remain outside it so updates are not
deferred by that busy state. Field validation links the relevant input to its
error through `aria-describedby`; editing or starting a new operation clears
previous invalid markers. An error response that is not readable JSON produces
a useful retry message rather than exposing a parser exception.

Result navigation uses native links with explicit focus destinations. There are
no positive tabindex values or custom Tab handlers. The browser's native details
elements expand with Enter or Space. Their download links are inside the opened
content, separate from the summary controls. Each JSON/DSL download has a distinct
name and each scrollable text region has an accessible label. Arrow keys scroll
the focused text region; Tab and Shift+Tab leave it normally. The preview iframe
retains its title and sandbox.

Visible focus covers links, buttons, inputs, headings and scrollable regions.
Navigation uses normal focus scrolling rather than an animated result jump.
The narrow layout, reduced-motion preference and forced-colors mode are included
in the browser checks.

## Reproduce the actual browser checks

The optional QA scripts are `tools/check_ui_keyboard.py` and
`tools/ui_keyboard_checks.cjs`. The Python script creates its own loopback server
on a free port and closes it after the Node.js checks finish. It uses the installed
ResumeLens component, including its packaged UI resources. No existing UI server
or fixed port is needed.

First install the project normally. For automated interaction checks, use a
Node.js version and operating system supported by Playwright, then run from the
repository root in PowerShell:

```powershell
npm install --prefix .ui-test-deps --no-save --package-lock=false playwright@1.62.1
node .ui-test-deps/node_modules/playwright/cli.js install chromium
.\.venv\Scripts\python.exe tools/check_ui_keyboard.py
```

The `.ui-test-deps/` directory is ignored by Git. Node.js, Playwright and its
browser download are optional QA tools, not dependencies needed to use ResumeLens.
Their installation may require network access. Missing tools or a failed check
return a nonzero exit status; they are not reported as a successful skipped test.

Expected final output: `Keyboard browser acceptance: 18 scenario groups passed`,
followed by the actual Chromium version. These checks are separate from the
168 Python unittest cases. They include:

- A complete keyboard-only example/process/ZIP/edit/clear journey and normal
  forward/reverse input navigation.
- Empty text and byte limits; file chooser activation, BOM/CRLF preservation,
  invalid files and recovery after a failed example load.
- Pending file/example/process operations, disabled controls, duplicate-submit
  protection and preservation of focus when the user navigates away.
- All five downloads activated with Enter and compared byte for byte with the
  actual HTTP response; native details opening, closing and text scrolling.
- Input invalidation, network/server failures, unreadable responses, successful
  retry and repeated errors using the same live regions.
- A 390px layout, reduced motion and high contrast focus visibility.

The check makes actual local HTTP requests and uses a browser engine. Controlled
request delays and injected failures exercise recovery; they are not live network
reliability measurements. To run one scenario group for diagnosis, set
`RESUMELENS_UI_CHECK_FILTER` to part of its printed name. A filter matching no
groups fails. The optional `RESUMELENS_PLAYWRIGHT_MODULE` and
`RESUMELENS_UI_BROWSER` variables allow an existing QA module/browser installation.

## Manual verification without additional QA tools

Start `python -m resumelens.web` with the project's Python and open its printed
URL. Perform this sequence with the mouse left aside:

1. Press Tab to reveal Skip to resume input, then Enter. Tab to the file chooser
   and example button. Press Enter on Try an example; focus should land on the
   loaded resume text.
2. Tab through Candidate name and Process resume. Press Enter to process. Observe
   the loading message, then the focused results heading. Tab once and press
   Enter to download the ZIP.
3. Tab to Edit resume input and press Enter. Edit the text and confirm old results
   disappear. Process again and use the report download and all three details
   panels with Enter/Space, Tab, Shift+Tab and arrow keys.
4. Clear and submit empty text. Confirm focus returns to Resume text and an error
   is shown. Try an invalid TXT file and confirm focus returns to its chooser.
5. With valid text loaded, stop the server and process. Confirm the connection
   error is focused, controls recover, and Tab reaches Return to resume input.
   Restart the server and retry successfully.
6. Repeat in a narrow window and with the operating system's high contrast mode.
   Every focused control should remain identifiable and reachable.

## Verification limits and references

The automated browser checks verify behavior and DOM semantics, not spoken output
from a screen reader. Native Windows interaction, NVDA/JAWS/VoiceOver, other browser
engines and a complete WCAG audit remain outside the recorded Linux verification.
These changes do not constitute a claim of full WCAG conformance.

- W3C [Focus Order](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html):
  meaningful sequential navigation and focus placement.
- W3C [Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html):
  programmatically exposed processing and error feedback.
- W3C [ARIA19](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA19):
  an error live region present before its text is updated.
- Playwright [library usage](https://playwright.dev/docs/library),
  [browser installation](https://playwright.dev/docs/browsers) and
  [supported systems](https://playwright.dev/docs/intro#system-requirements).
