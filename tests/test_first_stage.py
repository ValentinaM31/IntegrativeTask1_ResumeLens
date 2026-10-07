import copy
import unittest
from pyformlang.fst import FST
from resumelens.normalization import build_transducers, normalize_skills
from resumelens.catalog import load_catalog, validate_catalog
from resumelens.extraction import extract_resume

class CandidateTests(unittest.TestCase):
    def test_name_and_absence(self):
        self.assertEqual(extract_resume("Nombre: José")["candidate"]["name"], "José")
        self.assertIsNone(extract_resume("Heading")["candidate"]["name"])
        self.assertEqual(extract_resume("Heading", "Ana")["candidate"]["name"], "Ana")

    def test_contact_and_offsets(self):
        text = "Correo: ana@example.com dos@example.org\r\nPhone: +57 300-123-4567\r\nhttps://github.com/ana"
        candidate = extract_resume(text)["candidate"]
        self.assertEqual(len(candidate["emails"]), 2)
        self.assertEqual(len(candidate["phones"]), 1)
        self.assertEqual(len(candidate["links"]), 1)
        for key in ("emails", "phones", "links"):
            for item in candidate[key]:
                self.assertEqual(text[item["start"]:item["end"]], item["raw"])

    def test_sections_and_homonyms(self):
        text = "Education\n- Bachelor of Science, Example University\n- Master of Science, Data University\nExperience:\n- Developer, Example Ltd, 2023-2025\nSkills: Python"
        candidate = extract_resume(text)["candidate"]
        self.assertEqual(len(candidate["education"]), 2)
        self.assertEqual(len(candidate["experience"]), 1)
        self.assertEqual(extract_resume("Scrum Master. I master Python.")["candidate"]["education"], [])

    def test_empty_and_invalid_contact(self):
        with self.assertRaises(ValueError):
            extract_resume("  ")
        candidate = extract_resume("Email: a..b@example.com\nPhone: +1 3001234567")["candidate"]
        self.assertEqual(candidate["emails"], [])
        self.assertEqual(candidate["phones"], [])


