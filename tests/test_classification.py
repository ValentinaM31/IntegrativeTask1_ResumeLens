"""Profile recognition tests independent of later DSL and UI stages."""
import itertools
import copy
import json
from pathlib import Path
import unittest
from resumelens import process_resume
from resumelens.classification import (build_profile_automaton, canonical_sequence,
                                      classify_skills, load_profiles, profile_branches, validate_profile)

ROOT = Path(__file__).resolve().parents[1]


class RecognitionTests(unittest.TestCase):
    def accepted(self, skills):
        return classify_skills(skills)["accepted_profiles"]

    def test_existing_sample_expectations(self):
        cases = json.loads((ROOT / "data/expected_samples.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["file"]):
                text = (ROOT / case["file"]).read_text(encoding="utf-8")
                result = {"first_stage": process_resume(text)}
                result["classification"] = classify_skills(result["first_stage"]["normalized_skills"])
                self.assertEqual(result["first_stage"], process_resume(text))
                self.assertEqual(result["classification"]["accepted_profiles"], sorted(case["accepted_profiles_expected_later"]))

    def test_full_stack_all_alternatives_and_missing_groups(self):
        groups = [("JAVASCRIPT", "TYPESCRIPT"), ("REACT", "ANGULAR", "VUE"),
                  ("NODE_JS", "DJANGO", "SPRING_BOOT"), ("SQL", "POSTGRESQL", "MYSQL", "MONGODB"), ("GIT",)]
        for combination in itertools.product(*groups):
            self.assertIn("FULL_STACK_DEVELOPER", self.accepted(combination))
            for missing in range(len(combination)):
                self.assertNotIn("FULL_STACK_DEVELOPER", self.accepted(combination[:missing] + combination[missing + 1:]))

    def test_ml_alternatives_and_no_inferred_sql(self):
        for library, engine, database in itertools.product(("PANDAS", "NUMPY"), ("TENSORFLOW", "PYTORCH"), ("SQL", "POSTGRESQL", "MYSQL")):
            skills = ["PYTHON", library, engine, database, "GIT"]
            self.assertIn("MACHINE_LEARNING_ENGINEER", self.accepted(skills))
            for symbol in skills:
                self.assertNotIn("MACHINE_LEARNING_ENGINEER", self.accepted(set(skills) - {symbol}))
        self.assertNotIn("MACHINE_LEARNING_ENGINEER", self.accepted(["PYTHON", "PANDAS", "PYTORCH", "MONGODB", "GIT"]))

    def test_backend_compatible_and_incompatible_pairs(self):
        pairs = {("JAVA", "SPRING_BOOT"), ("PYTHON", "DJANGO"), ("JAVASCRIPT", "NODE_JS"), ("TYPESCRIPT", "NODE_JS")}
        for language, framework in itertools.product(("JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT"), ("SPRING_BOOT", "DJANGO", "NODE_JS")):
            skills = [language, framework, "SQL", "REST_API", "GIT"]
            self.assertEqual("BACKEND_DEVELOPER" in self.accepted(skills), (language, framework) in pairs)
        self.assertIn("BACKEND_DEVELOPER", self.accepted(["JAVA", "PYTHON", "DJANGO", "NODE_JS", "MYSQL", "REST_API", "GIT"]))
        for missing in ("REST_API", "GIT", "MYSQL"):
            self.assertNotIn("BACKEND_DEVELOPER", self.accepted({"JAVA", "SPRING_BOOT", "MYSQL", "REST_API", "GIT"} - {missing}))

    def test_data_engineer_alternatives_and_missing_groups(self):
        for database, tool in itertools.product(("SQL", "POSTGRESQL", "MYSQL"), ("ETL", "AIRFLOW", "APACHE_SPARK")):
            skills = ["PYTHON", database, tool, "GIT"]
            self.assertIn("DATA_ENGINEER", self.accepted(skills))
            for missing in skills:
                self.assertNotIn("DATA_ENGINEER", self.accepted(set(skills) - {missing}))

    def test_order_repetition_optional_and_other_skills(self):
        base = ["GIT", "REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL"]
        for permutation in itertools.permutations(base):
            self.assertEqual(self.accepted(permutation), ["FULL_STACK_DEVELOPER"])
        self.assertEqual(self.accepted(base + base + ["DOCKER", "NUMPY", "REST_API"]), ["BACKEND_DEVELOPER", "FULL_STACK_DEVELOPER"])
        self.assertEqual(self.accepted([]), [])
        with self.assertRaises(ValueError):
            self.accepted(["RUST"])
        with self.assertRaises(ValueError):
            self.accepted("PYTHON")

    def test_actual_machine_rejects_bad_order_and_missing_bucket(self):
        profile = load_profiles()[0]
        machine = build_profile_automaton(profile)
        sequence = canonical_sequence(["GIT", "REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL"], profile)
        self.assertTrue(machine.accepts(sequence))
        self.assertFalse(machine.accepts(list(reversed(sequence))))
        self.assertFalse(machine.accepts(sequence[:-1]))
        self.assertFalse(machine.accepts([]))

    def test_packaged_profile_configuration(self):
        self.assertEqual(load_profiles(), json.loads((ROOT / "config/profiles_design.json").read_text(encoding="utf-8")))
        for profile in load_profiles():
            buckets = [allowed for allowed, _ in profile_branches(profile)[0]]
            self.assertEqual(sum(map(len, buckets)), len(set.union(*buckets)))

    def test_invalid_configuration_is_rejected(self):
        original = load_profiles()[0]
        for change in ([], [["RUST"]], [["GIT"], ["GIT"]]):
            profile = copy.deepcopy(original)
            profile["required_groups"] = change
            with self.assertRaises(ValueError):
                validate_profile(profile)
        profile = copy.deepcopy(load_profiles()[2])
        profile["required_pair_alternatives"] = [["JAVA"]]
        with self.assertRaises(ValueError):
            validate_profile(profile)
        profile = copy.deepcopy(original)
        profile["optional"] = ["GIT"]
        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_canonical_order_retains_all_pair_candidates(self):
        profile = load_profiles()[2]
        skills = ["PYTHON", "JAVA", "NODE_JS", "DJANGO", "SQL", "REST_API", "GIT", "DOCKER"]
        self.assertEqual(canonical_sequence(skills, profile),
                         ["JAVA", "PYTHON", "DJANGO", "NODE_JS", "SQL", "REST_API", "GIT"])
        self.assertTrue(build_profile_automaton(profile).accepts(canonical_sequence(skills, profile)))

    def test_invalid_skill_collection(self):
        for skills in (None, [123], [["PYTHON"]]):
            with self.assertRaises(ValueError):
                classify_skills(skills)

    def test_generated_models_and_classifications_match_execution(self):
        from pyformlang.finite_automaton import Epsilon, EpsilonNFA
        for profile in load_profiles():
            model = json.loads((ROOT / "docs/automata" / (profile["id"] + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(model["epsilon_label"], "ε")
            actual = build_profile_automaton(profile)
            self.assertEqual(model["Q"], sorted(state.value for state in actual.states))
            self.assertEqual(model["Sigma"], sorted(symbol.value for symbol in actual.symbols))
            self.assertNotIn("ε", model["Sigma"])
            restored = EpsilonNFA()
            restored.add_start_state(model["q0"])
            for state in model["F"]:
                restored.add_final_state(state)
            for source, symbol, target in model["delta"]:
                restored.add_transition(source, Epsilon() if symbol == "ε" else symbol, target)
            self.assertEqual(actual.to_dict(), restored.to_dict())
        cases = json.loads((ROOT / "data/expected_samples.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            path = ROOT / case["file"]
            first = process_resume(path.read_text(encoding="utf-8"))
            expected = classify_skills(first["normalized_skills"])
            persisted = json.loads((ROOT / "data/classification" / (path.stem + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(persisted, expected)


if __name__ == "__main__":
    unittest.main()
