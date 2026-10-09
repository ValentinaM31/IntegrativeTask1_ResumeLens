"""Candidate-language behavior independently of future HTML and UI components."""
import copy
from importlib.resources import files
import json
from pathlib import Path
import unittest
from textx import TextXSyntaxError
from resumelens import process_resume, classify_skills, generate_candidate_dsl, parse_candidate_dsl
from resumelens.catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


class CandidateLanguageTests(unittest.TestCase):
    def setUp(self):
        self.first = process_resume('Name: Ana\nEmail: a@example.com\nSkills: Python, Pandas, TensorFlow, SQL, Git.\nEducation:\nBSc Computing\nMSc AI\nExperience:\nJob one\nJob two')
        self.classification = classify_skills(self.first["normalized_skills"])
        self.source = generate_candidate_dsl(self.first, self.classification)

    def test_round_trip_and_repeated_records(self):
        candidate = parse_candidate_dsl(self.source)
        self.assertEqual(candidate["name"], "Ana")
        self.assertEqual(candidate["accepted_profiles"], ["MACHINE_LEARNING_ENGINEER"])
        self.assertEqual(candidate["education"], ["BSc Computing", "MSc AI"])
        self.assertEqual(candidate["experience"], ["Job one", "Job two"])
        self.assertEqual(candidate["contacts"], [{"kind": "email", "value": "a@example.com"}])
        self.assertEqual(candidate["skills"], self.first["normalized_skills"])

    def test_multiple_contacts(self):
        first = process_resume('Name: A\nEmail: a@example.com, b@example.com\nPhone: +57 300 000 0001\nGitHub: https://github.com/example')
        candidate = parse_candidate_dsl(generate_candidate_dsl(first, classify_skills([])))
        self.assertEqual(candidate["contacts"], [
            {"kind": "email", "value": "a@example.com"}, {"kind": "email", "value": "b@example.com"},
            {"kind": "phone", "value": "+57 300 000 0001"}, {"kind": "link", "value": "https://github.com/example"}])

    def test_empty_sections_and_missing_name(self):
        first = process_resume('A resume without known qualifications.')
        candidate = parse_candidate_dsl(generate_candidate_dsl(first, classify_skills([])))
        self.assertEqual(candidate, {"name": None, "contacts": [], "education": [], "experience": [],
                                     "skills": [], "accepted_profiles": []})

    def test_null_word_is_distinct_from_missing_name(self):
        first = process_resume('Name: null')
        candidate = parse_candidate_dsl(generate_candidate_dsl(first, classify_skills([])))
        self.assertEqual(candidate["name"], "null")

    def test_unicode_quotes_and_backslashes(self):
        first = process_resume('Name: Ana María "AI"\nEducation: Carrère "AI" \\ path\nExperience: Línea α')
        candidate = parse_candidate_dsl(generate_candidate_dsl(first, classify_skills([])))
        self.assertEqual(candidate["name"], 'Ana María "AI"')
        self.assertEqual(candidate["education"], ['Carrère "AI" \\ path'])
        self.assertEqual(candidate["experience"], ['Línea α'])

    def test_json_escapes_and_control_characters(self):
        source = 'candidate { name "Ana\\nMaría\\t\\u03b1"; contacts {} education {} experience {} skills {} accepted_profiles {} }'
        self.assertEqual(parse_candidate_dsl(source)["name"], 'Ana\nMaría\tα')
        with self.assertRaises(TextXSyntaxError):
            parse_candidate_dsl(source.replace('Ana\\n', 'Ana\n'))

    def test_missing_braces_fields_and_wrong_order(self):
        for source in (self.source[:-2], self.source.replace('name "Ana";', ''),
                       self.source.replace('contacts {', 'contact {'),
                       self.source.replace('education {', 'experience {'), self.source + 'trailing'):
            with self.subTest(source=source):
                with self.assertRaises(TextXSyntaxError):
                    parse_candidate_dsl(source)

    def test_unknown_case_and_keyword_boundaries(self):
        for value in ('Python', 'RUST', 'PYTHON_EXTRA', 'PYTHON3'):
            with self.subTest(value=value):
                with self.assertRaises(TextXSyntaxError):
                    parse_candidate_dsl(self.source.replace('skill PYTHON;', 'skill ' + value + ';'))
        with self.assertRaises(TextXSyntaxError):
            parse_candidate_dsl(self.source.replace('candidate {', 'candidate_extra {'))

    def test_unquoted_strings_bad_escapes_and_unknown_profiles(self):
        malformed = [self.source.replace('name "Ana";', 'name Ana;'),
                     self.source.replace('name "Ana";', 'name "bad\\xZZ";'),
                     self.source.replace('name "Ana";', "name 'Ana';"),
                     self.source.replace('profile MACHINE_LEARNING_ENGINEER;', 'profile UNKNOWN;')]
        for source in malformed:
            with self.assertRaises(TextXSyntaxError):
                parse_candidate_dsl(source)

    def test_duplicate_skills_and_profiles(self):
        for source in (self.source.replace('skill PYTHON;', 'skill PYTHON; skill PYTHON;'),
                       self.source.replace('profile MACHINE_LEARNING_ENGINEER;',
                                           'profile MACHINE_LEARNING_ENGINEER; profile MACHINE_LEARNING_ENGINEER;')):
            with self.assertRaises(ValueError):
                parse_candidate_dsl(source)

    def test_inconsistent_classification_claims(self):
        for source in (self.source.replace('profile MACHINE_LEARNING_ENGINEER;', ''),
                       self.source.replace('profile MACHINE_LEARNING_ENGINEER;', 'profile FULL_STACK_DEVELOPER;')):
            with self.assertRaises(ValueError):
                parse_candidate_dsl(source)

    def test_all_catalog_symbols_are_lexically_supported(self):
        template = 'candidate { name null; contacts {} education {} experience {} skills { skill %s; } accepted_profiles {} }'
        for item in load_catalog()["skills"]:
            symbol = item["canonical"]
            with self.subTest(symbol=symbol):
                self.assertEqual(parse_candidate_dsl(template % symbol)["skills"], [symbol])

    def test_three_simultaneous_profiles(self):
        text = (ROOT / 'data/samples/08_multiple_records.txt').read_text(encoding='utf-8')
        first = process_resume(text)
        candidate = parse_candidate_dsl(generate_candidate_dsl(first, classify_skills(first['normalized_skills'])))
        self.assertEqual(candidate['accepted_profiles'], ['BACKEND_DEVELOPER', 'DATA_ENGINEER', 'MACHINE_LEARNING_ENGINEER'])

    def test_packaged_grammar_and_invalid_input_type(self):
        self.assertTrue(files('resumelens').joinpath('candidate.tx').is_file())
        with self.assertRaises(ValueError):
            parse_candidate_dsl(None)
        with self.assertRaises(TextXSyntaxError):
            parse_candidate_dsl('')

    def test_generator_does_not_modify_previous_results(self):
        before = copy.deepcopy((self.first, self.classification))
        first_generation = generate_candidate_dsl(self.first, self.classification)
        second_generation = generate_candidate_dsl(self.first, self.classification)
        self.assertEqual(first_generation, second_generation)
        self.assertEqual((self.first, self.classification), before)

    def test_all_preserved_valid_and_invalid_examples(self):
        report = json.loads((ROOT / 'data/dsl/validation.json').read_text(encoding='utf-8'))
        self.assertEqual((len(report['valid']), len(report['invalid'])), (8, 8))
        for case in report['valid']:
            path = ROOT / case['dsl']
            parsed = parse_candidate_dsl(path.read_text(encoding='utf-8'))
            self.assertEqual(parsed, json.loads(path.with_suffix('.json').read_text(encoding='utf-8')))
            self.assertEqual(parsed['accepted_profiles'], case['accepted_profiles'])
        for case in report['invalid']:
            error = TextXSyntaxError if case['error_kind'] == 'syntax' else ValueError
            with self.subTest(example=case['dsl']):
                with self.assertRaises(error):
                    parse_candidate_dsl((ROOT / case['dsl']).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
