from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


GRADING_COLUMNS = [
    "item_id",
    "subject",
    "source",
    "knowledge",
    "question",
    "student_answer",
    "correct_answer",
    "is_correct",
    "error_type",
    "feynman_status",
    "redo_required",
    "points_delta",
    "note",
]


def _submission_folder(spec: dict[str, Any], root: Path) -> Path:
    folder = Path(spec["voice_intake"]["folder"])
    if not folder.is_absolute():
        folder = root / folder
    return folder


def _iter_questions(spec: dict[str, Any]) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    for section in spec.get("sections", []):
        for question in section.get("questions", []):
            questions.append(question)
    return questions


def _write_readme(spec: dict[str, Any], folder: Path) -> None:
    voice = spec["voice_intake"]
    parent = spec.get("parent_card", {})
    day_slug = str(spec["day"]).lower()
    operating_note = (
        "先打开网页练习台，完成后导出结果 JSON；PDF 是备用。"
        if spec.get("mode") == "web-first"
        else "不用打开电脑，先看 PDF 第3页《大副今日操作卡》。"
    )
    clip_lines = [
        f"- `{clip['name']}`：{clip['duration']}，{clip['prompt']}"
        for clip in voice.get("requested_clips", [])
    ]
    text = "\n".join(
        [
            f"# {spec['day']} 提交包",
            "",
            f"练习：{spec['title']}",
            "",
            operating_note,
            "",
            "## 放入网页结果",
            "",
            f"- `{spec['day']}-result.json`：网页练习台导出的结果",
            "",
            "## 放入照片",
            "",
            f"- `{day_slug}-page1.jpg`：第1页做题区或草稿",
            f"- `{day_slug}-page2.jpg`：第2页做题区和课堂雷达",
            "",
            "## 放入语音",
            "",
            *clip_lines,
            "",
            "## 大副当天确认",
            "",
            f"- 输入：{' / '.join(parent.get('inputs', []))}",
            f"- 输出：{' / '.join(parent.get('outputs', []))}",
            "",
        ]
    )
    (folder / "README.md").write_text(text, encoding="utf-8")


def _write_voice_intake(spec: dict[str, Any], folder: Path) -> None:
    voice = spec["voice_intake"]
    lines = [
        f"# {spec['day']} 语音对齐清单",
        "",
        f"文件夹：`{voice['folder']}`",
        "",
        "## 待提交音频",
        "",
    ]
    for clip in voice.get("requested_clips", []):
        lines.extend(
            [
                f"### {clip['name']}",
                "",
                f"- 时长：{clip['duration']}",
                f"- 提示：{clip['prompt']}",
                "- 状态：[ ] 已收到  [ ] 需补录",
                "",
            ]
        )
    lines.extend(["## 课堂对齐备注", "", "- 语文：", "- 数学：", "- 英语：", ""])
    (folder / "voice-intake.md").write_text("\n".join(lines), encoding="utf-8")


def _write_grading_template(spec: dict[str, Any], folder: Path) -> None:
    with (folder / "grading-result.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=GRADING_COLUMNS)
        writer.writeheader()
        for question in _iter_questions(spec):
            writer.writerow(
                {
                    "item_id": question.get("id", ""),
                    "subject": question.get("subject", ""),
                    "source": question.get("source", ""),
                    "knowledge": question.get("knowledge", ""),
                    "question": question.get("prompt", ""),
                    "correct_answer": question.get("answer", ""),
                }
            )


def prepare_submission_packet(spec: dict[str, Any], root: Path) -> Path:
    folder = _submission_folder(spec, root)
    folder.mkdir(parents=True, exist_ok=True)
    _write_readme(spec, folder)
    _write_voice_intake(spec, folder)
    _write_grading_template(spec, folder)
    return folder
