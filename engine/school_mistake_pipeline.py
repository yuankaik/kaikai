from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SchoolMistakeDraft:
    upload_id: int
    day: str
    original_name: str
    file_path: str
    status: str
    subject: str
    knowledge: str
    prompt: str
    student_answer: str
    expected_answer: str
    note: str


FIELDNAMES = [
    "upload_id",
    "created_at",
    "day",
    "original_name",
    "file_path",
    "status",
    "subject",
    "knowledge",
    "prompt",
    "student_answer",
    "expected_answer",
    "note",
]


def ingest_school_upload(
    root: Path,
    upload_id: int,
    day: str,
    original_name: str,
    relative_path: str,
    content_type: str,
    data: bytes,
) -> SchoolMistakeDraft:
    draft = _draft_from_text(upload_id, day, original_name, relative_path, content_type, data)
    if draft is None:
        draft = SchoolMistakeDraft(
            upload_id=upload_id,
            day=day,
            original_name=original_name,
            file_path=relative_path,
            status="needs_ocr",
            subject=_infer_subject(original_name),
            knowledge="待识别",
            prompt="图片/PDF 已归档，等待 OCR 或人工校准。",
            student_answer="待识别",
            expected_answer="待识别",
            note="当前本机未配置 OCR 引擎，先进入识别队列。",
        )
    _upsert_draft(root / "records" / "school-mistake-drafts.csv", draft)
    return draft


def read_school_mistake_drafts(root: Path) -> list[SchoolMistakeDraft]:
    path = root / "records" / "school-mistake-drafts.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    drafts = []
    for row in rows:
        drafts.append(
            SchoolMistakeDraft(
                upload_id=int(row.get("upload_id") or 0),
                day=row.get("day") or "",
                original_name=row.get("original_name") or "",
                file_path=row.get("file_path") or "",
                status=row.get("status") or "needs_ocr",
                subject=row.get("subject") or "数学",
                knowledge=row.get("knowledge") or "待识别",
                prompt=row.get("prompt") or "",
                student_answer=row.get("student_answer") or "",
                expected_answer=row.get("expected_answer") or "",
                note=row.get("note") or "",
            )
        )
    return drafts


def _draft_from_text(
    upload_id: int,
    day: str,
    original_name: str,
    relative_path: str,
    content_type: str,
    data: bytes,
) -> SchoolMistakeDraft | None:
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".txt", ".md"} and "text" not in content_type.lower():
        return None
    text = data.decode("utf-8-sig", errors="ignore").strip()
    if not text:
        return None
    fields = _parse_key_values(text)
    prompt = fields.get("题目") or fields.get("prompt") or text.splitlines()[0]
    return SchoolMistakeDraft(
        upload_id=upload_id,
        day=day,
        original_name=original_name,
        file_path=relative_path,
        status="ready",
        subject=fields.get("科目") or fields.get("subject") or _infer_subject(original_name),
        knowledge=fields.get("知识点") or fields.get("knowledge") or "学校错题",
        prompt=prompt,
        student_answer=fields.get("错误答案") or fields.get("student_answer") or "待核对",
        expected_answer=fields.get("正确答案") or fields.get("expected_answer") or "待核对",
        note=fields.get("错因") or fields.get("note") or "学校错题上传识别",
    )


def _parse_key_values(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
        elif "：" in line:
            key, value = line.split("：", 1)
        else:
            continue
        fields[key.strip()] = value.strip()
    return fields


def _upsert_draft(path: Path, draft: SchoolMistakeDraft) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    rows = [row for row in rows if str(row.get("upload_id")) != str(draft.upload_id)]
    rows.append(
        {
            "upload_id": str(draft.upload_id),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "day": draft.day,
            "original_name": draft.original_name,
            "file_path": draft.file_path,
            "status": draft.status,
            "subject": draft.subject,
            "knowledge": draft.knowledge,
            "prompt": draft.prompt,
            "student_answer": draft.student_answer,
            "expected_answer": draft.expected_answer,
            "note": draft.note,
        }
    )
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _infer_subject(name: str) -> str:
    text = name.lower()
    if "语文" in name or "chinese" in text:
        return "语文"
    if "英语" in name or "english" in text:
        return "英语"
    return "数学"
