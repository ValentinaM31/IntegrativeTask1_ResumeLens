"use strict";

const byId = (id) => document.getElementById(id);
const form = byId("resume-form");
const textInput = byId("resume-text");
const nameInput = byId("candidate-name");
const fileInput = byId("resume-file");
const fields = byId("input-fields");
const status = byId("status");
const errorMessage = byId("error-message");
const limit = 64 * 1024;
const encoder = new TextEncoder();
let sourceText = "";
let downloadUrls = [];
let busy = false;
const profileNames = {
  FULL_STACK_DEVELOPER: "Full Stack Developer",
  MACHINE_LEARNING_ENGINEER: "Machine Learning Engineer",
  BACKEND_DEVELOPER: "Backend Developer",
  DATA_ENGINEER: "Data Engineer",
};

function message(text, kind = "") {
  status.textContent = kind === "error" ? "" : text;
  status.className = kind;
  errorMessage.textContent = kind === "error" ? text : "";
  byId("error-input-link").hidden = kind !== "error";
}

function clearInvalidInputs() {
  textInput.removeAttribute("aria-invalid");
  textInput.setAttribute("aria-describedby", "input-count");
  fileInput.removeAttribute("aria-invalid");
  fileInput.setAttribute("aria-describedby", "file-help");
}

function inputError(text, input, helpId) {
  message(text, "error");
  input.setAttribute("aria-invalid", "true");
  input.setAttribute("aria-describedby", `${helpId} error-message`);
  input.focus();
}

function startOperation(text) {
  busy = true;
  document.body.classList.add("is-processing");
  clearInvalidInputs();
  message(text);
  const previousFocus = document.activeElement;
  fields.disabled = true;
  form.setAttribute("aria-busy", "true");
  // Disabling a focused control otherwise leaves keyboard users on the body.
  // The status region is outside the busy form, so updates are not deferred.
  if (fields.contains(previousFocus) || previousFocus === document.body) byId("input-heading").focus();
}

function finishOperation(target) {
  busy = false;
  document.body.classList.remove("is-processing");
  fields.disabled = false;
  form.setAttribute("aria-busy", "false");
  // Respect a user who has already tabbed away while the request was pending.
  if (document.activeElement === byId("input-heading") || document.activeElement === document.body) target.focus();
}

function clearResults() {
  byId("results").hidden = true;
  byId("results-link").hidden = true;
  for (const details of byId("results").querySelectorAll("details")) details.open = false;
  byId("report-preview").removeAttribute("srcdoc");
  byId("profile-checks").replaceChildren();
  byId("evidence-options").replaceChildren();
  byId("evidence-content").replaceChildren();
  for (const id of ["first-json", "classification-json", "candidate-dsl"]) byId(id).textContent = "";
  for (const url of downloadUrls) URL.revokeObjectURL(url);
  downloadUrls = [];
  for (const id of ["zip-download", "html-download", "first-download", "classification-download", "dsl-download"]) byId(id).removeAttribute("href");
}

function updateCount() {
  const bytes = encoder.encode(sourceText).length;
  byId("input-count").textContent = bytes ? `${bytes.toLocaleString()} / 65,536 UTF-8 bytes` : "No resume loaded.";
}

function setInput(text) {
  sourceText = text;
  // A textarea displays LF; keep the original decoded file text separately until edited.
  textInput.value = text;
  clearResults();
  updateCount();
}

