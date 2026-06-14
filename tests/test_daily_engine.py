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


class DailyEngineTests(unittest.TestCase):
    def test_generates_spec_pdf_and_submission_packet_from_config(self) -> None:
        from tutor_core.daily_engine import DailyBuildConfig, generate_daily_materials
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = DailyBuildConfig(
                day="Day3",
                source_grading_path=ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv",
                row_reader=lambda _: rows,
                spec_builder=build_day3_spec,
            )

            result = generate_daily_materials(root, config)

            self.assertEqual(result.spec["day"], "Day3")
            self.assertEqual(result.spec_path, root / "practice" / "specs" / f"{result.spec['title']}.json")
            self.assertEqual(result.pdf_path, root / f"{result.spec['title']}.pdf")
            self.assertTrue(result.spec_path.exists())
            self.assertTrue(result.pdf_path.exists())
            self.assertTrue((result.submission_folder / "README.md").exists())
            self.assertTrue((result.submission_folder / "voice-intake.md").exists())
            self.assertTrue((result.submission_folder / "grading-result.csv").exists())

    def test_day3_factory_uses_daily_engine_contract(self) -> None:
        from scripts.make_day3_from_day2 import build_day3_config
        from tutor_core.daily_engine import DailyBuildConfig

        config = build_day3_config(ROOT)

        self.assertIsInstance(config, DailyBuildConfig)
        self.assertEqual(config.day, "Day3")
        self.assertEqual(config.source_grading_path, ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")

    def test_generic_daily_script_resolves_registered_day(self) -> None:
        from scripts.generate_daily_practice import build_config_for_day
        from tutor_core.daily_engine import DailyBuildConfig

        config = build_config_for_day("Day3", ROOT)

        self.assertIsInstance(config, DailyBuildConfig)
        self.assertEqual(config.day, "Day3")

    def test_generic_daily_script_rejects_unregistered_day_with_clear_message(self) -> None:
        from scripts.generate_daily_practice import build_config_for_day

        with self.assertRaisesRegex(ValueError, "No daily builder registered for Day5"):
            build_config_for_day("Day5", ROOT)


if __name__ == "__main__":
    unittest.main()
