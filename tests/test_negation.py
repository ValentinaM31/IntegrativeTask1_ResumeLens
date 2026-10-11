"""Regression cases for explicit negation through extraction and public workflows."""
import base64
from http.client import HTTPConnection
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from zipfile import ZipFile

from resumelens import process_resume, process_complete_resume, parse_candidate_dsl
from resumelens.first_stage import validate_result
from resumelens.web import create_server


class NegationExtractionTests(unittest.TestCase):
    def check_case(self, text, skills, excluded):
        result = process_resume(text, name="Ana")
        self.assertEqual(sorted(skills), result["normalized_skills"])
        self.assertEqual(excluded, [item["raw"] for item in result["excluded_mentions"]])
        for item in result["excluded_mentions"]:
            self.assertEqual("Explicit simple negation", item["reason"])
        for item in result["extracted_skills"] + result["excluded_mentions"]:
            self.assertEqual(item["raw"], text[item["start"]:item["end"]])
        validate_result(result, text)
        return result

    def test_english_knowledge_and_use_negations(self):
        for phrase in ("I do not know", "do not know", "I don't know", "don't know",
                       "I don’t know", "don’t know", "I do not use", "I don't use",
                       "I don’t use", "I\tdo\tnot\tknow", "I\tdon’t\tuse", "I cannot use",
                       "I can not use", "I can't use", "I can’t use"):
            for heading in ("", "Technical Skills: "):
                with self.subTest(phrase=phrase, heading=heading):
                    self.check_case(heading + phrase + " React", [], ["React"])

    def test_spanish_knowledge_negations(self):
        for phrase in ("No sé", "No se", "No conozco", "Yo no conozco", "NO SÉ", "No\tsé"):
            with self.subTest(phrase=phrase):
                self.check_case("Habilidades: " + phrase + " Python ni Git; Java",
                                ["JAVA"], ["Python", "Git"])

    def test_known_alias_lists_and_oxford_comma(self):
        for separator in (", ", " / ", " and ", " or ", " nor ", " y ", " o ", " ni ",
                          ", and ", ", or ", ", nor "):
            with self.subTest(separator=separator):
                self.check_case("Skills: I do not know React" + separator + "Angular" +
                                separator + "Vue; Python, Git", ["GIT", "PYTHON"],
                                ["React", "Angular", "Vue"])

    def test_clause_and_line_boundaries_keep_positive_skills(self):
        for separator in (". ", "! ", "? ", "; ", "\n", "\r\n", ", but ",
                          ", however ", ", pero ", ", aunque ", ", sin embargo "):
            with self.subTest(separator=separator):
                self.check_case("Skills: I do not know Python" + separator + "Git",
                                ["GIT"], ["Python"])

    def test_nonlist_words_stop_negation_scope(self):
        self.check_case("Skills: I do not know React, I use Python and Git",
                        ["GIT", "PYTHON"], ["React"])
        self.check_case("Skills: I do not know React, but I use Angular",
                        ["ANGULAR"], ["React"])
        self.check_case("I do not know React, but I use Angular", ["ANGULAR"], ["React"])

    def test_positive_react_knowledge_or_usage(self):
        for phrase in ("I know", "I use", "know", "use", "Yo sé", "Sé", "Conozco",
                       "Yo uso", "Uso", "I\tknow"):
            with self.subTest(phrase=phrase):
                self.check_case(phrase + " React", ["REACT"], [])

    def test_ordinary_react_verb_is_still_excluded(self):
        for text in ("I react quickly to changes.", "I know how to react to changes.",
                     "I use exercises to react quickly."):
            with self.subTest(text=text):
                result = process_resume(text, name="Ana")
                self.assertEqual([], result["normalized_skills"])
                self.assertEqual(["React without supported technical context"],
                                 [item["reason"] for item in result["excluded_mentions"]])

    def test_positive_repetition_survives_an_earlier_negation(self):
        result = self.check_case("Skills: I don't know React or Python. I know React; Python",
                                 ["PYTHON", "REACT"], ["React", "Python"])
        self.assertEqual(["React", "Python"], [item["raw"] for item in result["extracted_skills"]])
        self.assertEqual([0, 1], [item["extracted_index"] for item in result["normalization_evidence"]])

    def test_unicode_and_crlf_offsets_are_unchanged(self):
        text = "Name: José\r\nSkills: I don’t know rEaCt, Angular, or Vue; Python, Git\r\n"
        result = self.check_case(text, ["GIT", "PYTHON"], ["rEaCt", "Angular", "Vue"])
        self.assertEqual("José", result["candidate"]["name"])
        for raw, item in zip(("rEaCt", "Angular", "Vue"), result["excluded_mentions"]):
            self.assertEqual(text.index(raw), item["start"])
            self.assertEqual(text.index(raw) + len(raw), item["end"])

    def test_longest_aliases_and_internal_dots_in_negative_lists(self):
        self.check_case("Skills: I do not know React.js, Node.js or PostgreSQL; Python",
                        ["PYTHON"], ["React.js", "Node.js", "PostgreSQL"])

    def test_pandas_context_is_preserved(self):
        result = process_resume("I don’t use Pandas for data analysis. "
                                "I use Pandas for data analysis. I like pandas at the zoo.", name="Ana")
        self.assertEqual(["PANDAS"], result["normalized_skills"])
        self.assertEqual(["Explicit simple negation", "Pandas without supported technical context"],
                         [item["reason"] for item in result["excluded_mentions"]])
        validate_result(result, "I don’t use Pandas for data analysis. "
                        "I use Pandas for data analysis. I like pandas at the zoo.")


