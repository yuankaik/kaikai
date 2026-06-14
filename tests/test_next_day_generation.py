from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class NextDayGenerationTests(unittest.TestCase):
    def test_generates_day6_with_more_english_and_words(self) -> None:
        from tutor_core.next_day import generate_next_day_spec

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records"
            records.mkdir()
            (records / "switch2_points.txt").write_text("1903\n", encoding="utf-8")

            spec = generate_next_day_spec(root, "Day5")
            spec_exists = (root / "practice" / "specs" / f"{spec['title']}.json").exists()

        questions = [question for section in spec["sections"] for question in section["questions"]]
        english = [question for question in questions if question["subject"] == "英语"]
        vocab = [question for question in english if question["kind"] == "vocab"]

        self.assertEqual(spec["day"], "Day6")
        self.assertGreaterEqual(len(english), 7)
        self.assertGreaterEqual(len(vocab), 5)
        self.assertIn("艾宾浩斯", spec["practice_policy"]["ebbinghaus"])
        self.assertTrue(spec_exists)


if __name__ == "__main__":
    unittest.main()