textInput.addEventListener("input", () => {
  clearInvalidInputs();
  sourceText = textInput.value;
  fileInput.value = "";
  byId("file-name").textContent = "No file selected";
  clearResults();
  updateCount();
  message("Resume edited. Process it to update the results.");
});
nameInput.addEventListener("input", () => {
  clearInvalidInputs();
  clearResults();
  message("Name updated. Process the resume again.");
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file || busy) return;
  setInput("");
  startOperation(`Loading ${file.name}…`);
  let target = textInput;
  try {
    if (!file.name.toLowerCase().endsWith(".txt")) throw new Error("Choose a TXT file.");
    if (file.size > limit + 3) throw new Error("The file exceeds the 64 KiB limit.");
    let text;
    try {
      text = new TextDecoder("utf-8", {fatal: true}).decode(await file.arrayBuffer());
    } catch (error) {
      throw new Error("The file could not be read as UTF-8. Save it as UTF-8 TXT and try again.");
    }
    if (!text.trim()) throw new Error("The selected file is empty.");
    if (encoder.encode(text).length > limit) throw new Error("Resume text exceeds the 64 KiB limit.");
    setInput(text);
    byId("file-name").textContent = file.name;
    message(`Loaded ${file.name}. Ready to process.`);
  } catch (error) {
    fileInput.value = "";
    byId("file-name").textContent = "No file selected";
    message(error.message, "error");
    fileInput.setAttribute("aria-invalid", "true");
    fileInput.setAttribute("aria-describedby", "file-help error-message");
    target = fileInput;
  } finally {
    finishOperation(target);
  }
});

byId("example-button").addEventListener("click", async () => {
  if (busy) return;
  clearResults();
  startOperation("Loading example…");
  let target = textInput;
  try {
    const response = await fetch("/example.txt", {cache: "no-store"});
    if (!response.ok) throw new Error("The example could not be loaded.");
    setInput(await response.text());
    fileInput.value = "";
    byId("file-name").textContent = "No file selected";
    nameInput.value = "";
    message("Synthetic Full Stack example loaded. Select Process resume.");
  } catch (error) {
    message(error.message, "error");
    target = errorMessage;
  } finally {
    finishOperation(target);
  }
});

byId("clear-button").addEventListener("click", () => {
  if (busy) return;
  form.reset();
  byId("file-name").textContent = "No file selected";
  clearInvalidInputs();
  setInput("");
  message("Ready when you are.");
  textInput.focus();
});

for (const id of ["back-to-input", "error-input-link"]) {
  byId(id).addEventListener("click", (event) => {
    event.preventDefault();
    if (busy) byId("input-heading").focus();
    else textInput.focus();
  });
}
byId("results-link").addEventListener("click", (event) => {
  event.preventDefault();
  if (!byId("results").hidden) byId("results-heading").focus();
});

function downloadLink(id, content, mime) {
  const blob = content instanceof Uint8Array ? new Blob([content], {type: mime}) : new Blob([content], {type: `${mime};charset=utf-8`});
  const url = URL.createObjectURL(blob);
  downloadUrls.push(url);
  byId(id).href = url;
}

function renderResults(data) {
  const result = data.result;
  const profiles = result.classification.profiles;
  const accepted = result.classification.accepted_profiles.length;
  byId("metric-skills").textContent = result.first_stage.normalized_skills.length;
  byId("metric-profiles").textContent = accepted;
  byId("metric-mentions").textContent = result.first_stage.extracted_skills.length;
  byId("metric-exclusions").textContent = result.first_stage.excluded_mentions.length;
  byId("results-heading").textContent = result.validated_candidate.name || "Unnamed candidate";
  byId("summary").textContent = `${result.first_stage.normalized_skills.length} normalized qualifications · ${accepted} of 4 profiles accepted · Candidate specification validated`;
  for (const [index, profile] of profiles.entries()) {
    const card = document.createElement("article");
    card.className = "profile-card" + (profile.accepted ? " accepted" : "");
    card.style.setProperty("--delay", `${index * 60}ms`);
    const title = document.createElement("h4");
    title.textContent = profileNames[profile.profile] || profile.profile;
    card.append(title);
    const decision = document.createElement("p");
    decision.className = "decision";
    decision.textContent = profile.accepted ? "Accepted" : "Not accepted";
    card.append(decision);
    for (const message of profile.explanations) {
      const explanation = document.createElement("p");
      explanation.textContent = message;
      card.append(explanation);
    }
    if (profile.compatible_pair_missing && profile.pair_diagnostics) {
      const label = document.createElement("p");
      label.textContent = "Supported pairs — one complete pair is sufficient:";
      card.append(label);
      const alternatives = document.createElement("ul");
      for (const option of profile.pair_diagnostics.alternatives) {
        const item = document.createElement("li");
        item.textContent = option.message;
        alternatives.append(item);
      }
      card.append(alternatives);
    }
    byId("profile-checks").append(card);
  }
  byId("first-json").textContent = data.downloads["first_stage.json"];
  byId("classification-json").textContent = data.downloads["classification.json"];
  byId("candidate-dsl").textContent = data.downloads["candidate.rl"];
  byId("report-preview").srcdoc = result.html;
  downloadLink("first-download", data.downloads["first_stage.json"], "application/json");
  downloadLink("classification-download", data.downloads["classification.json"], "application/json");
  downloadLink("dsl-download", data.downloads["candidate.rl"], "text/plain");
  downloadLink("html-download", data.downloads["candidate.html"], "text/html");
  const zip = Uint8Array.from(atob(data.bundle_zip), (character) => character.charCodeAt(0));
  downloadLink("zip-download", zip, "application/zip");
  byId("results").hidden = false;
  byId("results-link").hidden = false;
  renderEvidence(result);
}

