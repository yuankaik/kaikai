from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class MistakeReviewTests(unittest.TestCase):
    def test_reads_failed_and_weak_rows_from_grading_log(self) -> None:
        from engine.mistake_review import read_recent_mistakes

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            records = root / "records"
            records.mkdir()
            (records / "grading-log.csv").write_text(
                "\n".join(
                    [
                        "session_id,date,item_id,subject,source,knowledge,prompt,student_answer,expected_answer,is_correct,error_type,status,redo,score_delta,note",
                        "s,2026-06-05,D3-B3,数学,Day2 Boss补验,除法陷阱,题目,错,对,0,概念语言不稳,weak,1,,需要回炉",
                        "s,2026-06-05,D3-V2,数学,同型检查,退位减法,题目,25,25,1,,pass,0,,正确",
                    ]
                ),
                encoding="utf-8",
            )

            mistakes = read_recent_mistakes(root)

        self.assertEqual(len(mistakes), 1)
        self.assertEqual(mistakes[0].item_id, "D3-B3")
        self.assertEqual(mistakes[0].category, "Boss失误")

    def test_reads_subject_sheets_from_workbook(self) -> None:
        from engine.mistake_review import read_recent_mistakes

        mistakes = read_recent_mistakes(ROOT)
        subjects = {mistake.subject for mistake in mistakes}

        self.assertIn("语文", subjects)
        self.assertIn("英语", subjects)
        self.assertTrue(any(mistake.prompt for mistake in mistakes if mistake.subject == "语文"))
        self.assertTrue(any(mistake.prompt for mistake in mistakes if mistake.subject == "英语"))


    def test_reads_ready_school_mistake_drafts(self) -> None:
        from engine.learning_store import LearningStore
        from engine.mistake_review import read_recent_mistakes

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = LearningStore(root)
            store.save_school_mistake_upload(
                "Day6",
                "english.txt",
                "text/plain",
                "\n".join(
                    [
                        "科目：英语",
                        "知识点：三单",
                        "题目：He ____ (like) fishing.",
                        "错误答案：like",
                        "正确答案：likes",
                        "错因：三单漏加s",
                    ]
                ).encode("utf-8"),
            )

            mistakes = read_recent_mistakes(root)

        self.assertEqual(len(mistakes), 1)
        self.assertEqual(mistakes[0].category, "学校错题")
        self.assertEqual(mistakes[0].subject, "英语")
        self.assertIn("fishing", mistakes[0].prompt)


if __name__ == "__main__":
    unittest.main()
