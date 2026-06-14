from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT.parent / ".deps"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if DEPS.exists() and str(DEPS) not in sys.path:
    sys.path.insert(0, str(DEPS))


class DayWebGenerationTests(unittest.TestCase):
    def test_renders_self_contained_web_practice_from_spec(self) -> None:
        from rendering.day_web import render_practice_html
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows
        from tutor_core.points import POINTS_GOAL, read_current_points

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)
        html = render_practice_html(spec)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Day3-海王龙的逆向追踪", html)
        self.assertIn(f"Switch2 {read_current_points(ROOT)}/{POINTS_GOAL}", html)
        self.assertIn("D3-R1", html)
        self.assertIn("D3-B3", html)
        self.assertIn("费曼 Boss 录音", html)
        self.assertIn("家校雷达", html)
        self.assertIn("大副提交", html)
        self.assertIn("localStorage", html)
        self.assertIn("<svg", html)
        self.assertNotIn("https://", html)

    def test_script_writes_web_file(self) -> None:
        from scripts.generate_web_practice import generate_web_practice

        spec_path = ROOT / "practice" / "specs" / "Day3-海王龙的逆向追踪.json"
        with tempfile.TemporaryDirectory() as tmp:
            output = generate_web_practice(spec_path, Path(tmp))

            self.assertEqual(output.name, "Day3-海王龙的逆向追踪.html")
            self.assertTrue(output.exists())
            self.assertIn("船长练习", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
