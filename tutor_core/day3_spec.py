from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from tutor_core.points import POINTS_GOAL, read_current_points


ROOT = Path(__file__).resolve().parents[1]


def read_grading_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.DictReader(f) if any((v or "").strip() for v in row.values())]


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "对", "正确"}


def _wrong_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if not truthy(row.get("is_correct", "")) or truthy(row.get("redo_required", ""))]


def _question(item_id: str, source: str, knowledge: str, prompt: str, answer: str, kind: str = "practice") -> dict[str, str]:
    return {
        "id": item_id,
        "source": source,
        "subject": "数学",
        "knowledge": knowledge,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
    }


def build_day3_spec(rows: list[dict[str, str]]) -> dict[str, Any]:
    wrong = _wrong_rows(rows)
    wrong_by_knowledge = {row.get("knowledge", ""): row for row in wrong}

    sections = [
        {
            "title": "Normal Rod - 进门回测",
            "hint": "只测昨天跑掉的鱼，不加新难点",
            "questions": [
                _question(
                    "D3-R1",
                    "Day2错题回炉",
                    "除法计算与运算顺序",
                    "回炉1. 752 ÷ 8 + 406 ÷ 7 = ______（先估一估，再按顺序算）",
                    "152",
                ),
                _question(
                    "D3-R2",
                    "Day2错题回炉",
                    "容量单位换算和有余数除法",
                    "回炉2. 2升40ml = ____ml；分装 200ml 瓶，可装满____瓶，剩____ml。",
                    "2040ml；10瓶，剩40ml",
                ),
                _question(
                    "D3-R3",
                    "Day2错题回炉",
                    "两位数退位减法",
                    "回炉3. 44 - 18 = ______（个位不够，先退一十）",
                    "26",
                ),
            ],
        },
        {
            "title": "Monster Rod - 补做 Boss 战",
            "hint": "补 Day2 第2页核心理解",
            "questions": [
                _question(
                    "D3-B1",
                    "Day2 Boss补验",
                    "除法陷阱",
                    "Boss1. 480÷4 + 480÷6 = ______。能不能写成 480÷(4+6)？[  ]能 [  ]不能",
                    "200；不能",
                    "boss",
                ),
                _question(
                    "D3-B2",
                    "Day2 Boss补验",
                    "除法陷阱",
                    "Boss2. 判断：300÷5 + 300÷10 = 300÷(5+10)    [  ]对  [  ]错",
                    "错",
                    "boss",
                ),
                _question(
                    "D3-B3",
                    "Day2 Boss补验",
                    "除法陷阱",
                    "Boss3. 填空：被除数（  ）拆开，除数（  ）拆开。",
                    "可以；不能",
                    "boss",
                ),
            ],
        },
        {
            "title": "Super Rod - 轻量变式",
            "hint": "做完就收工，不追加",
            "questions": [
                _question(
                    "D3-V1",
                    "同型检查",
                    "容量单位换算和有余数除法",
                    "变式1. 3升120ml 分装 240ml 瓶，可装满____瓶，剩____ml。",
                    "13瓶，剩0ml",
                ),
                _question(
                    "D3-V2",
                    "同型检查",
                    "两位数退位减法",
                    "变式2. 52 - 27 = ______",
                    "25",
                ),
            ],
        },
    ]

    return {
        "day": "Day3",
        "title": "Day3-海王龙的逆向追踪",
        "mode": "回炉版",
        "focus": "除法陷阱 + Day2三条逃脱鱼回炉",
        "source_session": "2026-06-04-Day2",
        "points": {"current": read_current_points(ROOT), "goal": POINTS_GOAL},
        "knowledge_fish": {"current": 2, "goal": 93},
        "decision_basis": {
            "graded_items": len(rows),
            "wrong_or_redo": len(wrong),
            "missing_modules": ["Day2第2页Boss战", "家校雷达", "费曼教学", "课堂语音反馈"],
            "weak_knowledge": sorted(k for k in wrong_by_knowledge if k),
        },
        "sections": sections,
        "feynman": {
            "target": "除数不能合并",
            "prompt": "请船长讲清楚：为什么 480÷4 + 480÷6 不能写成 480÷(4+6)？",
            "pass_rule": "能说出这是两次分，不是一次按10分；除数不能随便合并。",
            "voice_option": "可以现场勾选，也可以录一段30-60秒语音放进本次 submissions 文件夹。",
        },
        "parent_card": {
            "title": "大副今日操作卡",
            "headline": "不用打开电脑，照这张纸执行。",
            "before": [
                "准备铅笔、橡皮、计时器，先看状态：绿/黄/红。",
                "告诉袁佳乐：今天只追昨天逃脱的鱼，不额外加题。",
            ],
            "during": [
                "先做进门回测，再做 Boss，不会就跳过标星。",
                "费曼环节只问“为什么”，少讲答案，让孩子讲给你听。",
            ],
            "after": [
                "拍第1页、第2页做题区，放入今日作业文件夹。",
                "录课堂反馈和 Boss 讲题两段短语音，完成即收工。",
            ],
            "inputs": ["做题照片", "课堂反馈语音", "Boss讲题语音"],
            "outputs": ["Day4练习", "掌握度更新", "袁佳乐进度反馈"],
        },
        "classroom_radar": [
            "语文今天讲到：________________  我记得一个词：________________",
            "数学今天讲到：________________  我觉得：[ ]会 [ ]半会 [ ]不会",
            "英语今天讲到：________________  我记得一句：________________",
            "大副补充：老师强调/作业/测验：____________________________",
        ],
        "voice_intake": {
            "folder": "submissions/2026-06-05-Day3/",
            "accepted_files": [".m4a", ".mp3", ".wav", ".aac", ".ogg"],
            "requested_clips": [
                {
                    "name": "classroom-brief",
                    "duration": "30-90秒",
                    "prompt": "请爸爸或袁佳乐说：今天语文、数学、英语分别讲到哪里，老师强调了什么。",
                },
                {
                    "name": "feynman-boss",
                    "duration": "30-60秒",
                    "prompt": "请袁佳乐讲：为什么 480÷4 + 480÷6 不能写成 480÷(4+6)。",
                },
            ],
            "fallback": "如果今晚不方便录音，就在家庭教师操作台里写三句话。",
        },
    }


def write_spec(spec: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