class SkillTests(unittest.TestCase):
    def assert_evidence(self, result, text):
        for group in (result["extracted_skills"], result["excluded_mentions"]):
            for item in group:
                self.assertEqual(text[item["start"]:item["end"]], item["raw"])

    def test_every_alias_and_case_preserves_evidence(self):
        catalog = load_catalog()
        self.assertEqual(len(catalog["skills"]), 26)
        self.assertEqual(sum(len(skill["aliases"]) for skill in catalog["skills"]), 56)
        for skill in catalog["skills"]:
            for alias in skill["aliases"]:
                for variant in (alias, alias.upper(), alias.lower()):
                    with self.subTest(alias=variant):
                        text = "Skills: " + variant
                        result = extract_resume(text)
                        self.assertEqual([item["raw"] for item in result["extracted_skills"]], [variant])
                        self.assertEqual(result["excluded_mentions"], [])
                        self.assert_evidence(result, text)

    def test_boundaries_literal_dots_and_contacts(self):
        text = ("Skills: JavaScript, GitHub, ReactXjs, NodeXjs, React.js, Node.js, Git.\n"
                "https://example.com/Python\nPython@example.com")
        result = extract_resume(text)
        self.assertEqual([item["raw"] for item in result["extracted_skills"]],
                         ["JavaScript", "React.js", "Node.js", "Git"])
        self.assertEqual([item["reason"] for item in result["excluded_mentions"]],
                         ["Mention inside a URL", "Mention inside an email address"])
        self.assert_evidence(result, text)

    def test_repetitions_are_not_removed(self):
        text = "Skills: JS, JavaScript, JS"
        result = extract_resume(text)
        self.assertEqual([item["raw"] for item in result["extracted_skills"]],
                         ["JS", "JavaScript", "JS"])
        self.assertEqual(len({item["start"] for item in result["extracted_skills"]}), 3)
        self.assert_evidence(result, text)

    def test_js_ts_require_actual_skills_context(self):
        for text in ("Skills: JS, TS", "Technical Skills:\nJS, TS", "Skills\n- JS\n- TS"):
            result = extract_resume(text)
            self.assertEqual([item["raw"] for item in result["extracted_skills"]], ["JS", "TS"])
            self.assert_evidence(result, text)
        for text in ("We discuss skills and JS, TS are meeting codes",
                     "Skills:\nI discussed JS, but TS is a meeting code"):
            result = extract_resume(text)
            self.assertEqual(result["extracted_skills"], [])
            self.assertEqual(len(result["excluded_mentions"]), 2)
            self.assert_evidence(result, text)

    def test_react_framework_and_verb(self):
        for text in ("Skills: React", "Technical Skills:\nReact, Git",
                     "Developed interfaces using react", "React framework", "A React.js component"):
            result = extract_resume(text)
            self.assertTrue(any(item["raw"].casefold().startswith("react")
                                for item in result["extracted_skills"]))
            self.assert_evidence(result, text)
        for text in ("I react quickly to changes", "We REACT to feedback"):
            result = extract_resume(text)
            self.assertEqual(result["extracted_skills"], [])
            self.assertEqual(result["excluded_mentions"][0]["reason"],
                             "React without supported technical context")
            self.assert_evidence(result, text)

    def test_pandas_technical_usage_and_animals(self):
        for text in ("Skills: Pandas", "Technical Skills:\nPython, pandas, NumPy",
                     "I use pandas for data analysis.", "Uso pandas para procesar datos."):
            result = extract_resume(text)
            self.assertTrue(any(item["raw"].casefold() == "pandas"
                                for item in result["extracted_skills"]))
            self.assert_evidence(result, text)
        for text in ("I like pandas at the zoo.", "Los pandas viven en China.",
                     "I like PANDAS at the zoo."):
            result = extract_resume(text)
            self.assertEqual(result["extracted_skills"], [])
            self.assertEqual(result["excluded_mentions"][0]["reason"],
                             "Pandas without supported technical context")
            self.assert_evidence(result, text)

    def test_negation_retains_previous_positive_skills(self):
        text = "Skills: Python, Pandas, Git.\r\nNo tengo experiencia en TensorFlow."
        result = extract_resume(text)
        self.assertEqual([item["raw"] for item in result["extracted_skills"]], ["Python", "Pandas", "Git"])
        self.assertEqual([item["raw"] for item in result["excluded_mentions"]], ["TensorFlow"])
        self.assert_evidence(result, text)

    def test_all_supported_negative_phrases(self):
        phrases = ("no experience with", "sin experiencia en", "no knowledge of",
                   "sin conocimientos de", "I do not use", "I don't use",
                   "No tengo experiencia en", "No tengo experiencia con", "No uso")
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                text = phrase + " Python. Skills: Git"
                result = extract_resume(text)
                self.assertEqual([item["raw"] for item in result["extracted_skills"]], ["Git"])
                self.assertEqual(result["excluded_mentions"][0]["reason"], "Explicit simple negation")
                self.assert_evidence(result, text)

    def test_negative_lists_and_contrast(self):
        cases = {
            "No experience with Python, TensorFlow or PyTorch. Skills: Git": ["Git"],
            "I do not use Python anymore, but I use Git": ["Git"],
            "No tengo experiencia en Python, pero sí en Java": ["Java"],
            "I use Git; no experience with Python": ["Git"],
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                result = extract_resume(text)
                self.assertEqual([item["raw"] for item in result["extracted_skills"]], expected)
                self.assert_evidence(result, text)

    def test_catalog_resources_and_conflicts(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        catalog = load_catalog()
        self.assertEqual(catalog, json.loads((root/"config/skills_catalog.json").read_text(encoding="utf-8")))
        broken = copy.deepcopy(catalog)
        broken["skills"][1]["aliases"].append("js")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            validate_catalog(broken)


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
                        text = "Skills: " + raw
                        extracted = extract_resume(text)
                        result = normalize_skills(extracted["extracted_skills"], self.machines)
                        self.assertEqual(result["normalized_skills"], [skill["canonical"]])
                        self.assertEqual(extracted["extracted_skills"][0]["raw"], raw)
                        self.assertEqual(result["normalization_evidence"],
                                         [{"extracted_index": 0, "canonical": skill["canonical"]}])
                        self.assertEqual(list(self.machines[skill["category"]].translate(list(raw.casefold()))),
                                         [[skill["canonical"]]])

    def test_unknown_and_full_consumption(self):
        for raw in ("Rust", "JSx", "J", "React.js extra", ""):
            with self.subTest(raw=raw):
                evidence = {"raw": raw, "start": 0, "end": len(raw)}
                result = normalize_skills([evidence], self.machines)
                self.assertEqual(result["normalized_skills"], [])
                self.assertEqual(result["normalization_evidence"], [])
                self.assertEqual(result["unknown_skills"], [evidence])

    def test_catalog_conflict_is_rejected_before_building(self):
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

    def test_machine_sizes_and_complete_output_symbols(self):
        expected = {"languages": (78, 77, 11), "frameworks_libraries": (166, 165, 22),
                    "databases": (67, 66, 7), "tools_qualifications": (207, 206, 16)}
        for category, machine in self.machines.items():
            self.assertEqual((len(machine.states), machine.get_number_transitions(), len(machine.final_states)),
                             expected[category])
        self.assertIn("JAVASCRIPT", self.machines["languages"].output_symbols)
        self.assertNotIn("J", self.machines["languages"].output_symbols)

    def test_repeated_mentions_keep_links_and_original_evidence(self):
        text = "Skills: JS, JavaScript, JS, Git SCM"
        extracted = extract_resume(text)
        mentions = extracted["extracted_skills"]
        before = copy.deepcopy(mentions)
        result = normalize_skills(mentions, self.machines)
        self.assertEqual(mentions, before)
        self.assertEqual(result["normalized_skills"], ["GIT", "JAVASCRIPT"])
        self.assertEqual(result["normalization_evidence"],
                         [{"extracted_index": 0, "canonical": "JAVASCRIPT"},
                          {"extracted_index": 1, "canonical": "JAVASCRIPT"},
                          {"extracted_index": 2, "canonical": "JAVASCRIPT"},
                          {"extracted_index": 3, "canonical": "GIT"}])
        for item in mentions:
            self.assertEqual(text[item["start"]:item["end"]], item["raw"])

    def test_order_changes_evidence_not_canonical_symbols(self):
        a = extract_resume("Skills: JS, React.js, NodeJS, Postgres, Git")["extracted_skills"]
        b = extract_resume("Skills: Git, Postgres, NodeJS, React.js, JS")["extracted_skills"]
        self.assertEqual(normalize_skills(a, self.machines)["normalized_skills"],
                         normalize_skills(b, self.machines)["normalized_skills"])
        self.assertNotEqual(a, b)
