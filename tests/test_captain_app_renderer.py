from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class CaptainAppRendererTests(unittest.TestCase):
    def test_renders_child_facing_day_without_mate_buttons(self) -> None:
        from app.captain_renderer import render_captain_day
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_day(build_day4_spec(ROOT))

        self.assertIn("船长复盘", html)
        self.assertIn("MediaRecorder", html)
        self.assertIn("instantReport", html)
        self.assertIn("buildFeedbackReport", html)
        self.assertIn("feedback_report", html)
        self.assertIn("今日即时反馈报告", html)
        self.assertIn("学校错题收集", html)
        self.assertIn("school-vault", html)
        self.assertIn("/api/school-mistake", html)
        self.assertIn("/api/result", html)
        self.assertIn("/api/recording", html)
        self.assertIn("完成今日出海", html)
        self.assertIn("鱼竿升级", html)
        self.assertIn("碳素竿", html)
        self.assertIn("合金竿 Lv.3", html)
        self.assertIn("mission-scene", html)
        self.assertIn("Boss雷达", html)
        self.assertIn("出海任务", html)
        self.assertIn("scanSweep", html)
        self.assertNotIn("大副查看", html)
        self.assertNotIn("记录按钮", html)
        self.assertNotIn("data-answer-toggle", html)
        self.assertNotIn("data-hint", html)

    def test_growth_status_cards_open_visual_modals(self) -> None:
        from app.captain_renderer import render_captain_day
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_day(build_day4_spec(ROOT))

        self.assertIn('data-open-modal="coin"', html)
        self.assertIn('data-open-modal="skills"', html)
        self.assertIn('data-open-modal="rods"', html)
        self.assertIn('data-open-modal="school"', html)
        self.assertIn('data-open-modal="mistakes"', html)
        self.assertIn('data-open-modal="history"', html)
        self.assertIn("往日练习", html)
        self.assertIn("错误回顾", html)
        self.assertIn("coin-jar", html)
        self.assertIn("大副加分", html)
        self.assertIn("data-mate-award", html)
        self.assertIn("data-mate-points", html)
        self.assertIn("data-mate-password", html)
        self.assertIn("data-mate-reason", html)
        self.assertIn("rod-wall", html)
        self.assertIn("data-school-count", html)
        self.assertIn("mistake-review", html)
        self.assertIn("mistake-table", html)
        self.assertIn("mistake-tabs", html)
        self.assertIn('data-mistake-tab="数学"', html)
        self.assertIn('data-mistake-tab="语文"', html)
        self.assertIn('data-mistake-tab="英语"', html)
        self.assertIn('data-mistake-sheet="数学"', html)
        self.assertIn("船长答案", html)
        self.assertIn("正确方向", html)
        self.assertIn("<th>题目</th>", html)
        self.assertNotIn("<th>编号</th>", html)
        self.assertLess(html.index("<th>语音</th>"), html.index("<th>序号</th>"))
        self.assertLess(html.index("<th>再战</th>"), html.index("<th>序号</th>"))
        self.assertIn("听讲解", html)
        self.assertIn("变换题型再战一次", html)
        self.assertIn("data-rematch-panel", html)
        self.assertIn("data-rematch-trigger", html)
        self.assertIn("data-rematch-question-text", html)
        self.assertIn("错题原题", html)
        self.assertIn("具体解法", html)
        self.assertIn("solutionStepsFor", html)
        self.assertIn("skill-map", html)
        self.assertNotIn('data-open-modal="streak"', html)

    def test_language_mistakes_use_subject_specific_actions(self) -> None:
        from app.captain_renderer import render_captain_day
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_day(
            build_day4_spec(ROOT),
            mistakes=[
                {
                    "subject": "语文",
                    "category": "小题失误",
                    "knowledge": "修辞手法",
                    "prompt": "比喻/拟人识别",
                    "student_answer": "等第“合格须努力”",
                    "expected_answer": "需加强",
                    "note": "知识点缺失",
                    "item_id": "语文-1",
                },
                {
                    "subject": "英语",
                    "category": "小题失误",
                    "knowledge": "三单",
                    "prompt": "he/she/it +s/es",
                    "student_answer": "卷面有错",
                    "expected_answer": "需加强",
                    "note": "知识点缺失",
                    "item_id": "英语-1",
                },
            ],
        )

        self.assertIn("先找本体、喻体或人的动作", html)
        self.assertIn("判断修辞", html)
        self.assertIn("这是比喻还是拟人", html)
        self.assertIn("he/she/it 后动词加 s/es", html)
        self.assertIn("He ____ (like) fishing", html)
        self.assertNotIn("把这道错题换一组数字", html)

    def test_school_upload_queue_shows_pipeline_status(self) -> None:
        from app.captain_renderer import render_captain_day
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_day(
            build_day4_spec(ROOT),
            school_stats={"total": 2, "today": 1},
            school_uploads=[
                {"id": "1", "original_name": "paper.jpg", "status": "needs_ocr"},
                {"id": "2", "original_name": "english.txt", "status": "ready"},
            ],
            school_drafts=[
                {
                    "upload_id": "1",
                    "status": "needs_ocr",
                    "subject": "数学",
                    "knowledge": "待识别",
                    "prompt": "图片/PDF 已归档，等待 OCR 或人工校准。",
                },
                {
                    "upload_id": "2",
                    "status": "ready",
                    "subject": "英语",
                    "knowledge": "三单",
                    "prompt": "He ____ (like) fishing.",
                },
            ],
        )

        self.assertIn("最近上传队列", html)
        self.assertIn("待 OCR/人工校准", html)
        self.assertIn("已入错题回顾", html)
        self.assertIn("He ____ (like) fishing.", html)

    def test_gameplay_video_renders_as_success_case(self) -> None:
        from app.captain_renderer import render_captain_day
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_day(
            build_day4_spec(ROOT),
            {
                "videos": [
                    {
                        "title": "珊瑚礁样例",
                        "path": "../../resources/gameplay/clips/sample.mp4",
                        "mime_type": "video/mp4",
                    }
                ],
                "posters": [],
            },
        )

        self.assertIn("scene-video", html)
        self.assertIn("短视频成功样例", html)
        self.assertIn("/resources/gameplay/clips/sample.mp4", html)
        self.assertIn("Boss雷达", html)

    def test_home_links_to_available_day(self) -> None:
        from app.captain_renderer import render_home
        from tutor_core.day4_spec import build_day4_spec

        html = render_home([build_day4_spec(ROOT)])

        self.assertIn("/captain/Day4", html)
        self.assertIn("袁佳乐船长训练站", html)


if __name__ == "__main__":
    unittest.main()
