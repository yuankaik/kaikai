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


class Day3SpecTests(unittest.TestCase):
    def test_builds_recovery_day_from_day2_grading(self) -> None:
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)

        self.assertEqual(spec["day"], "Day3")
        self.assertEqual(spec["mode"], "回炉版")
        self.assertEqual(spec["title"], "Day3-海王龙的逆向追踪")
        self.assertIn("除法陷阱", spec["focus"])

        questions = [q["prompt"] for section in spec["sections"] for q in section.get("questions", [])]
        self.assertTrue(any("752" in q and "406" in q for q in questions))
        self.assertFalse(any("754" in q and "408" in q for q in questions))
        self.assertTrue(any("2升40ml" in q and "200ml" in q for q in questions))
        self.assertFalse(any("6升641ml" in q and "255ml" in q for q in questions))
        self.assertTrue(any("44 - 18" in q for q in questions))
        self.assertTrue(any("480÷4 + 480÷6" in q for q in questions))
        self.assertIn("除数不能合并", spec["feynman"]["target"])
        self.assertIn("voice_intake", spec)
        self.assertIn("parent_card", spec)
        self.assertNotIn("handwriting", spec)

    def test_spec_can_be_written_as_json_safe_data(self) -> None:
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows, write_spec

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "day3.json"
            write_spec(spec, output)
            text = output.read_text(encoding="utf-8")

        self.assertIn('"day": "Day3"', text)
        self.assertIn("海王龙的逆向追踪", text)


class TypographyTests(unittest.TestCase):
    def test_wrap_preserves_digit_unit_tokens(self) -> None:
        from rendering.typography import wrap_text

        lines = wrap_text(
            "回炉2. 2升40ml = ____ml；分装 200ml 瓶，可装满几瓶，剩多少ml？",
            font_name="Helvetica",
            font_size=10.8,
            max_width=170,
        )

        joined = "\n".join(lines)
        self.assertIn("2升40ml", joined)
        self.assertIn("200ml", joined)
        self.assertNotIn("m\nl", joined)

    def test_wrap_uses_width_not_character_count(self) -> None:
        from rendering.typography import wrap_text

        lines = wrap_text(
            "15. 判断: 480÷4 + 480÷6 = 480÷(4+6)    [  ]对  [  ]错",
            font_name="Helvetica",
            font_size=10.8,
            max_width=220,
        )

        self.assertGreaterEqual(len(lines), 2)
        self.assertTrue(all(line.strip() for line in lines))


class PdfRendererTests(unittest.TestCase):
    def test_renderer_exposes_print_readable_font_sizes(self) -> None:
        from rendering.day_pdf import BODY_FONT_SIZE, QUESTION_FONT_SIZE, SMALL_FONT_SIZE

        self.assertGreaterEqual(QUESTION_FONT_SIZE, 12.0)
        self.assertGreaterEqual(BODY_FONT_SIZE, 12.0)
        self.assertGreaterEqual(SMALL_FONT_SIZE, 10.5)

    def test_rendered_pdf_keeps_units_together_and_replaces_handwriting_with_voice_intake(self) -> None:
        from rendering.day_pdf import render_practice_pdf
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows
        from pypdf import PdfReader

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "day3.pdf"
            render_practice_pdf(spec, output)
            reader = PdfReader(output)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        self.assertEqual(len(reader.pages), 3)
        self.assertIn("200ml", text)
        self.assertNotIn("6升641ml", text)
        self.assertNotIn("m\nl", text)
        self.assertIn("语音文件", text)
        self.assertIn("课堂反馈", text)
        self.assertIn("Boss3", text)
        self.assertIn("出海用时", text)
        self.assertNotIn("今日鱼币：+____", text)
        self.assertNotIn("+ 今日鱼币", text)
        self.assertNotIn("Switch2鱼币：", text)
        self.assertIn("大副今日操作卡", text)
        self.assertIn("船长做题", text)
        self.assertIn("不用打开电脑", text)
        self.assertNotIn("收杆练字", text)

    def test_rendered_pdf_has_balanced_page_density(self) -> None:
        from rendering.day_pdf import render_practice_pdf
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows
        from pypdf import PdfReader

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "day3.pdf"
            render_practice_pdf(spec, output)
            reader = PdfReader(output)
            page_text_lengths = [len(page.extract_text() or "") for page in reader.pages]

        self.assertTrue(all(280 <= length <= 1300 for length in page_text_lengths), page_text_lengths)

    def test_first_two_pages_use_most_of_the_printable_area(self) -> None:
        import rendering.day_pdf as day_pdf
        from rendering.day_pdf import render_practice_pdf
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)
        original_init = day_pdf.Sheet.__init__
        sheets = []

        def tracking_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            sheets.append(self)

        day_pdf.Sheet.__init__ = tracking_init
        try:
            with tempfile.TemporaryDirectory() as tmp:
                render_practice_pdf(spec, Path(tmp) / "day3.pdf")
        finally:
            day_pdf.Sheet.__init__ = original_init

        remaining_mm = {sheet.page_no: sheet.y / 72 * 25.4 for sheet in sheets}
        self.assertLessEqual(remaining_mm[1], 60.0, remaining_mm)
        self.assertLessEqual(remaining_mm[2], 60.0, remaining_mm)
        self.assertGreaterEqual(remaining_mm[1], 30.0, remaining_mm)
        self.assertGreaterEqual(remaining_mm[2], 30.0, remaining_mm)


class SubmissionPacketTests(unittest.TestCase):
    def test_prepares_submission_folder_from_spec(self) -> None:
        from tutor_core.day3_spec import build_day3_spec, read_grading_rows
        from tutor_core.submission_packet import prepare_submission_packet

        rows = read_grading_rows(ROOT / "submissions" / "2026-06-04-Day2" / "grading-result.csv")
        spec = build_day3_spec(rows)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = prepare_submission_packet(spec, root)

            readme = folder / "README.md"
            voice = folder / "voice-intake.md"
            grading = folder / "grading-result.csv"

            self.assertTrue(readme.exists())
            self.assertTrue(voice.exists())
            self.assertTrue(grading.exists())
            self.assertIn("day3-page1", readme.read_text(encoding="utf-8"))
            self.assertIn("classroom-brief", voice.read_text(encoding="utf-8"))
            self.assertIn("item_id,subject", grading.read_text(encoding="utf-8-sig").splitlines()[0])


if __name__ == "__main__":
    unittest.main()
