import copy
import io
import json
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
import subprocess
import sys
import shutil
import uuid
import unittest
from unittest.mock import patch
from jsonschema.exceptions import ValidationError
from pyformlang.fst import FST

from resumelens import process_resume
from resumelens.catalog import load_catalog
from resumelens.cli import main
from resumelens.extraction import extract_resume
from resumelens.first_stage import validate_result
from resumelens.normalization import build_transducers, normalize_skills

ROOT = Path(__file__).resolve().parents[1]
TEST_TMP = ROOT / "tmp" / "tests"
TEST_TMP.mkdir(parents=True, exist_ok=True)


@contextmanager
def test_directory():
    # Regular mkdir inherits project permissions, including in the Windows sandbox.
    directory = TEST_TMP / uuid.uuid4().hex
    directory.mkdir()
    try:
        yield directory
    finally:
        if directory.resolve().parent != TEST_TMP.resolve():
            raise ValueError("Temporary path outside the test directory")
        shutil.rmtree(directory)


class ExtractionTests(unittest.TestCase):
    def test_english_resume_end_to_end(self):
        text = ("Name: Ana Example\r\nEmail: ana@example.com\r\n"
                "Phone: +57 300-123-4567\r\nhttps://linkedin.com/in/ana\r\n"
                "Education: Bachelor in Computer Science\r\n"
                "Experience: 3 years of experience processing data.\r\n"
                "Skills: Python, Pandas, Git.\r\n"
                "No experience with TensorFlow.\r\nI like pandas at the zoo.")
        result = process_resume(text)
        self.assertEqual(result["candidate"]["name"], "Ana Example")
        for field in ("emails", "phones", "links", "education", "experience"):
            self.assertEqual(len(result["candidate"][field]), 1, field)
        self.assertEqual(result["normalized_skills"], ["GIT", "PANDAS", "PYTHON"])
        self.assertEqual([item["reason"] for item in result["excluded_mentions"]],
                         ["Explicit simple negation", "Pandas without supported technical context"])
        self.assertEqual(result["warnings"], [])
        validate_result(result, text)
        self.assertEqual(process_resume("Skills: Python")["warnings"],
                         ["Name not found; use Name: or --name"])

    def test_multiple_candidate_records_and_unicode_offsets(self):
        text = "Nombre: José\r\nEmail: uno@example.com dos@example.org\r\nTeléfono: +57 300-123-4567 y 3112223333\r\nhttps://github.com/jose https://linkedin.com/in/jose\r\nEducación: Ingeniería de Sistemas\r\nDegree: Master in Data Science\r\nExperiencia: 3 años de experiencia en datos.\r\nExperience: 1 year of experience.\r\n"
        result = process_resume(text)
        self.assertEqual(result["candidate"]["name"], "José")
        for category in ("emails", "phones", "links", "education", "experience"):
            self.assertEqual(len(result["candidate"][category]), 2, category)
        validate_result(result, text)

    def test_absent_name_and_fallback(self):
        self.assertIsNone(process_resume("Arbitrary heading")["candidate"]["name"])
        self.assertEqual(process_resume("Arbitrary heading", "Ana")["candidate"]["name"], "Ana")
        self.assertEqual(process_resume("Name: Alex", "Ana")["candidate"]["name"], "Alex")
        self.assertEqual(process_resume("Name:   \nSkills: Python", "Ana")["candidate"]["name"], "Ana")

    def test_boundaries_literal_dots_and_urls(self):
        text = "Skills: JavaScript, GitHub, ReactXjs, NodeXjs, PySpark, Git.\nhttps://github.com/Python/Java\ncorreo Python@example.com"
        self.assertEqual(process_resume(text)["normalized_skills"], ["GIT", "JAVASCRIPT"])

    def test_longest_alias_and_repetitions(self):
        result = process_resume("Skills: Java SE, REST APIs, Git SCM, JS, JavaScript, JS")
        self.assertEqual([e["raw"] for e in result["extracted_skills"]], ["Java SE", "REST APIs", "Git SCM", "JS", "JavaScript", "JS"])
        self.assertEqual(result["normalized_skills"], ["GIT", "JAVA", "JAVASCRIPT", "REST_API"])
        self.assertEqual(len(result["normalization_evidence"]), 6)

    def test_ambiguous_inline_section_and_prose(self):
        text = "The JS name and TS meeting.\nTechnical Skills:\nJS, TS\n\nExperience: TS is a code name"
        result = process_resume(text)
        self.assertEqual(result["normalized_skills"], ["JAVASCRIPT", "TYPESCRIPT"])
        self.assertEqual(len(result["excluded_mentions"]), 3)

    def test_bullet_continuation(self):
        self.assertEqual(process_resume("Habilidades:\n- JS\n- TS\nExperience: JS")['normalized_skills'], ["JAVASCRIPT", "TYPESCRIPT"])

    def test_negations_and_positive_recovery(self):
        text = "No experience with Python\nsin experiencia en TensorFlow\nno knowledge of Java\nsin conocimientos de Git\nSkills: Python, Git"
        result = process_resume(text)
        self.assertEqual(result["normalized_skills"], ["GIT", "PYTHON"])
        self.assertEqual(len(result["excluded_mentions"]), 4)

    def test_unmarked_academic_and_experience_phrases(self):
        result = process_resume("Bachelor in Computer Science.\n3 years of experience building apps.")
        self.assertEqual(len(result["candidate"]["education"]), 1)
        self.assertEqual(len(result["candidate"]["experience"]), 1)

    def test_non_phone_years_and_non_mobile(self):
        result = process_resume("Years: 2020-2026; 1234567890; abc3001234567; 30012345678")
        self.assertEqual(result["candidate"]["phones"], [])

    def test_empty_input(self):
        for text in ("", " \n\t", None):
            with self.subTest(text=text), self.assertRaises(ValueError):
                process_resume(text)

    def test_multiline_academic_and_work_sections(self):
        text = "Education\n- Bachelor of Science, Example University, 2022\n- Master of Science, Data University, 2024\nWork Experience:\n- Backend Developer, Example Ltd, 2023-2025\n- Data Engineer, Sample Ltd, 2025-2026\nSkills\nJS, TS\nProjects:\nOther project"
        result = process_resume(text)
        self.assertEqual(len(result["candidate"]["education"]), 2)
        self.assertEqual(len(result["candidate"]["experience"]), 2)
        self.assertEqual(result["candidate"]["experience"][0]["raw"], "Backend Developer, Example Ltd, 2023-2025")
        self.assertEqual(result["normalized_skills"], ["JAVASCRIPT", "TYPESCRIPT"])
        validate_result(result, text)

    def test_academic_homonyms_are_not_degrees(self):
        self.assertEqual(process_resume("Scrum Master. I master Python.")["candidate"]["education"], [])
        self.assertEqual(process_resume("Master of Science.")["candidate"]["education"][0]["raw"], "Master of Science")

    def test_negated_known_lists_and_clause_boundary(self):
        result = process_resume("no experience with Python, Java or Git. Skills: Docker\nSkills: Python")
        self.assertEqual(result["normalized_skills"], ["DOCKER", "PYTHON"])
        self.assertEqual(len(result["excluded_mentions"]), 3)
        result = process_resume("sin experiencia en React, Angular y Vue; conocimientos de Python")
        self.assertEqual(result["normalized_skills"], ["PYTHON"])

    def test_prose_with_comma_does_not_extend_skills_context(self):
        result = process_resume("Skills:\nI discussed JS, but TS is a meeting code")
        self.assertEqual(result["normalized_skills"], [])
        self.assertEqual(len(result["excluded_mentions"]), 2)

    def test_malformed_email_and_foreign_phone(self):
        result = process_resume("Email: a..b@example.com bad@-example.com\nPhone: +1 3001234567")
        self.assertEqual(result["candidate"]["emails"], [])
        self.assertEqual(result["candidate"]["phones"], [])
        self.assertEqual(process_resume("Write to ana@example.com.")["candidate"]["emails"][0]["raw"], "ana@example.com")

    def test_react_requires_explicit_technical_context(self):
        for text in ("Skills: React", "Technical Skills:\nReact, Git",
                     "Developed web applications using react", "Desarrollé interfaces con React",
                     "React framework", "A ReactJS component", "A React.js component"):
            with self.subTest(text=text):
                self.assertIn("REACT", process_resume(text)["normalized_skills"])
        for text in ("I react quickly to changes", "We REACT to feedback"):
            with self.subTest(text=text):
                result = process_resume(text)
                self.assertNotIn("REACT", result["normalized_skills"])
                self.assertEqual(result["excluded_mentions"][0]["reason"], "React without supported technical context")
                validate_result(result, text)

    def test_pandas_technical_context_and_animals(self):
        positive = ("Skills: Pandas", "Technical Skills:\nPython, pandas, NumPy",
                    "Uso pandas para procesar datos.", "I use pandas for data analysis.",
                    "Utilizo Pandas para análisis de datos.")
        for text in positive:
            with self.subTest(text=text):
                result = process_resume(text)
                self.assertIn("PANDAS", result["normalized_skills"])
                validate_result(result, text)
        for text in ("Los pandas viven en China.", "I like pandas at the zoo.", "I like PANDAS at the zoo."):
            with self.subTest(text=text):
                result = process_resume(text)
                self.assertEqual(result["normalized_skills"], [])
                self.assertEqual(result["excluded_mentions"][0]["reason"], "Pandas without supported technical context")
                validate_result(result, text)

    def test_pandas_and_other_positive_skills_survive_negation(self):
        text = "Skills: Python, Pandas, Git.\nNo tengo experiencia en TensorFlow."
        result = process_resume(text)
        self.assertEqual(result["normalized_skills"], ["GIT", "PANDAS", "PYTHON"])
        self.assertEqual([m["raw"] for m in result["excluded_mentions"]], ["TensorFlow"])
        self.assertEqual(result["excluded_mentions"][0]["reason"], "Explicit simple negation")

    def test_extended_negation_phrases(self):
        phrases = ("no experience with", "sin experiencia en", "no knowledge of",
                   "sin conocimientos de", "I do not use", "I don't use",
                   "No tengo experiencia en", "No tengo experiencia con", "No uso")
        for phrase in phrases:
            text = phrase + " Python anymore"
            with self.subTest(phrase=phrase):
                result = process_resume(text)
                self.assertEqual(result["normalized_skills"], [])
                self.assertEqual(result["excluded_mentions"][0]["raw"], "Python")
                self.assertEqual(result["excluded_mentions"][0]["reason"], "Explicit simple negation")

    def test_contrast_preserves_positive_mentions(self):
        cases = {"No tengo experiencia en Python, pero sí en Java": ["JAVA"],
                 "I do not use Python anymore, but I use Git": ["GIT"],
                 "No experience with Python, TensorFlow or PyTorch. Skills: Git": ["GIT"],
                 "I use Git; no experience with Python": ["GIT"],
                 "No uso Python. Trabajo con React": ["REACT"]}
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(process_resume(text)["normalized_skills"], expected)

    def test_js_ts_context_and_embedded_skills_word(self):
        for text in ("Skills: JS, TS", "Technical Skills:\nJS, TS", "Habilidades\n- JS\n- TS"):
            self.assertEqual(process_resume(text)["normalized_skills"], ["JAVASCRIPT", "TYPESCRIPT"])
        self.assertEqual(process_resume("We discuss skills and JS, TS are meeting codes")["normalized_skills"], [])

    def test_original_pdf_fragments_with_manual_name(self):
        text = "Wednesday Addams\n3 years of experience developing web applications.\nTechnical Skills : JS, React.js, NodeJS, Postgres, Git."
        result = process_resume(text, name="Wednesday Addams")
        self.assertEqual(result["candidate"]["name"], "Wednesday Addams")
        self.assertEqual(result["normalized_skills"], ["GIT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "REACT"])
        text = "Mary Jane Watson\n2 years of experience developing predictive models and data-processing pipelines.\nTechnical Skills: Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."
        result = process_resume(text, name="Mary Jane Watson")
        self.assertEqual(result["candidate"]["name"], "Mary Jane Watson")
        self.assertEqual(result["normalized_skills"], ["GIT", "ML_MODEL", "NUMPY", "PANDAS", "PYTHON", "SCIKIT_LEARN", "SQL", "TENSORFLOW"])
        validate_result(result, text)


class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.machines = build_transducers(cls.catalog)

    def test_every_alias_and_case_variant(self):
        for skill in self.catalog["skills"]:
            for alias in skill["aliases"]:
                for raw in (alias, alias.upper(), alias.swapcase()):
                    with self.subTest(alias=raw):
                        result = process_resume("Skills: " + raw)
                        self.assertEqual(result["normalized_skills"], [skill["canonical"]])
                        self.assertEqual(result["extracted_skills"][0]["raw"], raw)
                        self.assertEqual(list(self.machines[skill["category"]].translate(list(raw.casefold()))), [[skill["canonical"]]])

    def test_unknown_and_full_consumption(self):
        for raw in ("Rust", "JSx", "J", "React.js extra", ""):
            result = normalize_skills([{"raw": raw, "start": 0, "end": len(raw)}], self.machines)
            self.assertEqual(result["normalized_skills"], [])
            self.assertEqual(result["unknown_skills"][0]["raw"], raw)

    def test_catalog_conflict(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["skills"][1]["aliases"].append("js")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            build_transducers(catalog)

    def test_multiple_canonical_outputs_are_rejected(self):
        first, second = FST(), FST()
        for machine, symbol in ((first, "PYTHON"), (second, "JAVA")):
            machine.add_start_state("q0")
            machine.add_transition("q0", "x", "q1", [symbol])
            machine.add_final_state("q1")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            normalize_skills([{"raw": "x", "start": 0, "end": 1}], {"one": first, "two": second})

    def test_machine_sizes_and_single_token_output(self):
        expected = {"languages": (78, 77, 11), "frameworks_libraries": (166, 165, 22),
                    "databases": (67, 66, 7), "tools_qualifications": (207, 206, 16)}
        for category, machine in self.machines.items():
            self.assertEqual((len(machine.states), machine.get_number_transitions(), len(machine.final_states)), expected[category])
        self.assertIn("JAVASCRIPT", self.machines["languages"].output_symbols)
        self.assertNotIn("J", self.machines["languages"].output_symbols)

    def test_incompatible_schema_version_is_rejected(self):
        text = "Skills: Python"
        result = process_resume(text)
        result["schema_version"] = "2.0"
        with self.assertRaises(ValidationError):
            validate_result(result, text)

    def test_transducers_are_cached_across_process_calls(self):
        from resumelens.first_stage import _transducers
        _transducers.cache_clear()
        with patch("resumelens.first_stage.build_transducers", wraps=build_transducers) as builder:
            process_resume("Skills: Python, Git")
            process_resume("Skills: Java")
            self.assertEqual(builder.call_count, 1)

    def test_order_does_not_change_canonical_symbols(self):
        a = process_resume("Skills: JS, React.js, NodeJS, Postgres, Git")
        b = process_resume("Skills: Git, Postgres, NodeJS, React.js, JS")
        self.assertEqual(a["normalized_skills"], b["normalized_skills"])
        self.assertNotEqual(a["extracted_skills"], b["extracted_skills"])

    def test_all_eight_samples_and_reference_contract(self):
        expectations = json.loads((ROOT / "data/expected_samples.json").read_text(encoding="utf-8"))
        for case in expectations["cases"]:
            with self.subTest(file=case["file"]):
                text = (ROOT / case["file"]).read_text(encoding="utf-8")
                result = process_resume(text)
                self.assertEqual(result["normalized_skills"], case["normalized_skills"])
                self.assertNotIn("accepted_profiles", result)
        self.assertEqual(process_resume((ROOT / "contracts/example_input.txt").read_text(encoding="utf-8")), json.loads((ROOT / "contracts/example_output.json").read_text(encoding="utf-8")))

    def test_semantic_validator_detects_corruption(self):
        text = "Skills: Python, Git"
        result = process_resume(text)
        for mutation in ("offset", "index", "translation", "symbols"):
            changed = copy.deepcopy(result)
            if mutation == "offset":
                changed["extracted_skills"][0]["end"] += 1
            elif mutation == "index":
                changed["normalization_evidence"][0]["extracted_index"] = 999
            elif mutation == "translation":
                changed["normalization_evidence"][0]["canonical"] = "JAVA"
                changed["normalized_skills"] = ["GIT", "JAVA"]
            else:
                changed["normalized_skills"] = ["PYTHON", "GIT"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_result(changed, text)

    def test_packaged_resources_match_editable_sources(self):
        self.assertEqual(self.catalog, json.loads((ROOT / "config/skills_catalog.json").read_text(encoding="utf-8")))
        self.assertEqual((ROOT / "src/resumelens/first_stage.schema.json").read_bytes(), (ROOT / "contracts/first_stage.schema.json").read_bytes())
        for category, machine in self.machines.items():
            model = json.loads((ROOT / f"docs/models/{category}.json").read_text(encoding="utf-8"))
            transitions = sorted((s, c, t, list(out)) for (s, c), edges in machine.transitions.items() for t, out in edges)
            self.assertEqual(model["Q"], sorted(machine.states))
            self.assertEqual(model["Sigma"], sorted(machine.input_symbols))
            self.assertEqual(model["Gamma"], sorted(machine.output_symbols))
            self.assertEqual(model["q0"], "q0")
            self.assertEqual(model["F"], sorted(machine.final_states))
            self.assertEqual(model["delta"], [[s, c, t] for s, c, t, _ in transitions])
            self.assertEqual(model["omega"], [{"transition": [s, c, t], "output": out} for s, c, t, out in transitions])


class CliTests(unittest.TestCase):
    def run_cli(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_cli_bom_crlf_nested_output_and_overwrite(self):
        with test_directory() as directory:
            root = Path(directory)
            source, output = root / "resume.txt", root / "nested/out.json"
            source.write_bytes(b"\xef\xbb\xbfName: Alex\r\nSkills: Python\r\n")
            args = [str(source), "-o", str(output)]
            self.assertEqual(self.run_cli(args)[0], 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            validate_result(result, "Name: Alex\r\nSkills: Python\r\n")
            original = output.read_bytes()
            self.assertEqual(self.run_cli(args)[0], 2)
            self.assertEqual(output.read_bytes(), original)
            self.assertEqual(self.run_cli(args + ["--force"])[0], 0)

    def test_cli_invalid_inputs(self):
        with test_directory() as directory:
            root = Path(directory)
            for filename, contents in (("empty.txt", b""), ("invalid.txt", b"\xff"), ("resume.pdf", b"Skills: Python")):
                source = root / filename
                source.write_bytes(contents)
                output = root / (filename + ".json")
                code, _, error = self.run_cli([str(source), "-o", str(output)])
                self.assertEqual(code, 2)
                self.assertTrue(error.startswith("Error:"))
                self.assertFalse(output.exists())
            self.assertEqual(self.run_cli([str(root / "missing.txt"), "-o", str(root / "out.json")])[0], 2)

    def test_cli_protects_input(self):
        with test_directory() as directory:
            source = Path(directory) / "resume.txt"
            source.write_text("Skills: Python", encoding="utf-8")
            self.assertEqual(self.run_cli([str(source), "-o", str(source), "--force"])[0], 2)
            self.assertEqual(source.read_text(), "Skills: Python")

    def test_module_entry_point(self):
        result = subprocess.run([sys.executable, "-m", "resumelens", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--output", result.stdout)

    def test_pandas_api_cli_equivalence_with_manual_name(self):
        with test_directory() as directory:
            source, output = directory / "resume.txt", directory / "nested/result.json"
            source.write_bytes(b"\xef\xbb\xbfSkills: Python, Pandas, Git.\r\nNo tengo experiencia en TensorFlow.\r\nLos pandas viven en China.\r\n")
            self.assertEqual(self.run_cli([str(source), "-o", str(output), "--name", "Ana"])[0], 0)
            with source.open(encoding="utf-8-sig", newline="") as stream:
                text = stream.read()
            actual = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(actual, process_resume(text, name="Ana"))
            self.assertEqual(actual["normalized_skills"], ["GIT", "PANDAS", "PYTHON"])
            self.assertEqual(len(actual["excluded_mentions"]), 2)


if __name__ == "__main__":
    unittest.main()
