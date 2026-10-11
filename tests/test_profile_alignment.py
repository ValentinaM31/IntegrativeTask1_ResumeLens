"""Execute the assignment's ML alternatives through actual models and adapters."""
import base64
from http.client import HTTPConnection
from io import BytesIO
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from zipfile import ZipFile

from resumelens import (classify_skills, parse_candidate_dsl,
                       process_complete_resume, process_resume)
from resumelens.classification import build_profile_automaton, canonical_sequence, load_profiles
from resumelens.web import create_server
from resumelens.workflow import BUNDLE_FILES, _bundle_payloads

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "profile-alignment"
ML = "MACHINE_LEARNING_ENGINEER"
LIBRARIES = ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"]


def ml_row(skills):
    return next(row for row in classify_skills(skills)["profiles"] if row["profile"] == ML)


class ProfileAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = next(profile for profile in load_profiles() if profile["id"] == ML)
        cls.machine = build_profile_automaton(cls.profile)
        cls.cases = json.loads((FIXTURES / "cases.json").read_text(encoding="utf-8"))["cases"]

    def test_diagram_library_alternatives_and_reference_databases(self):
        # Page 5: PYTHON (PANDAS|NUMPY) (SCIKIT|TF|TORCH) (SQL|PG) GIT.
        for data, library, database in itertools.product(
                ("PANDAS", "NUMPY"), LIBRARIES, ("SQL", "POSTGRESQL")):
            with self.subTest(data=data, library=library, database=database):
                sequence = ["PYTHON", data, library, database, "GIT"]
                self.assertTrue(self.machine.accepts(sequence))
                row = ml_row(sequence)
                self.assertTrue(row["accepted"])
                self.assertEqual(row["sequence"], sequence)
                self.assertEqual(row["missing_groups"], [])
                self.assertNotIn(library, row["optional_present"])

    def test_actual_machine_requires_each_bucket_in_order(self):
        sequence = ["PYTHON", "PANDAS", "SCIKIT_LEARN", "POSTGRESQL", "GIT"]
        self.assertTrue(self.machine.accepts(sequence))
        self.assertFalse(self.machine.accepts(sequence[::-1]))
        self.assertFalse(self.machine.accepts([]))
        for index in range(len(sequence)):
            with self.subTest(missing=sequence[index]):
                short = sequence[:index] + sequence[index + 1:]
                self.assertFalse(self.machine.accepts(short))
                self.assertFalse(ml_row(short)["accepted"])

    def test_all_learning_libraries_are_retained_in_canonical_order(self):
        skills = ["GIT", "TENSORFLOW", "SCIKIT_LEARN", "PYTORCH", "SQL", "NUMPY", "PYTHON"]
        expected = ["PYTHON", "NUMPY", "PYTORCH", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]
        self.assertEqual(canonical_sequence(skills + skills, self.profile), expected)
        self.assertTrue(self.machine.accepts(expected))
        self.assertEqual(ml_row(skills)["sequence"], expected)

    def test_scikit_aliases_roundtrip_with_simultaneous_profiles(self):
        for alias in ("Scikit-learn", "sklearn", "scikit learn"):
            with self.subTest(alias=alias):
                text = (f"Name: Ana\nSkills: Python, NumPy, {alias}, SQL, Git, "
                        "Django, REST API, ETL.")
                result = process_complete_resume(text)
                self.assertEqual(result["first_stage"], process_resume(text))
                self.assertEqual(result["classification"]["accepted_profiles"],
                                 ["BACKEND_DEVELOPER", "DATA_ENGINEER", ML])
                self.assertEqual(parse_candidate_dsl(result["dsl"]), result["validated_candidate"])
                self.assertIn("profile MACHINE_LEARNING_ENGINEER;", result["dsl"])
                self.assertIn("<li>MACHINE LEARNING ENGINEER</li>", result["html"])
                evidence = next(item for item in result["first_stage"]["extracted_skills"]
                                if item["raw"] == alias)
                self.assertEqual(text[evidence["start"]:evidence["end"]], alias)

    def test_optional_models_or_negated_libraries_do_not_fill_the_group(self):
        for text, optional in (
                ("Name: Ana\nSkills: Python, NumPy, machine learning models, Docker, SQL, Git.",
                 ["DOCKER", "ML_MODEL"]),
                ("Name: Ana\nSkills: Python, NumPy, SQL, Git.\nI do not know sklearn.", []),
                ("Name: Ana\nSkills: Python, NumPy, SQL, Git.\nNo uso Scikit-learn.", [])):
            with self.subTest(text=text):
                result = process_complete_resume(text)
                row = next(item for item in result["classification"]["profiles"] if item["profile"] == ML)
                self.assertFalse(row["accepted"])
                self.assertEqual(row["optional_present"], optional)
                self.assertEqual(row["missing_groups"], [LIBRARIES])
                self.assertEqual(row["explanations"],
                                 ["Missing one of: Scikit-learn or TensorFlow or PyTorch."])
                self.assertNotIn("SCIKIT_LEARN", result["first_stage"]["normalized_skills"])

    def test_fixture_bundles_and_dsl_claims_match_the_new_rule(self):
        for case in self.cases:
            with self.subTest(case=case["file"]):
                source = FIXTURES / case["file"]
                result = process_complete_resume(source.read_text(encoding="utf-8"))
                self.assertEqual(result["first_stage"]["normalized_skills"], case["normalized_skills"])
                self.assertEqual(result["classification"]["accepted_profiles"], case["accepted_profiles"])
                for name, payload in _bundle_payloads(result).items():
                    self.assertEqual((FIXTURES / source.stem / name).read_text(encoding="utf-8"), payload)
                if case["accepted_profiles"]:
                    corrupt = result["dsl"].replace("    profile MACHINE_LEARNING_ENGINEER;\n", "")
                else:
                    corrupt = result["dsl"].replace("  accepted_profiles {\n",
                                                    "  accepted_profiles {\n    profile MACHINE_LEARNING_ENGINEER;\n")
                with self.assertRaises(ValueError):
                    parse_candidate_dsl(corrupt)

    def test_real_cli_matches_the_api_with_bom_lf_and_crlf(self):
        for case, newline in itertools.product(self.cases, ("\n", "\r\n")):
            with self.subTest(case=case["file"], newline=repr(newline)), tempfile.TemporaryDirectory() as folder:
                text = (FIXTURES / case["file"]).read_text(encoding="utf-8").replace("\n", newline)
                source = Path(folder) / "resume.txt"
                source.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
                destination = Path(folder) / "reports"
                done = subprocess.run([sys.executable, "-m", "resumelens.workflow_cli",
                                       str(source), "-o", str(destination)], cwd=folder,
                                      capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(done.returncode, 0, done.stderr)
                expected = process_complete_resume(text)
                self.assertEqual(expected["classification"]["accepted_profiles"], case["accepted_profiles"])
                for name, payload in _bundle_payloads(expected).items():
                    self.assertEqual((destination / name).read_bytes(), payload.encode("utf-8"))

    def test_actual_http_and_zip_match_both_profile_outcomes(self):
        server = create_server(0)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for case in self.cases:
                with self.subTest(case=case["file"]):
                    text = (FIXTURES / case["file"]).read_text(encoding="utf-8")
                    expected = process_complete_resume(text)
                    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
                    try:
                        connection.request("POST", "/api/process", json.dumps({"text": text}).encode("utf-8"),
                                           {"Content-Type": "application/json"})
                        response = connection.getresponse()
                        self.assertEqual(response.status, 200)
                        body = json.loads(response.read())
                    finally:
                        connection.close()
                    self.assertEqual(body["result"], expected)
                    self.assertEqual(expected["classification"]["accepted_profiles"], case["accepted_profiles"])
                    payloads = _bundle_payloads(expected)
                    with ZipFile(BytesIO(base64.b64decode(body["bundle_zip"], validate=True))) as archive:
                        self.assertEqual(set(archive.namelist()), set(BUNDLE_FILES))
                        for name, payload in payloads.items():
                            self.assertEqual(body["downloads"][name], payload)
                            self.assertEqual(archive.read(name), payload.encode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