class NegationWorkflowTests(unittest.TestCase):
    TEXT = "Name: Ana\r\nTechnical Skills: JS, NodeJS, Postgres, Git; I do not know React\r\n"

    def test_full_stack_false_acceptance_and_positive_recovery(self):
        for suffix, expected in (("", []), ("I know React\r\n", ["FULL_STACK_DEVELOPER"]),
                                 ("I use Angular\r\n", ["FULL_STACK_DEVELOPER"])):
            with self.subTest(suffix=suffix):
                result = process_complete_resume(self.TEXT + suffix)
                self.assertEqual(expected, result["classification"]["accepted_profiles"])
                self.assertEqual(result["validated_candidate"], parse_candidate_dsl(result["dsl"]))
                self.assertEqual(self.TEXT + suffix, result["source_text"])
                self.assertEqual("Explicit simple negation",
                                 result["first_stage"]["excluded_mentions"][0]["reason"])

    def test_bom_crlf_file_matches_api_and_both_clis(self):
        result = process_complete_resume(self.TEXT)
        with tempfile.TemporaryDirectory(prefix="resumelens-negation-") as folder:
            root = Path(folder)
            source = root / "resume.txt"
            source.write_bytes(b"\xef\xbb\xbf" + self.TEXT.encode("utf-8"))
            commands = (("resumelens", root / "first.json"),
                        ("resumelens.workflow_cli", root / "bundle"))
            for module, output in commands:
                completed = subprocess.run([sys.executable, "-m", module, str(source), "-o", str(output)],
                                           cwd=folder, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual(result["first_stage"], json.loads((root / "first.json").read_text(encoding="utf-8")))
            bundle = root / "bundle"
            for filename, field in (("first_stage.json", "first_stage"),
                                    ("classification.json", "classification")):
                self.assertEqual(result[field], json.loads((bundle / filename).read_text(encoding="utf-8")))
            self.assertEqual(result["dsl"], (bundle / "candidate.rl").read_text(encoding="utf-8"))
            self.assertEqual(result["html"], (bundle / "candidate.html").read_text(encoding="utf-8"))

    def test_real_http_response_and_zip_reflect_the_corrected_decision(self):
        server = create_server(0)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        try:
            connection.request("POST", "/api/process",
                               json.dumps({"text": "\ufeff" + self.TEXT}).encode("utf-8"),
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            self.assertEqual(200, response.status)
            body = json.loads(response.read())
            self.assertEqual([], body["result"]["classification"]["accepted_profiles"])
            self.assertNotIn("REACT", body["result"]["first_stage"]["normalized_skills"])
            with ZipFile(BytesIO(base64.b64decode(body["bundle_zip"]))) as bundle:
                self.assertEqual(sorted(body["downloads"]), sorted(bundle.namelist()))
                for filename, content in body["downloads"].items():
                    self.assertEqual(content, bundle.read(filename).decode("utf-8"))
                classification = json.loads(bundle.read("classification.json"))
                self.assertEqual([], classification["accepted_profiles"])
                candidate = parse_candidate_dsl(bundle.read("candidate.rl").decode("utf-8"))
                self.assertEqual(body["result"]["validated_candidate"], candidate)
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
