from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class RodSystemTests(unittest.TestCase):
    def test_day4_uses_carbon_rod_and_points_to_next_upgrade(self) -> None:
        from engine.rod_system import rod_status_for_spec
        from tutor_core.day4_spec import build_day4_spec

        status = rod_status_for_spec(build_day4_spec(ROOT))

        self.assertEqual(status["current"].name, "碳素竿")
        self.assertEqual(status["current"].level, 2)
        self.assertEqual(status["current"].sea, "珊瑚礁")
        self.assertEqual(status["next"].name, "合金竿")
        self.assertIn("Boss核心", status["materials"])
        self.assertIn("解锁合金竿 Lv.3", status["upgrade_text"])

    def test_day16_caps_at_legendary_rod(self) -> None:
        from engine.rod_system import rod_status_for_spec

        status = rod_status_for_spec({"day": "Day16", "sections": []})

        self.assertEqual(status["current"].name, "传说竿")
        self.assertIsNone(status["next"])
        self.assertIn("最高等级", status["upgrade_text"])


if __name__ == "__main__":
    unittest.main()
