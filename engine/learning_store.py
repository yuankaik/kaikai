from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from engine.school_mistake_pipeline import ingest_school_upload


@dataclass(frozen=True)
class StoredResult:
    id: int
    day: str
    title: str
    completed_at: str


@dataclass(frozen=True)
class StoredRecording:
    id: int
    day: str
    clip: str
    path: Path


@dataclass(frozen=True)
class StoredSchoolMistakeUpload:
    id: int
    day: str
    original_name: str
    path: Path
    status: str = "queued"


class LearningStore:
    def __init__(self, root: Path, db_path: Path | None = None) -> None:
        self.root = root
        self.db_path = db_path or root / "data" / "learning.db"

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            conn.execute(
                """
                create table if not exists practice_results (
                    id integer primary key autoincrement,
                    day text not null,
                    title text not null,
                    completed_at text not null,
                    payload_json text not null,
                    created_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists recordings (
                    id integer primary key autoincrement,
                    day text not null,
                    clip text not null,
                    content_type text not null,
                    file_path text not null,
                    size_bytes integer not null,
                    created_at text not null
                )
                """
            )
            conn.execute(
                """
                create index if not exists idx_practice_results_day
                on practice_results(day, created_at)
                """
            )
            conn.execute(
                """
                create index if not exists idx_recordings_day
                on recordings(day, created_at)
                """
            )
            conn.execute(
                """
                create table if not exists school_mistake_uploads (
                    id integer primary key autoincrement,
                    day text not null,
                    original_name text not null,
                    content_type text not null,
                    file_path text not null,
                    size_bytes integer not null,
                    created_at text not null,
                    status text not null
                )
                """
            )
            conn.execute(
                """
                create index if not exists idx_school_mistake_uploads_day
                on school_mistake_uploads(day, created_at)
                """
            )
            conn.commit()

    def save_result(self, payload: dict[str, Any]) -> StoredResult:
        self.initialize()
        day = str(payload.get("day") or "unknown-day")
        title = str(payload.get("title") or day)
        completed_at = str(payload.get("completed_at") or _now_iso())
        created_at = _now_iso()
        payload_json = json.dumps(payload, ensure_ascii=False, indent=2)

        with closing(self._connect()) as conn:
            cursor = conn.execute(
                """
                insert into practice_results(day, title, completed_at, payload_json, created_at)
                values (?, ?, ?, ?, ?)
                """,
                (day, title, completed_at, payload_json, created_at),
            )
            row_id = int(cursor.lastrowid)
            conn.commit()
        return StoredResult(id=row_id, day=day, title=title, completed_at=completed_at)

    def save_recording(self, day: str, clip: str, content_type: str, data: bytes) -> StoredRecording:
        self.initialize()
        clean_day = _safe_name(day or "unknown-day")
        clean_clip = _safe_name(clip or "captain-brief")
        extension = _extension_for(content_type)
        folder = self.root / "content" / "voice" / clean_day
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{clean_clip}{extension}"
        file_path.write_bytes(data)

        with closing(self._connect()) as conn:
            cursor = conn.execute(
                """
                insert into recordings(day, clip, content_type, file_path, size_bytes, created_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (day, clip, content_type, str(file_path.relative_to(self.root)), len(data), _now_iso()),
            )
            row_id = int(cursor.lastrowid)
            conn.commit()
        return StoredRecording(id=row_id, day=day, clip=clip, path=file_path)

    def save_school_mistake_upload(
        self,
        day: str,
        original_name: str,
        content_type: str,
        data: bytes,
    ) -> StoredSchoolMistakeUpload:
        self.initialize()
        clean_day = _safe_name(day or "unknown-day")
        clean_name = _safe_name(Path(original_name or "school-work").stem)
        suffix = _safe_suffix(original_name, content_type)
        folder = self.root / "content" / "school_mistakes" / clean_day
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{clean_name}{suffix}"
        file_path.write_bytes(data)

        with closing(self._connect()) as conn:
            cursor = conn.execute(
                """
                insert into school_mistake_uploads(day, original_name, content_type, file_path, size_bytes, created_at, status)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (day, original_name, content_type, str(file_path.relative_to(self.root)), len(data), _now_iso(), "queued"),
            )
            row_id = int(cursor.lastrowid)
            conn.commit()
        relative_path = str(file_path.relative_to(self.root))
        draft = ingest_school_upload(
            self.root,
            row_id,
            day,
            original_name,
            relative_path,
            content_type,
            data,
        )
        with closing(self._connect()) as conn:
            conn.execute("update school_mistake_uploads set status = ? where id = ?", (draft.status, row_id))
            conn.commit()
        return StoredSchoolMistakeUpload(
            id=row_id,
            day=day,
            original_name=original_name,
            path=file_path,
            status=draft.status,
        )

    def school_mistake_stats(self, day: str | None = None) -> dict[str, int]:
        self.initialize()
        with closing(self._connect()) as conn:
            total = int(conn.execute("select count(*) from school_mistake_uploads").fetchone()[0])
            today = 0
            if day:
                today = int(
                    conn.execute(
                        "select count(*) from school_mistake_uploads where day = ?",
                        (day,),
                    ).fetchone()[0]
                )
        return {"total": total, "today": today}

    def list_school_mistake_uploads(self, limit: int = 8) -> list[StoredSchoolMistakeUpload]:
        self.initialize()
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                select id, day, original_name, file_path, status
                from school_mistake_uploads
                order by created_at desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            StoredSchoolMistakeUpload(
                id=int(row[0]),
                day=row[1],
                original_name=row[2],
                path=self.root / row[3],
                status=row[4],
            )
            for row in rows
        ]

    def list_results(self, day: str | None = None) -> list[StoredResult]:
        self.initialize()
        query = "select id, day, title, completed_at from practice_results"
        params: tuple[str, ...] = ()
        if day:
            query += " where day = ?"
            params = (day,)
        query += " order by created_at desc"
        with closing(self._connect()) as conn:
            rows = conn.execute(query, params).fetchall()
        return [StoredResult(id=int(row[0]), day=row[1], title=row[2], completed_at=row[3]) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _safe_name(value: str) -> str:
    keep = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            keep.append(char)
        else:
            keep.append("-")
    return "".join(keep).strip("-") or "item"


def _extension_for(content_type: str) -> str:
    lower = content_type.lower()
    if "mp4" in lower:
        return ".mp4"
    if "mpeg" in lower:
        return ".mp3"
    if "wav" in lower:
        return ".wav"
    if "ogg" in lower:
        return ".ogg"
    return ".webm"


def _safe_suffix(original_name: str, content_type: str) -> str:
    suffix = Path(original_name or "").suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".heic", ".pdf", ".txt", ".md"}:
        return suffix
    lower = content_type.lower()
    if "png" in lower:
        return ".png"
    if "webp" in lower:
        return ".webp"
    if "pdf" in lower:
        return ".pdf"
    return ".jpg"
