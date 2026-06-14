from __future__ import annotations

from pathlib import Path
from typing import Any

from tutor_core.points import POINTS_GOAL, read_current_points


def _question(
    item_id: str,
    subject: str,
    knowledge: str,
    prompt: str,
    answer: str,
    kind: str = "practice",
    difficulty: int = 1,
    unlock_reward: str = "",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "source": "Day4网页练习",
        "subject": subject,
        "knowledge": knowledge,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
        "difficulty": difficulty,
        "unlock_reward": unlock_reward,
    }


def build_day4_spec(root: Path) -> dict[str, Any]:
    return {
        "day": "Day4",
        "title": "Day4-虎鲸队长的除法航线",
        "mode": "web-first",
        "focus": "除法陷阱回炉 + 容量单位复测 + 三科课堂雷达",
        "source_session": "2026-06-05-Day3",
        "points": {"current": read_current_points(root), "goal": POINTS_GOAL},
        "knowledge_fish": {"current": 2, "goal": 93},
        "sections": [
            {
                "title": "Normal Rod - 热身航线",
                "hint": "先确认昨天的鱼没有再逃走",
                "questions": [
                    _question(
                        "D4-R1",
                        "数学",
                        "除法计算与运算顺序",
                        "640 ÷ 8 + 360 ÷ 6 = ____",
                        "140",
                        difficulty=1,
                        unlock_reward="热身鱼",
                    ),
                    _question(
                        "D4-R2",
                        "数学",
                        "两位数退位减法",
                        "61 - 28 = ____",
                        "33",
                        difficulty=1,
                        unlock_reward="退位鱼",
                    ),
                    _question(
                        "D4-R3",
                        "英语",
                        "课堂句子复述",
                        "写出今天英语课你记住的一句话：________________",
                        "开放题",
                        difficulty=1,
                        unlock_reward="英语贝壳",
                    ),
                ],
            },
            {
                "title": "Monster Rod - Boss识别",
                "hint": "今天只打一个核心Boss：除数不能随便合并",
                "questions": [
                    _question(
                        "D4-B1",
                        "数学",
                        "除法陷阱",
                        "判断：420÷7 + 420÷3 = 420÷(7+3)  [ ]对 [ ]错",
                        "错",
                        "boss",
                        2,
                        "Boss鳞片",
                    ),
                    _question(
                        "D4-B2",
                        "数学",
                        "除法陷阱",
                        "420÷7 + 420÷3 = ____。能不能写成 420÷10？",
                        "200；不能",
                        "boss",
                        2,
                        "Boss牙齿",
                    ),
                    _question(
                        "D4-B3",
                        "数学",
                        "费曼解释",
                        "用一句话解释：为什么除数不能合并？",
                        "因为这是两次分，除数代表每次怎么分，不能相加变成一次分。",
                        "boss",
                        3,
                        "Boss核心",
                    ),
                ],
            },
            {
                "title": "Super Rod - 轻量变式",
                "hint": "做完就收工，不追加",
                "questions": [
                    _question(
                        "D4-V1",
                        "数学",
                        "容量单位换算和有余数除法",
                        "2升500ml = ____ml；每瓶250ml，可装满____瓶。",
                        "2500ml；10瓶",
                        difficulty=2,
                        unlock_reward="容量鱼",
                    ),
                    _question(
                        "D4-V2",
                        "语文",
                        "课堂词语回忆",
                        "写出今天语文课你记住的一个词，并造一个短句。",
                        "开放题",
                        difficulty=1,
                        unlock_reward="语文贝壳",
                    ),
                ],
            },
        ],
        "feynman": {
            "target": "除数不能合并",
            "prompt": "请船长讲清楚：为什么 420÷7 + 420÷3 不能写成 420÷(7+3)？",
            "pass_rule": "能说出这是两次分，不是一次按10分；除数不能随便合并。",
        },
        "parent_card": {
            "title": "大副今日操作卡",
            "headline": "网页优先，纸笔草稿仍然允许。",
            "before": ["先问精神状态：绿/黄/红。", "告诉船长：今天只打一只Boss。"],
            "during": ["不会时允许点提示，但记录提示次数。", "大副只追问为什么，不连续讲课。"],
            "after": ["导出 Day4-result.json。", "录 Boss 讲题语音，放入 Day4 提交文件夹。"],
            "inputs": ["Day4-result.json", "Boss讲题语音", "课堂雷达"],
            "outputs": ["Day5回炉练习", "技能地图更新", "鱼币结算"],
        },
        "classroom_radar": [
            "语文今天讲到：________________  我记得一个词：________________",
            "数学今天讲到：________________  我觉得：[ ]会 [ ]半会 [ ]不会",
            "英语今天讲到：________________  我记得一句：________________",
        ],
        "voice_intake": {
            "folder": "submissions/2026-06-06-Day4/",
            "accepted_files": [".m4a", ".mp3", ".wav", ".aac", ".ogg"],
            "requested_clips": [
                {
                    "name": "classroom-brief",
                    "duration": "30-90秒",
                    "prompt": "请大副或袁佳乐说：今天语文、数学、英语分别讲到哪里，老师强调了什么。",
                },
                {
                    "name": "feynman-boss",
                    "duration": "30-60秒",
                    "prompt": "请袁佳乐讲：为什么 420÷7 + 420÷3 不能写成 420÷(7+3)。",
                },
            ],
            "fallback": "如果今晚不方便录音，就在网页课堂雷达里写关键词。",
        },
    }
