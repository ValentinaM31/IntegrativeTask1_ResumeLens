"use strict";

const byId = (id) => document.getElementById(id);
const form = byId("resume-form");
const textInput = byId("resume-text");
const nameInput = byId("candidate-name");
const fileInput = byId("resume-file");
const fields = byId("input-fields");
const status = byId("status");
const limit = 64 * 1024;
const encoder = new TextEncoder();
let sourceText = "";
let downloadUrls = [];
const profileNames = {
  FULL_STACK_DEVELOPER: "Full Stack Developer",
  MACHINE_LEARNING_ENGINEER: "Machine Learning Engineer",
  BACKEND_DEVELOPER: "Backend Developer",
  DATA_ENGINEER: "Data Engineer",
};

function message(text, kind = "") {
  status.textContent = text;
  status.className = kind;
  status.setAttribute("role", kind === "error" ? "alert" : "status");
}

function clearResults() {
  byId("results").hidden = true;
  byId("report-preview").removeAttribute("srcdoc");
  byId("profile-checks").replaceChildren();
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
  sourceText = textInput.value;
  fileInput.value = "";
  clearResults();
  updateCount();
  message("Resume edited. Process it to update the results.");
});
nameInput.addEventListener("input", () => {
  clearResults();
  message("Name updated. Process the resume again.");
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  setInput("");
  fields.disabled = true;
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
    message(`Loaded ${file.name}. Ready to process.`);
  } catch (error) {
    fileInput.value = "";
    message(error.message, "error");
  } finally {
    fields.disabled = false;
  }
});

byId("example-button").addEventListener("click", async () => {
  clearResults();
  fields.disabled = true;
  message("Loading example…");
  try {
    const response = await fetch("/example.txt", {cache: "no-store"});
    if (!response.ok) throw new Error("The example could not be loaded.");
    setInput(await response.text());
    fileInput.value = "";
    nameInput.value = "";
    message("Synthetic Full Stack example loaded. Select Process resume.");
  } catch (error) {
    message(error.message, "error");
  } finally {
    fields.disabled = false;
  }
});

byId("clear-button").addEventListener("click", () => {
  form.reset();
  setInput("");
  message("Ready when you are.");
  textInput.focus();
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
  byId("results-heading").textContent = result.validated_candidate.name || "Unnamed candidate";
  byId("summary").textContent = `${result.first_stage.normalized_skills.length} normalized qualifications · ${accepted} of 4 profiles accepted · Candidate specification validated`;
  for (const profile of profiles) {
    const card = document.createElement("article");
    card.className = "profile-card" + (profile.accepted ? " accepted" : "");
    const title = document.createElement("h4");
    title.textContent = profileNames[profile.profile] || profile.profile;
    card.append(title);
    const decision = document.createElement("p");
    decision.className = "decision";
    decision.textContent = profile.accepted ? "Accepted" : "Not accepted";
    card.append(decision);
    const explanation = document.createElement("p");
    const missing = profile.missing_groups.map((group) => group.join(" or "));
    if (profile.compatible_pair_missing) missing.push("a compatible language/framework pair");
    explanation.textContent = profile.accepted ? "All required qualification groups are present." : `Missing: ${missing.join("; ") || "an accepted qualification pattern"}.`;
    card.append(explanation);
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
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearResults();
  if (!sourceText.trim()) return message("Paste a resume or load a nonempty UTF-8 TXT file.", "error");
  if (encoder.encode(sourceText).length > limit) return message("Resume text exceeds the 64 KiB limit.", "error");
  fields.disabled = true;
  message("Processing resume…");
  try {
    const response = await fetch("/api/process", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: sourceText, name: nameInput.value.trim() || null}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The resume could not be processed.");
    renderResults(data);
    message("Processing complete. Review the profile checks and download the validated outputs.", "success");
    byId("results").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    clearResults();
    message(error instanceof TypeError ? "Cannot reach ResumeLens. Keep the server terminal open and try again." : error.message, "error");
  } finally {
    fields.disabled = false;
  }
});
window.addEventListener("beforeunload", () => downloadUrls.forEach((url) => URL.revokeObjectURL(url)));
