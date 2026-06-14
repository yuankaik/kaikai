from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tutor_core.points import POINTS_GOAL, read_current_points


DAY6_WORDS = ["evening", "night", "today", "tomorrow", "weekend"]


def generate_next_day_spec(root: Path, completed_day: str) -> dict[str, Any]:
    next_number = _day_number(completed_day) + 1
    spec = _build_day_spec(root, next_number)
    path = _spec_path(root, spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return spec


def latest_day_spec(root: Path) -> dict[str, Any] | None:
    specs = []
    for path in (root / "practice" / "specs").glob("*.json"):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        specs.append((_day_number(str(spec.get("day", ""))), spec))
    if not specs:
        return None
    return max(specs, key=lambda item: item[0])[1]


def _build_day_spec(root: Path, day_number: int) -> dict[str, Any]:
    words = _words_for_day(day_number)
    day = f"Day{day_number}"
    return {
        "day": day,
        "title": f"{day}-蓝鲸英语补给航线",
        "mode": "web-first",
        "focus": "数学错题回炉 + 英语词汇句型加量 + 艾宾浩斯复习",
        "source_session": "auto-after-completion",
        "points": {"current": read_current_points(root), "goal": POINTS_GOAL},
        "knowledge_fish": {"current": 3, "goal": 93},
        "practice_policy": {
            "target_questions": 22,
            "english_minimum": "每天至少5个单词，2道句型，1道语法小Boss。",
            "ebbinghaus": "艾宾浩斯节奏：新词当天读写；第1天、第3天、第7天、第15天回看。今天先复习 Day3-Day5 的英语词汇和句型。",
        },
        "sections": [
            {
                "title": "Normal Rod - 数学热身回炉",
                "hint": "先稳住已暴露薄弱点，不追求难题堆量",
                "questions": [
                    _q(day_number, "M1", "数学", "除法陷阱", "review", "480÷6 + 480÷8 = ____。能不能写成480÷14？", "140；不能", 2),
                    _q(day_number, "M2", "数学", "括号与混合运算", "review", "[3600-(20+80×10)]÷20 = ____", "139", 2),
                    _q(day_number, "M3", "数学", "小数巧算与运算顺序", "practice", "0.406 + 0.194 = ____", "0.6", 1),
                    _q(day_number, "M4", "数学", "应用题答句和单位", "practice", "计划每天180个，10天完成；提前1天完成，实际每天____个。", "200个", 2),
                    _q(day_number, "M5", "数学", "商和余数变化规律", "practice", "a÷b商9余7，a、b都乘10后，商____，余数____。", "9；70", 2),
                ],
            },
            {
                "title": "English Rod - 5词补给",
                "hint": "每天5词，不贪多；先会读、会认、会放进句子",
                "questions": [
                    _q(day_number, "E1", "英语", "词汇记忆", "vocab", f"读一读并写出中文：{words[0]}", "晚上", 1),
                    _q(day_number, "E2", "英语", "词汇记忆", "vocab", f"读一读并写出中文：{words[1]}", "夜晚", 1),
                    _q(day_number, "E3", "英语", "词汇记忆", "vocab", f"读一读并写出中文：{words[2]}", "今天", 1),
                    _q(day_number, "E4", "英语", "词汇记忆", "vocab", f"读一读并写出中文：{words[3]}", "明天", 1),
                    _q(day_number, "E5", "英语", "词汇记忆", "vocab", f"读一读并写出中文：{words[4]}", "周末", 1),
                ],
            },
            {
                "title": "English Rod - 句型小Boss",
                "hint": "围绕当前薄弱点：三单、进行时、句子完整性",
                "questions": [
                    _q(day_number, "E6", "英语", "三单", "practice", "He ____ (like) fishing after school.", "likes", 2),
                    _q(day_number, "E7", "英语", "现在进行时", "practice", "Look! The boy is ____ (run).", "running", 2),
                    _q(day_number, "E8", "英语", "be动词", "practice", "I ____ happy. You ____ my friend.", "am；are", 1),
                    _q(day_number, "E9", "英语", "句子书写", "practice", "把句子补完整：I go to school in the ____.", "morning", 1),
                    _q(day_number, "E10", "英语", "艾宾浩斯复习", "review", "复习 Day5 词汇：read / write / draw，任选2个造短句。", "开放题", 1),
                ],
            },
            {
                "title": "Monster Rod - 三科雷达",
                "hint": "保持家校对齐，短句即可",
                "questions": [
                    _q(day_number, "S1", "语文", "课堂词语回忆", "practice", "写出今天语文课你记住的一个词，并造一个短句。", "开放题", 1),
                    _q(day_number, "S2", "英语", "课堂句子复述", "practice", "写出今天英语课你记住的一句话。", "开放题", 1),
                    _q(day_number, "S3", "数学", "课堂同步", "practice", "今天数学课讲到哪里？写一个关键词。", "开放题", 1),
                    _q(day_number, "S4", "通用", "艾宾浩斯计划", "practice", "今天需要回看：Day3英语V-ing、Day4 There be、Day5不规则动词。勾选已看：[ ]", "开放题", 1),
                ],
            },
        ],
        "feynman": {
            "target": "英语三单 + 数学除法陷阱",
            "prompt": "请船长任选一道错题，用一句话讲清楚为什么错。",
            "pass_rule": "能说出关键规则即可，不要求长篇解释。",
        },
    }


def _q(day_number: int, suffix: str, subject: str, knowledge: str, kind: str, prompt: str, answer: str, difficulty: int) -> dict[str, Any]:
    return {
        "id": f"D{day_number}-{suffix}",
        "source": f"Day{day_number}网页练习",
        "subject": subject,
        "knowledge": knowledge,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
        "difficulty": difficulty,
        "unlock_reward": "知识鱼",
    }


def _words_for_day(day_number: int) -> list[str]:
    if day_number <= 6:
        return DAY6_WORDS
    return DAY6_WORDS


def _spec_path(root: Path, spec: dict[str, Any]) -> Path:
    return root / "practice" / "specs" / f"{spec['title']}.json"


def _day_number(day: str) -> int:
    match = re.search(r"Day(\d+)", day)
    if not match:
        return 0
    return int(match.group(1))
