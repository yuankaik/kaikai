from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from engine.school_mistake_pipeline import read_school_mistake_drafts


@dataclass(frozen=True)
class MistakeCard:
    item_id: str
    source: str
    subject: str
    knowledge: str
    prompt: str
    student_answer: str
    expected_answer: str
    status: str
    note: str
    category: str


def read_recent_mistakes(root: Path, limit: int = 6) -> list[MistakeCard]:
    mistakes = _read_grading_log(root)
    mistakes.extend(_read_workbook(root))
    mistakes.extend(_read_school_drafts(root))
    mistakes = _dedupe(mistakes)
    return _limited_by_subject(mistakes, limit)


def _read_grading_log(root: Path) -> list[MistakeCard]:
    path = root / "records" / "grading-log.csv"
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    mistakes: list[MistakeCard] = []
    for row in rows:
        if not _needs_review(row):
            continue
        item_id = _cell(row, "item_id")
        source = _cell(row, "source")
        mistakes.append(
            MistakeCard(
                item_id=item_id,
                source=source,
                subject=_cell(row, "subject"),
                knowledge=_cell(row, "knowledge"),
                prompt=_cell(row, "prompt") or _cell(row, "question"),
                student_answer=_cell(row, "student_answer"),
                expected_answer=_cell(row, "expected_answer"),
                status=_cell(row, "status"),
                note=_cell(row, "note"),
                category=_category_for(item_id, source),
            )
        )

    return mistakes


def _read_workbook(root: Path) -> list[MistakeCard]:
    path = root / "袁佳乐错题本.xlsx"
    if not path.exists():
        candidates = list(root.glob("*错题本*.xlsx"))
        if not candidates:
            return []
        path = candidates[0]

    try:
        sheets = _read_xlsx_tables(path)
    except Exception:
        return []

    mistakes: list[MistakeCard] = []
    for subject in ("数学", "语文", "英语"):
        rows = sheets.get(subject, [])
        if not rows:
            continue
        header_index = _find_header_row(rows)
        if header_index is None:
            continue
        headers = rows[header_index]
        for values in rows[header_index + 1 :]:
            row = _row_dict(headers, values)
            if not _workbook_needs_review(row):
                continue
            source = _cell(row, "来源")
            item_id = f"{subject}-{_cell(row, '序号') or len(mistakes) + 1}"
            mistakes.append(
                MistakeCard(
                    item_id=item_id,
                    source=source,
                    subject=subject,
                    knowledge=_cell(row, "知识点分类"),
                    prompt=_cell(row, "题目"),
                    student_answer=_cell(row, "错误答案"),
                    expected_answer=_cell(row, "正确答案"),
                    status=_cell(row, "重做结果") or "待回炉",
                    note=_cell(row, "错因类型"),
                    category=_category_for(item_id, source),
                )
            )
    return mistakes


def _read_school_drafts(root: Path) -> list[MistakeCard]:
    mistakes: list[MistakeCard] = []
    for draft in read_school_mistake_drafts(root):
        if draft.status != "ready":
            continue
        mistakes.append(
            MistakeCard(
                item_id=f"SCHOOL-{draft.upload_id}",
                source=f"学校错题上传/{draft.day}",
                subject=draft.subject,
                knowledge=draft.knowledge,
                prompt=draft.prompt,
                student_answer=draft.student_answer,
                expected_answer=draft.expected_answer,
                status="weak",
                note=draft.note,
                category="学校错题",
            )
        )
    return mistakes


def _read_xlsx_tables(path: Path) -> dict[str, list[list[str]]]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with ZipFile(path) as book:
        shared_strings = _read_shared_strings(book, ns)
        workbook = ElementTree.fromstring(book.read("xl/workbook.xml"))
        rels = ElementTree.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("pkg:Relationship", ns)
        }
        tables: dict[str, list[list[str]]] = {}
        for sheet in workbook.findall("main:sheets/main:sheet", ns):
            title = sheet.attrib.get("name", "")
            rel_id = sheet.attrib.get(f"{{{ns['rel']}}}id", "")
            target = targets.get(rel_id, "")
            if not title or not target:
                continue
            sheet_path = "xl/" + target.lstrip("/")
            if sheet_path not in book.namelist():
                sheet_path = "xl/worksheets/" + Path(target).name
            tables[title] = _read_sheet(book.read(sheet_path), shared_strings, ns)
        return tables


def _read_shared_strings(book: ZipFile, ns: dict[str, str]) -> list[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall("main:si", ns):
        parts = [node.text or "" for node in item.findall(".//main:t", ns)]
        strings.append("".join(parts))
    return strings


def _read_sheet(data: bytes, shared_strings: list[str], ns: dict[str, str]) -> list[list[str]]:
    root = ElementTree.fromstring(data)
    rows: list[list[str]] = []
    for row in root.findall(".//main:sheetData/main:row", ns):
        values: dict[int, str] = {}
        for cell in row.findall("main:c", ns):
            index = _column_index(cell.attrib.get("r", "A1"))
            values[index] = _cell_text(cell, shared_strings, ns)
        if values:
            width = max(values) + 1
            rows.append([values.get(index, "") for index in range(width)])
    return rows


def _cell_text(cell: ElementTree.Element, shared_strings: list[str], ns: dict[str, str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//main:t", ns)).strip()
    value = cell.find("main:v", ns)
    text = value.text if value is not None and value.text is not None else ""
    if cell_type == "s" and text:
        try:
            return shared_strings[int(text)].strip()
        except (ValueError, IndexError):
            return ""
    return text.strip()


def _column_index(ref: str) -> int:
    total = 0
    for char in ref:
        if not char.isalpha():
            break
        total = total * 26 + (ord(char.upper()) - ord("A") + 1)
    return max(total - 1, 0)


def _find_header_row(rows: list[list[str]]) -> int | None:
    for index, row in enumerate(rows):
        if "序号" in row and "知识点分类" in row and "题目" in row:
            return index
    return None


def _row_dict(headers: list[str], values: list[str]) -> dict[str, str]:
    return {header: values[index] if index < len(values) else "" for index, header in enumerate(headers)}


def _workbook_needs_review(row: dict[str, str]) -> bool:
    if not any(_cell(row, key) for key in ("知识点分类", "题目", "错误答案", "正确答案")):
        return False
    return _cell(row, "是否已毕业") != "是"


def _dedupe(mistakes: list[MistakeCard]) -> list[MistakeCard]:
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[MistakeCard] = []
    for mistake in mistakes:
        key = (mistake.subject, mistake.knowledge, mistake.prompt, mistake.student_answer)
        if key in seen:
            continue
        seen.add(key)
        unique.append(mistake)
    return unique


def _limited_by_subject(mistakes: list[MistakeCard], limit: int) -> list[MistakeCard]:
    by_subject: dict[str, list[MistakeCard]] = {"数学": [], "语文": [], "英语": []}
    for mistake in reversed(mistakes):
        subject = mistake.subject or "数学"
        by_subject.setdefault(subject, []).append(mistake)
    ordered: list[MistakeCard] = []
    for subject in ("数学", "语文", "英语"):
        items = by_subject.get(subject, [])
        items = sorted(items, key=lambda item: 0 if item.category == "Boss失误" else 1)
        ordered.extend(items[:limit])
    return ordered


def _needs_review(row: dict[str, str]) -> bool:
    status = _cell(row, "status").lower()
    return _cell(row, "is_correct") == "0" or status in {"fail", "weak"}


def _category_for(item_id: str, source: str) -> str:
    text = f"{item_id} {source}".lower()
    if "-b" in text or "boss" in text:
        return "Boss失误"
    return "小题失误"


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()
