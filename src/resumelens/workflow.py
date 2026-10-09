"""Compose all four stages while preserving the first-stage JSON 1.0 contract."""
import json
from importlib.resources import files
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from .first_stage import process_resume
from .classification import classify_skills
from .dsl import generate_candidate_dsl, parse_candidate_dsl
from .rendering import render_candidate_html

BUNDLE_FILES = ("first_stage.json", "classification.json", "candidate.rl", "candidate.html")


def process_complete_resume(text, name=None):
    """Return fresh outputs after extraction, FSTs, recognition and DSL validation."""
    first = process_resume(text, name)
    classification = classify_skills(first["normalized_skills"])
    source = generate_candidate_dsl(first, classification)
    candidate = parse_candidate_dsl(source)
    html = render_candidate_html(source)
    return {"pipeline_version": "1.0", "first_stage": first,
            "classification": classification, "dsl": source,
            "validated_candidate": candidate, "html": html}


def _bundle_payloads(result):
    """Validate structure and cross-stage consistency before creating any files."""
    try:
        if result["pipeline_version"] != "1.0":
            raise ValueError("Unsupported pipeline version")
        first = result["first_stage"]
        schema = json.loads(files("resumelens").joinpath("first_stage.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(first)
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


def save_bundle(result, destination, force=False):
    """Save four UTF-8 files after validation and a complete overwrite preflight.

    Unrelated files are retained. The four writes are not a filesystem transaction;
    an operating-system error during writing can leave a partial bundle.
    """
    payloads = _bundle_payloads(result)
    destination = Path(destination)
    targets = [destination / filename for filename in BUNDLE_FILES]
    for target in targets:
        if target.is_symlink():
            raise ValueError("Bundle output files must not be symbolic links")
        if target.exists() and not target.is_file():
            raise IsADirectoryError("Bundle output path is not a regular file: " + str(target))
        if target.exists() and not force:
            raise FileExistsError("A bundle file already exists; choose another directory or use --force")
    destination.mkdir(parents=True, exist_ok=True)
    for filename, payload in payloads.items():
        with (destination / filename).open("w" if force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
    return destination
