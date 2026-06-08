from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RodLevel:
    level: int
    name: str
    sea: str
    start_day: int
    end_day: int
    boss: str


ROD_LEVELS = [
    RodLevel(level=1, name="竹竿", sea="新手沙滩", start_day=1, end_day=3, boss="菊石大师"),
    RodLevel(level=2, name="碳素竿", sea="珊瑚礁", start_day=4, end_day=7, boss="沧龙"),
    RodLevel(level=3, name="合金竿", sea="沉船湾", start_day=8, end_day=11, boss="邓氏鱼"),
    RodLevel(level=4, name="深渊竿", sea="深海裂谷", start_day=12, end_day=15, boss="海王龙"),
    RodLevel(level=5, name="传说竿", sea="远古深渊", start_day=16, end_day=20, boss="龙王鲸"),
]


def rod_status_for_spec(spec: dict[str, Any]) -> dict[str, Any]:
    day_number = _day_number(str(spec.get("day", "")))
    current = _current_level(day_number)
    next_level = _next_level(current)
    span = current.end_day - current.start_day + 1
    completed_in_sea = min(max(day_number - current.start_day + 1, 1), span)
    progress = completed_in_sea / span
    materials = _materials_from_spec(spec)
    return {
        "day_number": day_number,
        "current": current,
        "next": next_level,
        "completed_in_sea": completed_in_sea,
        "days_in_sea": span,
        "progress": progress,
        "materials": materials,
        "upgrade_text": _upgrade_text(current, next_level),
    }


def _day_number(day: str) -> int:
    match = re.search(r"(\d+)", day)
    return int(match.group(1)) if match else 1


def _current_level(day_number: int) -> RodLevel:
    for level in ROD_LEVELS:
        if level.start_day <= day_number <= level.end_day:
            return level
    return ROD_LEVELS[-1]


def _next_level(current: RodLevel) -> RodLevel | None:
    index = ROD_LEVELS.index(current)
    if index + 1 >= len(ROD_LEVELS):
        return None
    return ROD_LEVELS[index + 1]


def _materials_from_spec(spec: dict[str, Any]) -> list[str]:
    boss_materials: list[str] = []
    other_materials: list[str] = []
    for section in spec.get("sections", []):
        for question in section.get("questions", []):
            reward = str(question.get("unlock_reward", "")).strip()
            if not reward:
                continue
            target = boss_materials if str(question.get("kind", "")).lower() == "boss" else other_materials
            if reward not in boss_materials and reward not in other_materials:
                target.append(reward)
    return (boss_materials + other_materials)[:6]


def _upgrade_text(current: RodLevel, next_level: RodLevel | None) -> str:
    if not next_level:
        return "最高等级已解锁，继续收集传说鱼。"
    return f"击败{current.boss}后，解锁{next_level.name} Lv.{next_level.level}。"
