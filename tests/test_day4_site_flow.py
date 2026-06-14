from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Day4SiteFlowTests(unittest.TestCase):
    def test_builds_day4_web_first_spec(self) -> None:
        from tutor_core.day4_spec import build_day4_spec
        from tutor_core.points import read_current_points

        spec = build_day4_spec(ROOT)

        self.assertEqual(spec["day"], "Day4")
        self.assertEqual(spec["mode"], "web-first")
        self.assertIn("除法", spec["focus"])
        self.assertEqual(spec["points"]["current"], read_current_points(ROOT))
        self.assertGreaterEqual(len(spec["sections"]), 3)
        ids = [q["id"] for section in spec["sections"] for q in section["questions"]]
        self.assertIn("D4-R1", ids)
        self.assertIn("D4-B1", ids)
        self.assertIn("D4-V1", ids)
        self.assertIn("feynman", spec)
        self.assertIn("classroom_radar", spec)

    def test_daily_script_registers_day4(self) -> None:
        from scripts.generate_daily_practice import build_config_for_day

        config = build_config_for_day("Day4", ROOT)

        self.assertEqual(config.day, "Day4")
        spec = config.spec_builder([])
        self.assertEqual(spec["title"], "Day4-虎鲸队长的除法航线")

    def test_day_web_exports_result_json_contract(self) -> None:
        from rendering.day_web import render_practice_html
        from tutor_core.day4_spec import build_day4_spec

        html = render_practice_html(build_day4_spec(ROOT))

        self.assertIn("导出结果", html)
        self.assertIn("downloadResult", html)
        self.assertIn("Day4-result.json", html)
        self.assertIn("hint_count", html)
        self.assertIn("revealed_answer", html)
        self.assertIn("self_check", html)

    def test_renders_captain_deck_homepage(self) -> None:
        from rendering.captain_site import render_captain_deck
        from tutor_core.day4_spec import build_day4_spec
        from tutor_core.points import POINTS_GOAL, read_current_points

        html = render_captain_deck([build_day4_spec(ROOT)])

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Captain Deck", html)
        self.assertIn("今日航线", html)
        self.assertIn("Day4-虎鲸队长的除法航线.html", html)
        self.assertIn(f"Switch2 {read_current_points(ROOT)}/{POINTS_GOAL}", html)
        self.assertIn("知识鱼图鉴", html)

    def test_generates_day4_site_files(self) -> None:
        import tempfile

        from scripts.generate_web_practice import generate_captain_deck, generate_web_practice_from_spec
        from tutor_core.day4_spec import build_day4_spec

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            spec = build_day4_spec(ROOT)
            page = generate_web_practice_from_spec(spec, out)
            index = generate_captain_deck([spec], out)

            self.assertEqual(page.name, "Day4-虎鲸队长的除法航线.html")
            self.assertEqual(index.name, "index.html")
            self.assertTrue(page.exists())
            self.assertTrue(index.exists())

    def test_day4_submission_packet_uses_day4_file_names(self) -> None:
        import tempfile

        from tutor_core.day4_spec import build_day4_spec
        from tutor_core.submission_packet import prepare_submission_packet

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = build_day4_spec(ROOT)
            packet = prepare_submission_packet(spec, root)
            readme = (packet / "README.md").read_text(encoding="utf-8")

            self.assertIn("day4-page1.jpg", readme)
            self.assertIn("Day4-result.json", readme)
            self.assertNotIn("day3-page1.jpg", readme)


if __name__ == "__main__":
    unittest.main()
