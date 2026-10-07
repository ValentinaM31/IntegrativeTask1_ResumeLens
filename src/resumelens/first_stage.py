"""Public entry point for text processing."""
import json
from functools import lru_cache
from importlib.resources import files
from jsonschema import Draft202012Validator
from .extraction import extract_resume
from .normalization import build_transducers, normalize_skills


@lru_cache(maxsize=1)
def _transducers():
    return build_transducers()


def validate_result(result, text):
    schema = json.loads(files("resumelens").joinpath("first_stage.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(result)
    groups = [result["extracted_skills"], result["excluded_mentions"], result["unknown_skills"]]
    groups.extend(value for key, value in result["candidate"].items() if key != "name")
    for group in groups:
        for item in group:
            if not 0 <= item["start"] < item["end"] <= len(text) or text[item["start"]:item["end"]] != item["raw"]:
                raise ValueError("Evidence inconsistent with the original text")
    links = result["normalization_evidence"]
    indices = [link["extracted_index"] for link in links]
    if len(set(indices)) != len(indices) or any(i >= len(result["extracted_skills"]) for i in indices):
        raise ValueError("Invalid normalization indices")
    if result["normalized_skills"] != sorted({link["canonical"] for link in links}):
        raise ValueError("Inconsistent canonical list")
    actual = normalize_skills(result["extracted_skills"], _transducers())
    if any(result[key] != actual[key] for key in actual):
        raise ValueError("Links inconsistent with the actual FST translation")


def process_resume(text, name=None):
    extracted = extract_resume(text, name)
    result = {"schema_version": "1.0", **extracted,
              **normalize_skills(extracted["extracted_skills"], _transducers())}
    validate_result(result, text)
    return result
