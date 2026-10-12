"""Compose all four stages while preserving the first-stage JSON 1.0 contract."""
import json
import os
from pathlib import Path
import shutil
import stat
import time
import warnings
from jsonschema import ValidationError
from .first_stage import process_resume, validate_result
from .classification import classify_skills
from .dsl import generate_candidate_dsl, parse_candidate_dsl
from .rendering import render_candidate_html

BUNDLE_FILES = ("first_stage.json", "classification.json", "candidate.rl", "candidate.html")
BUNDLE_WORKSPACE = ".resumelens-export.lock"


def _replace_file(source, target):
    """Briefly retry Windows file locks; persistent denial still triggers recovery."""
    delays = (0.01, 0.03, 0.08, 0.16, 0.30)
    for attempt in range(len(delays) + 1):
        try:
            return os.replace(source, target)
        except PermissionError as error:
            if getattr(error, "winerror", None) not in (5, 32, 33) or attempt == len(delays):
                raise
            time.sleep(delays[attempt])


class BundleRecoveryError(OSError):
    """A failed export whose original copies must be retained for recovery."""

    def __init__(self, recovery_directory, rollback_errors):
        self.recovery_directory = recovery_directory
        self.rollback_errors = tuple(rollback_errors)
        names = ", ".join(filename for filename, _ in rollback_errors)
        super().__init__(f"Bundle recovery was incomplete for {names}. "
                         f"Original copies are retained at {recovery_directory}. "
                         "Resolve the filesystem error before recovering or retrying.")


def process_complete_resume(text, name=None):
    """Return fresh outputs after extraction, FSTs, recognition and DSL validation."""
    first = process_resume(text, name)
    classification = classify_skills(first["normalized_skills"])
    source = generate_candidate_dsl(first, classification)
    candidate = parse_candidate_dsl(source)
    html = render_candidate_html(source)
    return {"pipeline_version": "1.0", "source_text": text, "first_stage": first,
            "classification": classification, "dsl": source,
            "validated_candidate": candidate, "html": html}


def _bundle_payloads(result):
    """Validate structure and cross-stage consistency before creating any files."""
    try:
        if result["pipeline_version"] != "1.0":
            raise ValueError("Unsupported pipeline version")
        first = result["first_stage"]
        text = result["source_text"]
        if not isinstance(text, str):
            raise ValueError("Workflow source text must be a string")
        validate_result(first, text)
        classification = classify_skills(first["normalized_skills"])
        source = result["dsl"]
        candidate = parse_candidate_dsl(source)
        html = render_candidate_html(source)
        if (classification != result["classification"]
                or source != generate_candidate_dsl(first, classification)
                or candidate != result["validated_candidate"] or html != result["html"]):
            raise ValueError("Bundle outputs are inconsistent with the candidate DSL and recognition")
        return {"first_stage.json": json.dumps(first, ensure_ascii=False, indent=2) + "\n",
                "classification.json": json.dumps(classification, ensure_ascii=False, indent=2) + "\n",
                "candidate.rl": source, "candidate.html": html}
    except (KeyError, TypeError, ValidationError) as error:
        raise ValueError("Invalid workflow result structure") from error


def _check_bundle_targets(destination, force):
    for filename in BUNDLE_FILES:
        target = destination / filename
        if target.is_symlink():
            raise ValueError("Bundle output files must not be symbolic links")
        if target.exists() and not target.is_file():
            raise IsADirectoryError("Bundle output path is not a regular file: " + str(target))
        if target.exists() and not force:
            raise FileExistsError("A bundle file already exists; choose another directory or use --force")


def _write_payload(path, payload):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_recovery_state(workspace, originals, phase):
    state = {"version": 1, "phase": phase, "bundle_files": list(BUNDLE_FILES),
             "originals": originals}
    pending = workspace / "recovery.next.json"
    _write_payload(pending, json.dumps(state, indent=2) + "\n")
    _replace_file(pending, workspace / "recovery.json")


def _restore_targets(destination, workspace, originals, touched):
    errors = []
    for filename in reversed(touched):
        try:
            target = destination / filename
            if filename in originals:
                # Keep every original backup until the entire recovery succeeds.
                restored = workspace / "prepared" / (filename + ".restore")
                shutil.copy2(workspace / "previous" / filename, restored)
                _replace_file(restored, target)
            else:
                target.unlink(missing_ok=True)
        except OSError as error:
            errors.append((filename, error))
    return errors


def _remove_workspace(workspace):
    def remove_read_only(function, path, error_info):
        # Windows cannot delete a read-only backup; only private copies change.
        if isinstance(error_info[1], PermissionError) and Path(path).is_file():
            Path(path).chmod(stat.S_IREAD | stat.S_IWRITE)
            function(path)
        else:
            raise error_info[1]
    shutil.rmtree(workspace, onerror=remove_read_only)


def save_bundle(result, destination, force=False):
    """Prepare all outputs/backups, then replace; recover on controlled failures.

    The exclusive workspace coordinates cooperating writers. A failed recovery
    keeps the original copies and reports their location. This is not a durable
    multi-file filesystem transaction: abrupt termination requires inspection.
    """
    payloads = _bundle_payloads(result)
    destination = Path(destination)
    _check_bundle_targets(destination, force)
    destination.mkdir(parents=True, exist_ok=True)
    workspace = destination / BUNDLE_WORKSPACE
    try:
        workspace.mkdir(mode=0o700)
    except FileExistsError as error:
        raise FileExistsError("An export or recovery workspace already exists at "
                              + str(workspace) + "; inspect it before retrying") from error
    retain_workspace = False
    try:
        # Repeat the preflight after acquiring exclusive ownership.
        _check_bundle_targets(destination, force)
        originals = [name for name in BUNDLE_FILES if (destination / name).exists()]
        (workspace / "prepared").mkdir()
        (workspace / "previous").mkdir()
        for filename in BUNDLE_FILES:
            _write_payload(workspace / "prepared" / filename, payloads[filename])
        for filename in originals:
            backup = workspace / "previous" / filename
            shutil.copy2(destination / filename, backup)
            shutil.copymode(backup, workspace / "prepared" / filename)
        _write_recovery_state(workspace, originals, "prepared")
        touched = []
        try:
            # Exclusive placeholders protect previously absent names, including
            # against a non-overwriting export collision after its preflight.
            for filename in BUNDLE_FILES:
                if filename not in originals:
                    with (destination / filename).open("xb"):
                        touched.append(filename)
            _check_bundle_targets(destination, True)
            for filename in BUNDLE_FILES:
                if filename not in touched:
                    touched.append(filename)
                _replace_file(workspace / "prepared" / filename, destination / filename)
            _write_recovery_state(workspace, originals, "committed")
        except BaseException as error:
            retain_workspace = True
            failures = _restore_targets(destination, workspace, originals, touched)
            if failures:
                raise BundleRecoveryError(workspace, failures) from error
            retain_workspace = False
            raise
    finally:
        if not retain_workspace:
            try:
                _remove_workspace(workspace)
            except OSError as error:
                warnings.warn(f"Export cleanup failed at {workspace}: {error}. "
                              "Inspect the recovery files before retrying.",
                              RuntimeWarning, stacklevel=2)
    return destination