function renderEvidence(result) {
  const first = result.first_stage;
  const characters = Array.from(result.source_text);
  const options = byId("evidence-options");
  const content = byId("evidence-content");
  function select(button, mentions, excluded) {
    for (const item of options.children) item.setAttribute("aria-pressed", String(item === button));
    content.replaceChildren();
    for (const mention of mentions) {
      const row = document.createElement("div");
      row.className = "evidence-row";
      const label = document.createElement("p");
      label.textContent = `${mention.raw} · characters ${mention.start}–${mention.end}${excluded ? ` · ${mention.reason}` : " · positive mention"}`;
      const context = document.createElement("code");
      const mark = document.createElement("mark");
      mark.textContent = characters.slice(mention.start, mention.end).join("");
      context.append(document.createTextNode(characters.slice(Math.max(0, mention.start - 36), mention.start).join("")), mark,
        document.createTextNode(characters.slice(mention.end, mention.end + 36).join("")));
      row.append(label, context);
      content.append(row);
    }
  }
  function option(label, mentions, excluded = false) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => select(button, mentions, excluded));
    options.append(button);
    if (options.children.length === 1) select(button, mentions, excluded);
  }
  for (const canonical of first.normalized_skills) {
    const mentions = first.normalization_evidence.filter((link) => link.canonical === canonical)
      .map((link) => first.extracted_skills[link.extracted_index]);
    option(canonical.replaceAll("_", " "), mentions);
  }
  if (first.excluded_mentions.length) option(`Excluded mentions (${first.excluded_mentions.length})`, first.excluded_mentions, true);
  if (!options.children.length) content.textContent = "No cataloged qualification mentions were found in this text.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  clearResults();
  clearInvalidInputs();
  if (!sourceText.trim()) return inputError("Paste a resume or load a nonempty UTF-8 TXT file.", textInput, "input-count");
  if (encoder.encode(sourceText).length > limit) return inputError("Resume text exceeds the 64 KiB limit.", textInput, "input-count");
  startOperation("Processing resume…");
  let target = byId("results-heading");
  try {
    const response = await fetch("/api/process", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: sourceText, name: nameInput.value.trim() || null}),
    });
    let data;
    try {
      data = await response.json();
    } catch (error) {
      throw new Error("The server returned an unreadable response. Try processing the resume again.");
    }
    if (!response.ok) throw new Error(data.error || "The resume could not be processed.");
    renderResults(data);
    message("Processing complete. Review the profile checks and download the validated outputs.", "success");
  } catch (error) {
    clearResults();
    message(error instanceof TypeError ? "Cannot reach ResumeLens. Keep the server terminal open and try again." : error.message, "error");
    target = errorMessage;
  } finally {
    finishOperation(target);
  }
});
window.addEventListener("beforeunload", () => downloadUrls.forEach((url) => URL.revokeObjectURL(url)));
