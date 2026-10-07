import unittest
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
