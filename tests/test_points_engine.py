from __future__ import annotations

import csv
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


class PointsEngineTests(unittest.TestCase):
    def test_calculates_day2_points_from_completion_and_correct_answers(self) -> None:
        from tutor_core.day3_spec import read_grading_rows
        from tutor_core.points import calculate_points_delta

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")

        self.assertEqual(calculate_points_delta(rows), 41)

    def test_settles_session_once_and_records_ledger(self) -> None:
        from tutor_core.day3_spec import read_grading_rows
        from tutor_core.points import settle_session_points

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records"
            records.mkdir()
            (records / "switch2_points.txt").write_text("1835\n", encoding="utf-8")

            first = settle_session_points(root, "2026-06-04-Day2", rows)
            second = settle_session_points(root, "2026-06-04-Day2", rows)

            self.assertEqual(first.delta, 41)
            self.assertEqual(first.previous, 1835)
            self.assertEqual(first.current, 1876)
            self.assertEqual(second.delta, 0)
            self.assertEqual(second.current, 1876)
            self.assertEqual((records / "switch2_points.txt").read_text(encoding="utf-8").strip(), "1876")

            with (records / "points-ledger.csv").open("r", encoding="utf-8-sig", newline="") as f:
                ledger_rows = list(csv.DictReader(f))
            self.assertEqual(len(ledger_rows), 1)
            self.assertEqual(ledger_rows[0]["session"], "2026-06-04-Day2")
            self.assertEqual(ledger_rows[0]["delta"], "41")

    def test_awards_manual_points_with_reason(self) -> None:
        from tutor_core.points import award_manual_points

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records"
            records.mkdir()
            (records / "switch2_points.txt").write_text("1903\n", encoding="utf-8")

            settlement = award_manual_points(root, 12, "主动讲清一道错题")

            self.assertEqual(settlement.previous, 1903)
            self.assertEqual(settlement.delta, 12)
            self.assertEqual(settlement.current, 1915)
            self.assertEqual((records / "switch2_points.txt").read_text(encoding="utf-8").strip(), "1915")
            with (records / "points-ledger.csv").open("r", encoding="utf-8-sig", newline="") as f:
                ledger_rows = list(csv.DictReader(f))
            self.assertEqual(ledger_rows[0]["delta"], "12")
            self.assertIn("主动讲清一道错题", ledger_rows[0]["rule"])

    def test_awards_web_report_points_once(self) -> None:
        from tutor_core.points import award_report_points

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records"
            records.mkdir()
            (records / "switch2_points.txt").write_text("2038\n", encoding="utf-8")

            first = award_report_points(root, "Day5", 366, correct=12, total=20)
            second = award_report_points(root, "Day5", 366, correct=12, total=20)

            self.assertEqual(first.delta, 366)
            self.assertEqual(first.current, 2404)
            self.assertEqual(second.delta, 0)
            self.assertEqual(second.current, 2404)
            with (records / "points-ledger.csv").open("r", encoding="utf-8-sig", newline="") as f:
                ledger_rows = list(csv.DictReader(f))
            self.assertEqual(ledger_rows[0]["session"], "web-completion-Day5")
            self.assertEqual(ledger_rows[0]["delta"], "366")


if __name__ == "__main__":
    unittest.main()
