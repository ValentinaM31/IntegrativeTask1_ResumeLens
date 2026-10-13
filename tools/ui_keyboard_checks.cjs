"use strict";

// Optional QA only: Node.js and Playwright are not application dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const localModule = path.join(__dirname, "..", ".ui-test-deps", "node_modules", "playwright");
let chromium;
try {
  ({chromium} = require(process.env.RESUMELENS_PLAYWRIGHT_MODULE || localModule));
} catch (error) {
  console.error("Install the optional browser tools as described in README.md.");
  process.exit(2);
}
const url = process.env.RESUMELENS_UI_URL;
if (!url) {
  console.error("Run this check using python tools/check_ui_keyboard.py.");
  process.exit(2);
}

async function active(page, id) {
  await page.waitForFunction((expected) => document.activeElement.id === expected, id);
}

async function ready(page) {
  await page.waitForFunction(() => document.getElementById("resume-form").getAttribute("aria-busy") === "false");
  assert.equal(await page.locator("#input-fields").evaluate((item) => item.disabled), false);
}

async function example(page) {
  await page.locator("#example-button").focus();
  await page.keyboard.press("Enter");
  await active(page, "resume-text");
  await ready(page);
}

async function processResume(page) {
  await page.locator("#process-button").focus();
  const response = page.waitForResponse((item) => item.url().endsWith("/api/process"));
  await page.keyboard.press("Enter");
  const actual = await response;
  assert.equal(actual.status(), 200);
  const data = await actual.json();
  await active(page, "results-heading");
  await ready(page);
  return data;
}

async function download(page, id, filename, expected) {
  await active(page, id);
  const pending = page.waitForEvent("download");
  await page.keyboard.press("Enter");
  const file = await pending;
  assert.equal(file.suggestedFilename(), filename);
  const bytes = await fs.readFile(await file.path());
  assert.deepEqual(bytes, Buffer.isBuffer(expected) ? expected : Buffer.from(expected, "utf8"));
}

