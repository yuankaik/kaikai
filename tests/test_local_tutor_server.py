from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class LocalTutorServerTests(unittest.TestCase):
    def test_serves_captain_page_and_accepts_submissions(self) -> None:
        from app.local_tutor_server import create_server
        from tutor_core.day4_spec import build_day4_spec

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "practice" / "specs").mkdir(parents=True)
            (root / "records").mkdir()
            (root / "records" / "switch2_points.txt").write_text("1903\n", encoding="utf-8")
            spec = build_day4_spec(ROOT)
            (root / "practice" / "specs" / "day4.json").write_text(
                json.dumps(spec, ensure_ascii=False),
                encoding="utf-8",
            )
            server = create_server(root, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                home = urllib.request.urlopen(base + "/", timeout=5).read().decode("utf-8")
                self.assertIn("/captain/Day4", home)

                page = urllib.request.urlopen(base + "/captain/Day4", timeout=5).read().decode("utf-8")
                self.assertIn("MediaRecorder", page)
                self.assertIn("完成今日出海", page)
                self.assertIn("听讲解", page)

                result_request = urllib.request.Request(
                    base + "/api/result",
                    data=json.dumps({"day": "Day4", "title": "Day4 Test"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                result = json.loads(urllib.request.urlopen(result_request, timeout=5).read().decode("utf-8"))
                self.assertTrue(result["ok"])
                self.assertEqual(result["day"], "Day4")
                self.assertEqual(result["points"]["delta"], 0)

                voice_request = urllib.request.Request(
                    base + "/api/recording?day=Day4&clip=boss",
                    data=b"voice-bytes",
                    headers={"Content-Type": "audio/webm"},
                    method="POST",
                )
                voice = json.loads(urllib.request.urlopen(voice_request, timeout=5).read().decode("utf-8"))
                self.assertTrue(voice["ok"])
                self.assertTrue((root / voice["path"]).exists())

                upload_request = urllib.request.Request(
                    base + "/api/school-mistake?day=Day4&name=paper.jpg",
                    data=b"image-bytes",
                    headers={"Content-Type": "image/jpeg"},
                    method="POST",
                )
                upload = json.loads(urllib.request.urlopen(upload_request, timeout=5).read().decode("utf-8"))
                self.assertTrue(upload["ok"])
                self.assertEqual(upload["status"], "needs_ocr")
                self.assertTrue((root / upload["path"]).exists())

                points_request = urllib.request.Request(
                    base + "/api/points/manual",
                    data=json.dumps({"delta": 9, "reason": "主动复盘错题", "password": "1234"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                points = json.loads(urllib.request.urlopen(points_request, timeout=5).read().decode("utf-8"))
                self.assertTrue(points["ok"])
                self.assertEqual(points["previous"], 1903)
                self.assertEqual(points["current"], 1912)

                blocked_request = urllib.request.Request(
                    base + "/api/points/manual",
                    data=json.dumps({"delta": 9, "reason": "wrong password", "password": "0000"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(blocked_request, timeout=5)
                self.assertEqual(ctx.exception.code, 403)
            finally:
                server.shutdown()
                server.server_close()

    def test_serves_target_volume_day5_page(self) -> None:
        from app.local_tutor_server import create_server

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = root / "practice" / "specs"
            specs.mkdir(parents=True)
            source = ROOT / "practice" / "specs" / "Day5-巨枪乌贼的回炉海域.json"
            (specs / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            server = create_server(root, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                page = urllib.request.urlopen(base + "/captain/Day5", timeout=5).read().decode("utf-8")
                self.assertEqual(page.count('data-question-id="'), 20)
                self.assertIn("Day5-巨枪乌贼的回炉海域", page)
                self.assertIn("听讲解", page)
                self.assertIn("school-vault", page)
            finally:
                server.shutdown()
                server.server_close()

    def test_today_route_and_next_day_generation(self) -> None:
        from app.local_tutor_server import create_server

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = root / "practice" / "specs"
            records = root / "records"
            specs.mkdir(parents=True)
            records.mkdir()
            (records / "switch2_points.txt").write_text("1903\n", encoding="utf-8")
            source = ROOT / "practice" / "specs" / "Day5-巨枪乌贼的回炉海域.json"
            (specs / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            server = create_server(root, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                today = urllib.request.urlopen(base + "/captain/today", timeout=5).read().decode("utf-8")
                self.assertIn("Day5-巨枪乌贼的回炉海域", today)

                next_request = urllib.request.Request(
                    base + "/api/next-day",
                    data=json.dumps({"completed_day": "Day5"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                next_day = json.loads(urllib.request.urlopen(next_request, timeout=5).read().decode("utf-8"))
                self.assertTrue(next_day["ok"])
                self.assertEqual(next_day["day"], "Day6")

                latest = urllib.request.urlopen(base + "/captain/today", timeout=5).read().decode("utf-8")
                self.assertIn("Day6-蓝鲸英语补给航线", latest)
                self.assertIn("evening", latest)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
