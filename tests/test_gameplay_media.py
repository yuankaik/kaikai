from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class GameplayMediaTests(unittest.TestCase):
    def test_discovers_local_gameplay_videos(self) -> None:
        from tutor_core.media_assets import discover_gameplay_media

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "resources" / "gameplay"
            source.mkdir(parents=True)
            (source / "ace-angler-boss.mp4").write_bytes(b"fake-video")
            (source / "notes.txt").write_text("ignore", encoding="utf-8")

            manifest = discover_gameplay_media(root)

            self.assertEqual(manifest["kind"], "gameplay-video")
            self.assertEqual(len(manifest["videos"]), 1)
            self.assertEqual(manifest["videos"][0]["title"], "ace angler boss")
            self.assertEqual(manifest["videos"][0]["path"], "../../resources/gameplay/ace-angler-boss.mp4")

    def test_renderers_use_optional_gameplay_video_manifest(self) -> None:
        from rendering.captain_site import render_captain_deck
        from rendering.day_web import render_practice_html
        from tutor_core.day4_spec import build_day4_spec

        media = {
            "kind": "gameplay-video",
            "videos": [
                {
                    "title": "ace angler boss",
                    "path": "../../resources/gameplay/ace-angler-boss.mp4",
                    "mime_type": "video/mp4",
                }
            ],
        }
        spec = build_day4_spec(ROOT)

        deck = render_captain_deck([spec], media_manifest=media)
        practice = render_practice_html(spec, media_manifest=media)

        self.assertIn("<video", deck)
        self.assertIn("<video", practice)
        self.assertIn("muted", deck)
        self.assertIn("playsinline", practice)
        self.assertIn("../../resources/gameplay/ace-angler-boss.mp4", deck)
        self.assertNotIn("https://", deck + practice)


if __name__ == "__main__":
    unittest.main()