function gate() {
  let release;
  const promise = new Promise((resolve) => { release = resolve; });
  return {promise, release};
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.RESUMELENS_UI_BROWSER ? {executablePath: process.env.RESUMELENS_UI_BROWSER} : {}),
  });
  let passed = 0;
  async function check(name, run, options = {}) {
    if (process.env.RESUMELENS_UI_CHECK_FILTER && !name.toLowerCase().includes(process.env.RESUMELENS_UI_CHECK_FILTER.toLowerCase())) return;
    const context = await browser.newContext({baseURL: url, acceptDownloads: true, viewport: {width: 1280, height: 1000}, ...options});
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    try {
      await page.goto("/");
      await run(page);
      assert.deepEqual(errors, [], "Unexpected JavaScript exception");
      passed += 1;
      console.log(`PASS ${name}`);
    } catch (error) {
      throw new Error(`${name}: ${error.message}`, {cause: error});
    } finally {
      await context.close();
    }
  }
  try {
    await check("Skip link and input tab order", async (page) => {
      await page.keyboard.press("Tab");
      assert.equal(await page.locator(".skip-link").evaluate((link) => link === document.activeElement), true);
      assert.ok((await page.locator(".skip-link").boundingBox()).y >= 0);
      await page.keyboard.press("Enter");
      await active(page, "main-content");
      for (const id of ["resume-file", "example-button", "resume-text", "candidate-name", "process-button", "clear-button"]) {
        await page.keyboard.press("Tab");
        await active(page, id);
      }
      await page.keyboard.press("Shift+Tab");
      await active(page, "process-button");
    });

    await check("Complete example workflow using only keyboard navigation", async (page) => {
      await page.keyboard.press("Tab");
      await page.keyboard.press("Enter");
      await page.keyboard.press("Tab");
      await active(page, "resume-file");
      await page.keyboard.press("Tab");
      await active(page, "example-button");
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      await page.keyboard.press("Tab");
      await active(page, "candidate-name");
      await page.keyboard.type("Fallback name");
      await page.keyboard.press("Tab");
      await active(page, "process-button");
      const response = page.waitForResponse((item) => item.url().endsWith("/api/process"));
      await page.keyboard.press("Enter");
      const data = await (await response).json();
      await active(page, "results-heading");
      await page.keyboard.press("Tab");
      await download(page, "zip-download", "resumelens_bundle.zip", Buffer.from(data.bundle_zip, "base64"));
      await page.keyboard.press("Tab");
      await active(page, "back-to-input");
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      for (const id of ["candidate-name", "process-button", "clear-button"]) {
        await page.keyboard.press("Tab");
        await active(page, id);
      }
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      assert.equal(await page.locator("#results").isVisible(), false);
      assert.equal(await page.locator("#resume-text").inputValue(), "");
    });

    await check("Empty input error, field association and recovery", async (page) => {
      let requests = 0;
      page.on("request", (request) => { if (request.url().endsWith("/api/process")) requests += 1; });
      await page.locator("#process-button").focus();
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      assert.equal(await page.locator("#resume-text").getAttribute("aria-invalid"), "true");
      assert.match(await page.locator("#resume-text").getAttribute("aria-describedby"), /error-message/);
      assert.match(await page.getByRole("alert").innerText(), /nonempty/);
      assert.equal(requests, 0);
      await page.keyboard.type("Name: Ana");
      assert.equal(await page.locator("#resume-text").getAttribute("aria-invalid"), null);
      assert.equal(await page.getByRole("alert").innerText(), "");
      await processResume(page);
    });

    await check("UTF-8 byte limit returns focus to the input", async (page) => {
      await page.locator("#resume-text").fill("α".repeat(32769));
      await page.locator("#process-button").focus();
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      assert.match(await page.getByRole("alert").innerText(), /64 KiB/);
      assert.equal(await page.locator("#results").isVisible(), false);
      await ready(page);
    });

    await check("Example busy state and focus after loading", async (page) => {
      const body = await (await page.request.get("/example.txt")).text();
      const pending = gate();
      await page.route("**/example.txt", async (route) => {
        await pending.promise;
        await route.fulfill({status: 200, contentType: "text/plain", body});
      });
      try {
        await page.locator("#example-button").focus();
        await page.keyboard.press("Enter");
        await active(page, "input-heading");
        assert.equal(await page.locator("#resume-form").getAttribute("aria-busy"), "true");
        assert.equal(await page.locator("#input-fields").evaluate((item) => item.disabled), true);
        assert.match(await page.getByRole("status").innerText(), /Loading example/);
      } finally {
        pending.release();
      }
      await active(page, "resume-text");
      assert.equal(await page.locator("#resume-text").inputValue(), body.replace(/\r\n?/g, "\n"));
      await ready(page);
    });

    await check("File chooser by keyboard and BOM/CRLF fidelity", async (page) => {
      const text = "Name: María 😀\r\nSkills: Python, SQL, ETL, Git.\r\n";
      await page.locator("#resume-file").focus();
      const chooser = page.waitForEvent("filechooser");
      await page.keyboard.press("Enter");
      await (await chooser).setFiles({name: "unicode.txt", mimeType: "text/plain", buffer: Buffer.from("\ufeff" + text)});
      await active(page, "resume-text");
      const request = page.waitForRequest((item) => item.url().endsWith("/api/process"));
      const data = await processResume(page);
      assert.equal((await request).postDataJSON().text, text);
      assert.equal(data.result.validated_candidate.name, "María 😀");
      assert.ok(data.result.classification.accepted_profiles.includes("DATA_ENGINEER"));
    });

    await check("File read busy state and focus after loading", async (page) => {
      await page.evaluate(() => {
        const read = File.prototype.arrayBuffer;
        File.prototype.arrayBuffer = function () {
          return new Promise((resolve) => { window.releaseFileRead = () => resolve(read.call(this)); });
        };
      });
      try {
        await page.locator("#resume-file").focus();
        await page.locator("#resume-file").setInputFiles({name: "delayed.txt", mimeType: "text/plain", buffer: Buffer.from("Name: Ana")});
        await active(page, "input-heading");
        assert.equal(await page.locator("#resume-form").getAttribute("aria-busy"), "true");
        assert.equal(await page.locator("#input-fields").evaluate((item) => item.disabled), true);
        assert.match(await page.getByRole("status").innerText(), /Loading delayed.txt/);
      } finally {
        await page.evaluate(() => { if (window.releaseFileRead) window.releaseFileRead(); });
      }
      await active(page, "resume-text");
      await ready(page);
      assert.equal(await page.locator("#resume-text").inputValue(), "Name: Ana");
    });

    await check("Invalid file errors restore controls and file focus", async (page) => {
      for (const file of [{name: "resume.pdf", buffer: Buffer.from("PDF")}, {name: "empty.txt", buffer: Buffer.alloc(0)},
                         {name: "invalid.txt", buffer: Buffer.from([255])}, {name: "large.txt", buffer: Buffer.alloc(65540, 97)}]) {
        await page.locator("#resume-file").focus();
        await page.locator("#resume-file").setInputFiles({...file, mimeType: "text/plain"});
        await active(page, "resume-file");
        await ready(page);
        assert.equal(await page.locator("#resume-file").getAttribute("aria-invalid"), "true");
        assert.match(await page.locator("#resume-file").getAttribute("aria-describedby"), /error-message/);
        assert.ok((await page.getByRole("alert").innerText()).length > 0);
        assert.equal(await page.locator("#results").isVisible(), false);
      }
      await example(page);
      assert.equal(await page.locator("#resume-file").getAttribute("aria-invalid"), null);
    });

    await check("Example failure and keyboard return to input", async (page) => {
      await page.route("**/example.txt", (route) => route.fulfill({status: 503, body: "unavailable"}));
      await page.locator("#example-button").focus();
      await page.keyboard.press("Enter");
      await active(page, "error-message");
      await ready(page);
      assert.match(await page.getByRole("alert").innerText(), /example could not be loaded/);
      await page.keyboard.press("Tab");
      await active(page, "error-input-link");
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
    });

    await check("Processing busy state, duplicate guard and result focus", async (page) => {
      await example(page);
      const pending = gate();
      let requests = 0;
      await page.route("**/api/process", async (route) => {
        requests += 1;
        await pending.promise;
        await route.continue();
      });
      try {
        await page.locator("#process-button").focus();
        await page.keyboard.press("Enter");
        await active(page, "input-heading");
        assert.equal(await page.locator("#resume-form").getAttribute("aria-busy"), "true");
        assert.equal(await page.locator("#process-button").isDisabled(), true);
        assert.match(await page.getByRole("status").innerText(), /Processing resume/);
        await page.waitForFunction(() => document.getElementById("input-fields").disabled);
        await page.evaluate(() => document.getElementById("resume-form").dispatchEvent(new Event("submit", {cancelable: true})));
      } finally {
        pending.release();
      }
      await active(page, "results-heading");
      await ready(page);
      assert.equal(requests, 1);
      await page.keyboard.press("Tab");
      await active(page, "zip-download");
    });

    await check("Pending operation preserves focus after the user tabs away", async (page) => {
      await example(page);
      const pending = gate();
      await page.route("**/api/process", async (route) => { await pending.promise; await route.continue(); });
      try {
        await page.locator("#process-button").focus();
        await page.keyboard.press("Enter");
        await active(page, "input-heading");
        await page.keyboard.press("Shift+Tab");
        assert.equal(await page.getByRole("link", {name: "ResumeLens home"}).evaluate((link) => link === document.activeElement), true);
      } finally {
        pending.release();
      }
      await page.locator("#results").waitFor({state: "visible"});
      await ready(page);
      assert.equal(await page.getByRole("link", {name: "ResumeLens home"}).evaluate((link) => link === document.activeElement), true);
      await page.locator("#results-link").focus();
      await page.keyboard.press("Enter");
      await active(page, "results-heading");
    });

    await check("All five downloads and detail panels operate by keyboard", async (page) => {
      await example(page);
      const data = await processResume(page);
      await page.keyboard.press("Tab");
      await download(page, "zip-download", "resumelens_bundle.zip", Buffer.from(data.bundle_zip, "base64"));
      await page.keyboard.press("Tab");
      await active(page, "back-to-input");
      await page.keyboard.press("Tab");
      await download(page, "html-download", "candidate.html", data.downloads["candidate.html"]);
      assert.equal(await page.locator("summary a, summary button").count(), 0);
      for (const [summary, details, link, filename, pre, key] of [
        ["extraction-summary", "extraction-details", "first-download", "first_stage.json", "first-json", "Enter"],
        ["classification-summary", "classification-details", "classification-download", "classification.json", "classification-json", "Space"],
        ["candidate-summary", "candidate-details", "dsl-download", "candidate.rl", "candidate-dsl", "Enter"],
      ]) {
        await page.locator(`#${summary}`).focus();
        await page.keyboard.press(key);
        assert.equal(await page.locator(`#${details}`).evaluate((item) => item.open), true);
        await page.keyboard.press("Tab");
        await download(page, link, filename, data.downloads[filename]);
        await page.keyboard.press("Tab");
        await active(page, pre);
        assert.equal(await page.locator(`#${pre}`).getAttribute("aria-labelledby"), summary);
        if (pre === "first-json") {
          await page.keyboard.press("ArrowDown");
          await page.waitForFunction((id) => document.getElementById(id).scrollTop > 0, pre);
        }
        await page.keyboard.press("Shift+Tab");
        await active(page, link);
        await page.keyboard.press("Shift+Tab");
        await active(page, summary);
        await page.keyboard.press(key);
        assert.equal(await page.locator(`#${details}`).evaluate((item) => item.open), false);
      }
    });

    await check("Editing, clearing and return links invalidate old outputs", async (page) => {
      await example(page);
      await processResume(page);
      await page.locator("#back-to-input").focus();
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      await page.keyboard.press("End");
      await page.keyboard.type("\nSkills: Angular");
      assert.equal(await page.locator("#results").isVisible(), false);
      assert.equal(await page.locator("#results-link").isVisible(), false);
      assert.equal(await page.locator("#zip-download").getAttribute("href"), null);
      assert.equal(await page.locator("details[open]").count(), 0);
      await page.locator("#clear-button").focus();
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      assert.equal(await page.locator("#resume-text").inputValue(), "");
      assert.equal(await page.locator("#candidate-name").inputValue(), "");
      assert.equal(await page.getByRole("alert").innerText(), "");
    });

    await check("Network failure, keyboard recovery and successful retry", async (page) => {
      await example(page);
      await page.route("**/api/process", (route) => route.abort("failed"));
      await page.locator("#process-button").focus();
      await page.keyboard.press("Enter");
      await active(page, "error-message");
      await ready(page);
      assert.match(await page.getByRole("alert").innerText(), /Keep the server terminal open/);
      assert.equal(await page.locator("#results").isVisible(), false);
      await page.keyboard.press("Tab");
      await active(page, "error-input-link");
      await page.keyboard.press("Enter");
      await active(page, "resume-text");
      await page.unroute("**/api/process");
      await processResume(page);
      assert.equal(await page.getByRole("alert").innerText(), "");
    });

    await check("Server errors and unreadable responses have usable feedback", async (page) => {
      await example(page);
      for (const [body, expected] of [[JSON.stringify({error: "Processing failed. Try again."}), /Processing failed/], ["<html>unavailable</html>", /unreadable response/]]) {
        await page.route("**/api/process", (route) => route.fulfill({status: 500, body}));
        await page.locator("#process-button").focus();
        await page.keyboard.press("Enter");
        await active(page, "error-message");
        await ready(page);
        assert.match(await page.getByRole("alert").innerText(), expected);
        assert.equal(await page.locator("#results").isVisible(), false);
        await page.unroute("**/api/process");
      }
    });

    await check("Repeated errors reuse stable live regions", async (page) => {
      await page.evaluate(() => { window.originalAlert = document.getElementById("error-message"); });
      for (let i = 0; i < 2; i += 1) {
        await page.locator("#resume-text").fill(" ");
        await page.locator("#process-button").focus();
        await page.keyboard.press("Enter");
        await active(page, "resume-text");
        assert.equal(await page.getByRole("status").getAttribute("aria-live"), "polite");
        assert.equal(await page.getByRole("alert").getAttribute("aria-atomic"), "true");
        assert.equal(await page.evaluate(() => document.getElementById("error-message") === window.originalAlert), true);
        assert.match(await page.getByRole("alert").innerText(), /nonempty/);
      }
    });

    await check("Narrow layout, reduced motion and visible focus", async (page) => {
      await example(page);
      await processResume(page);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
      const outline = await page.locator("#results-heading").evaluate((item) => getComputedStyle(item).outlineWidth);
      assert.equal(outline, "3px");
      await page.keyboard.press("Tab");
      await active(page, "zip-download");
      assert.equal(await page.locator("#zip-download").evaluate((item) => getComputedStyle(item).outlineStyle), "solid");
      if (process.env.RESUMELENS_UI_SCREENSHOT_DIR) {
        await fs.mkdir(process.env.RESUMELENS_UI_SCREENSHOT_DIR, {recursive: true});
        await page.screenshot({path: path.join(process.env.RESUMELENS_UI_SCREENSHOT_DIR, "keyboard-mobile.png"), fullPage: true});
      }
    }, {viewport: {width: 390, height: 844}, reducedMotion: "reduce"});

    await check("High contrast mode retains keyboard focus", async (page) => {
      await page.keyboard.press("Tab");
      await page.keyboard.press("Enter");
      await page.keyboard.press("Tab");
      await active(page, "resume-file");
      assert.equal(await page.locator("#resume-file").evaluate((item) => getComputedStyle(item).outlineWidth), "3px");
    }, {forcedColors: "active"});

    if (!passed) throw new Error("No scenario matches RESUMELENS_UI_CHECK_FILTER.");
    console.log(`Keyboard browser acceptance: ${passed} scenario groups passed (Chromium ${browser.version()}).`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`Keyboard browser check failed: ${error.message}`);
  process.exitCode = 1;
});
