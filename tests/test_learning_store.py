from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class LearningStoreTests(unittest.TestCase):
    def test_saves_practice_result_to_sqlite(self) -> None:
        from engine.learning_store import LearningStore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LearningStore(root)
            stored = store.save_result(
                {
                    "day": "Day4",
                    "title": "Day4 Test",
                    "completed_at": "2026-06-05T20:00:00",
                    "answers": {"D4-R1": {"answer": "140"}},
                }
            )

            self.assertEqual(stored.day, "Day4")
            self.assertEqual(stored.id, 1)
            self.assertEqual(store.list_results("Day4")[0].title, "Day4 Test")
            self.assertTrue((root / "data" / "learning.db").exists())

    def test_saves_recording_file_and_metadata(self) -> None:
        from engine.learning_store import LearningStore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LearningStore(root)
            stored = store.save_recording("Day4", "boss", "audio/webm", b"voice-bytes")

            self.assertEqual(stored.day, "Day4")
            self.assertEqual(stored.clip, "boss")
            self.assertTrue(stored.path.exists())
            self.assertEqual(stored.path.read_bytes(), b"voice-bytes")

    def test_saves_school_mistake_upload(self) -> None:
        from engine.learning_store import LearningStore

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LearningStore(root)
            stored = store.save_school_mistake_upload("Day4", "paper.jpg", "image/jpeg", b"image-bytes")

            self.assertEqual(stored.day, "Day4")
            self.assertEqual(stored.original_name, "paper.jpg")
            self.assertEqual(stored.status, "needs_ocr")
            self.assertTrue(stored.path.exists())
            self.assertEqual(stored.path.read_bytes(), b"image-bytes")
            self.assertEqual(store.school_mistake_stats("Day4"), {"total": 1, "today": 1})
            self.assertEqual(store.school_mistake_stats("Day5"), {"total": 1, "today": 0})

    def test_structured_school_mistake_text_becomes_ready_draft(self) -> None:
        from engine.learning_store import LearningStore
        from engine.school_mistake_pipeline import read_school_mistake_drafts

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LearningStore(root)
            data = "\n".join(
                [
                    "科目：语文",
                    "知识点：修辞手法",
                    "题目：小河唱着歌向前跑。",
                    "错误答案：比喻",
                    "正确答案：拟人",
                    "错因：把人的动作判断漏了",
                ]
            ).encode("utf-8")
            stored = store.save_school_mistake_upload("Day6", "语文错题.txt", "text/plain", data)
            drafts = read_school_mistake_drafts(root)

        self.assertEqual(stored.status, "ready")
        self.assertEqual(drafts[0].status, "ready")
        self.assertEqual(drafts[0].subject, "语文")
        self.assertEqual(drafts[0].knowledge, "修辞手法")
        self.assertIn("小河唱着歌", drafts[0].prompt)


if __name__ == "__main__":
    unittest.main()
