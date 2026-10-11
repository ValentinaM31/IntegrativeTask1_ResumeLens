"""Explain requirements without changing the actual profile automaton decisions."""
import base64
import copy
from http.client import HTTPConnection
from html.parser import HTMLParser
from io import BytesIO
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from resumelens import classify_skills, process_complete_resume, save_bundle
from resumelens.classification import build_profile_automaton, load_profiles
from resumelens.web import create_server


def profile_row(skills, profile="BACKEND_DEVELOPER"):
    return next(row for row in classify_skills(skills)["profiles"] if row["profile"] == profile)


class VisibleText(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.values = []
        self.feed(source)

    def handle_data(self, value):
        self.values.append(value)


class ProfileExplanationTests(unittest.TestCase):
    BASE = ["SQL", "REST_API", "GIT"]

    def test_incompatible_language_framework_and_each_repair_option(self):
        row = profile_row(self.BASE + ["JAVA", "DJANGO"])
        self.assertFalse(row["accepted"])
        self.assertTrue(row["compatible_pair_missing"])
        self.assertEqual([], row["missing_groups"])
        diagnostics = row["pair_diagnostics"]
        self.assertEqual("incompatible", diagnostics["status"])
        self.assertEqual(["JAVA"], diagnostics["languages_present"])
        self.assertEqual(["DJANGO"], diagnostics["frameworks_present"])
        self.assertEqual(["SPRING_BOOT"], diagnostics["alternatives"][0]["missing"])
        self.assertEqual(["PYTHON"], diagnostics["alternatives"][1]["missing"])
        self.assertEqual(["JAVASCRIPT", "NODE_JS"], diagnostics["alternatives"][2]["missing"])
        self.assertEqual(["TYPESCRIPT", "NODE_JS"], diagnostics["alternatives"][3]["missing"])
        self.assertEqual(["Languages found: Java. Frameworks found: Django. "
                          "These do not form an admitted language/framework pair."], row["explanations"])
        self.assertEqual("Java + Spring Boot: missing Spring Boot.", diagnostics["alternatives"][0]["message"])
        self.assertEqual("Python + Django: missing Python.", diagnostics["alternatives"][1]["message"])

    def test_missing_framework_is_distinct_from_incompatibility(self):
        row = profile_row(self.BASE + ["JAVA"])
        self.assertEqual("missing_framework", row["pair_diagnostics"]["status"])
        self.assertEqual(["No supported backend framework is present. Languages found: Java."],
                         row["explanations"])

    def test_missing_language_is_distinct_from_incompatibility(self):
        row = profile_row(self.BASE + ["DJANGO"])
        self.assertEqual("missing_language", row["pair_diagnostics"]["status"])
        self.assertEqual(["No supported backend language is present. Frameworks found: Django."],
                         row["explanations"])

    def test_missing_both_and_empty_skills_describe_every_requirement(self):
        row = profile_row([])
        self.assertEqual("missing_both", row["pair_diagnostics"]["status"])
        self.assertEqual(["No supported backend language or framework is present.",
                          "Missing one of: SQL or PostgreSQL or MySQL or MongoDB.",
                          "Missing required qualification: REST API.",
                          "Missing required qualification: Git."], row["explanations"])
        for item in classify_skills([])["profiles"]:
            self.assertFalse(item["accepted"])
            self.assertTrue(item["explanations"])

    def test_valid_pair_does_not_hide_missing_other_groups(self):
        row = profile_row(["PYTHON", "DJANGO", "REST_API", "GIT"])
        self.assertFalse(row["accepted"])
        self.assertFalse(row["compatible_pair_missing"])
        self.assertEqual("matched", row["pair_diagnostics"]["status"])
        self.assertEqual([["SQL", "POSTGRESQL", "MYSQL", "MONGODB"]], row["missing_groups"])
        self.assertEqual(["Missing one of: SQL or PostgreSQL or MySQL or MongoDB."], row["explanations"])

    def test_multiple_valid_pairs_are_reported_without_requiring_all_alternatives(self):
        row = profile_row(self.BASE + ["JAVA", "SPRING_BOOT", "PYTHON", "DJANGO"])
        self.assertTrue(row["accepted"])
        self.assertEqual("matched", row["pair_diagnostics"]["status"])
        self.assertEqual(["All required qualification groups are present.",
                          "Compatible pair found: Java + Spring Boot; Python + Django."], row["explanations"])
        self.assertEqual([[], [], ["JAVASCRIPT", "NODE_JS"], ["TYPESCRIPT", "NODE_JS"]],
                         [option["missing"] for option in row["pair_diagnostics"]["alternatives"]])

    def test_full_stack_missing_group_is_described(self):
        row = profile_row(["JAVASCRIPT", "NODE_JS", "SQL", "GIT"], "FULL_STACK_DEVELOPER")
        self.assertIsNone(row["pair_diagnostics"])
        self.assertEqual([["REACT", "ANGULAR", "VUE"]], row["missing_groups"])
        self.assertEqual(["Missing one of: React or Angular or Vue."], row["explanations"])

    def test_ml_optional_library_does_not_fill_required_engine(self):
        row = profile_row(["PYTHON", "NUMPY", "SCIKIT_LEARN", "SQL", "GIT"], "MACHINE_LEARNING_ENGINEER")
        self.assertFalse(row["accepted"])
        self.assertEqual(["SCIKIT_LEARN"], row["optional_present"])
        self.assertEqual(["Missing one of: TensorFlow or PyTorch."], row["explanations"])

    def test_data_engineer_missing_pipeline_group_is_described(self):
        row = profile_row(["PYTHON", "SQL", "GIT"], "DATA_ENGINEER")
        self.assertFalse(row["accepted"])
        self.assertEqual(["Missing one of: ETL or Apache Airflow or Apache Spark."], row["explanations"])

    def test_backend_decisions_for_pairs_and_remaining_requirement_combinations(self):
        valid = {("JAVA", "SPRING_BOOT"), ("PYTHON", "DJANGO"),
                 ("JAVASCRIPT", "NODE_JS"), ("TYPESCRIPT", "NODE_JS")}
        for language, framework, mask in itertools.product(
                ("JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT"), ("SPRING_BOOT", "DJANGO", "NODE_JS"), range(8)):
            with self.subTest(language=language, framework=framework, mask=mask):
                extras = [symbol for index, symbol in enumerate(self.BASE) if mask & (1 << index)]
                row = profile_row([language, framework] + extras)
                self.assertEqual((language, framework) in valid and mask == 7, row["accepted"])
                self.assertEqual((language, framework) not in valid, row["compatible_pair_missing"])
                self.assertEqual("matched" if (language, framework) in valid else "incompatible",
                                 row["pair_diagnostics"]["status"])

    def test_diagnostics_use_the_configured_pairs(self):
        profile = copy.deepcopy(load_profiles()[2])
        profile["required_pair_alternatives"] = [["PYTHON", "DJANGO"]]
        machine = build_profile_automaton(profile)
        with patch("resumelens.classification._models", return_value={profile["id"]: (profile, machine)}):
            row = profile_row(self.BASE + ["JAVA", "DJANGO"])
        self.assertEqual("missing_language", row["pair_diagnostics"]["status"])
        self.assertEqual([["PYTHON", "DJANGO"]],
                         [option["pair"] for option in row["pair_diagnostics"]["alternatives"]])

    def test_automaton_remains_the_acceptance_authority(self):
        with patch("pyformlang.finite_automaton.EpsilonNFA.accepts", return_value=False) as accepts:
            row = profile_row(["JAVASCRIPT", "REACT", "NODE_JS", "SQL", "GIT"], "FULL_STACK_DEVELOPER")
        self.assertEqual(4, accepts.call_count)
        self.assertFalse(row["accepted"])
        self.assertEqual([], row["missing_groups"])
        self.assertEqual(["The profile automaton rejected the qualification sequence."], row["explanations"])

    def test_result_order_and_mutations_do_not_change_later_diagnostics(self):
        skills = self.BASE + ["JAVA", "DJANGO", "DOCKER"]
        expected = classify_skills(skills)
        self.assertEqual(expected, classify_skills(list(reversed(skills)) + skills))
        changed = classify_skills(skills)
        backend = next(row for row in changed["profiles"] if row["profile"] == "BACKEND_DEVELOPER")
        backend["explanations"].clear()
        backend["pair_diagnostics"]["alternatives"][0]["pair"].clear()
        backend["pair_diagnostics"]["alternatives"][0]["missing"].clear()
        self.assertEqual(expected, classify_skills(skills))


class ExplanationIntegrationTests(unittest.TestCase):
    TEXT = "Name: Ana\r\nSkills: Java, Django, SQL, REST API, Git\r\n"

    def test_validated_standalone_report_contains_the_same_explanations(self):
        result = process_complete_resume(self.TEXT)
        visible = VisibleText(result["html"]).values
        self.assertIn("Qualification checks", visible)
        for row in result["classification"]["profiles"]:
            for message in row["explanations"]:
                self.assertIn(message, visible)
            if row["compatible_pair_missing"]:
                for option in row["pair_diagnostics"]["alternatives"]:
                    self.assertIn(option["message"], visible)

    def test_changed_explanations_block_export_before_writing(self):
        result = process_complete_resume(self.TEXT)
        result["classification"]["profiles"][2]["explanations"] = ["All requirements met."]
        with tempfile.TemporaryDirectory(prefix="resumelens-explanations-") as folder:
            destination = Path(folder) / "bundle"
            with self.assertRaises(ValueError):
                save_bundle(result, destination)
            self.assertFalse(destination.exists())

    def test_workflow_cli_preserves_diagnostics_and_all_four_outputs(self):
        expected = process_complete_resume(self.TEXT)
        with tempfile.TemporaryDirectory(prefix="resumelens-explanations-") as folder:
            root = Path(folder)
            source = root / "resume.txt"
            source.write_bytes(b"\xef\xbb\xbf" + self.TEXT.encode("utf-8"))
            destination = root / "bundle"
            completed = subprocess.run([sys.executable, "-m", "resumelens.workflow_cli", str(source),
                                        "-o", str(destination)], cwd=folder, capture_output=True,
                                       text=True, encoding="utf-8")
            self.assertEqual(0, completed.returncode, completed.stderr)
            for filename, field in (("classification.json", "classification"), ("first_stage.json", "first_stage")):
                self.assertEqual(expected[field], json.loads((destination / filename).read_text(encoding="utf-8")))
            for filename, field in (("candidate.rl", "dsl"), ("candidate.html", "html")):
                self.assertEqual(expected[field], (destination / filename).read_text(encoding="utf-8"))

    def test_actual_http_and_zip_deliver_the_same_rejection_and_repair_details(self):
        server = create_server(0)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        try:
            connection.request("POST", "/api/process", json.dumps({"text": self.TEXT}).encode("utf-8"),
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            self.assertEqual(200, response.status)
            body = json.loads(response.read())
            with ZipFile(BytesIO(base64.b64decode(body["bundle_zip"]))) as bundle:
                for filename, content in body["downloads"].items():
                    self.assertEqual(content, bundle.read(filename).decode("utf-8"))
                classification = json.loads(bundle.read("classification.json"))
                backend = next(row for row in classification["profiles"] if row["profile"] == "BACKEND_DEVELOPER")
                self.assertFalse(backend["accepted"])
                self.assertEqual("incompatible", backend["pair_diagnostics"]["status"])
                visible = VisibleText(bundle.read("candidate.html").decode("utf-8")).values
                self.assertIn(backend["explanations"][0], visible)
                self.assertIn("Java + Spring Boot: missing Spring Boot.", visible)
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
