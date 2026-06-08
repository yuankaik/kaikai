from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


POINTS_GOAL = 3500
COMPLETION_POINTS = 15
CORRECT_POINTS = 2
PERFECT_BONUS = 10
LEDGER_COLUMNS = ["session", "date", "previous", "delta", "current", "rule", "correct", "total"]


@dataclass(frozen=True)
class PointsSettlement:
    session: str
    previous: int
    delta: int
    current: int
    already_settled: bool


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "对", "正确"}


def calculate_points_delta(rows: list[dict[str, str]]) -> int:
    graded = [row for row in rows if row.get("item_id") or row.get("question")]
    if not graded:
        return 0
    correct = sum(1 for row in graded if truthy(row.get("is_correct", "")))
    delta = COMPLETION_POINTS + correct * CORRECT_POINTS
    if correct == len(graded):
        delta += PERFECT_BONUS
    return delta


def read_current_points(root: Path) -> int:
    path = root / "records" / "switch2_points.txt"
    if not path.exists():
        return 0
    return int(path.read_text(encoding="utf-8").strip())


def write_current_points(root: Path, points: int) -> None:
    path = root / "records" / "switch2_points.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{points}\n", encoding="utf-8")


def _ledger_path(root: Path) -> Path:
    return root / "records" / "points-ledger.csv"


def _read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.DictReader(f)]


def settle_session_points(root: Path, session: str, rows: list[dict[str, str]]) -> PointsSettlement:
    previous = read_current_points(root)
    ledger_path = _ledger_path(root)
    ledger = _read_ledger(ledger_path)
    for row in ledger:
        if row.get("session") == session:
            return PointsSettlement(session=session, previous=previous, delta=0, current=previous, already_settled=True)

    delta = calculate_points_delta(rows)
    current = previous + delta
    write_current_points(root, current)

    graded = [row for row in rows if row.get("item_id") or row.get("question")]
    correct = sum(1 for row in graded if truthy(row.get("is_correct", "")))
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    exists = ledger_path.exists() and ledger_path.stat().st_size > 0
    with ledger_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "session": session,
                "date": date.today().isoformat(),
                "previous": previous,
                "delta": delta,
                "current": current,
                "rule": f"completion {COMPLETION_POINTS} + correct {correct}*{CORRECT_POINTS}",
                "correct": correct,
                "total": len(graded),
            }
        )
    return PointsSettlement(session=session, previous=previous, delta=delta, current=current, already_settled=False)


def award_report_points(root: Path, day: str, delta: int, correct: int = 0, total: int = 0) -> PointsSettlement:
    clean_day = str(day or "").strip() or "unknown-day"
    session = f"web-completion-{clean_day}"
    previous = read_current_points(root)
    ledger_path = _ledger_path(root)
    ledger = _read_ledger(ledger_path)
    for row in ledger:
        if row.get("session") == session:
            return PointsSettlement(session=session, previous=previous, delta=0, current=previous, already_settled=True)

    if delta <= 0:
        return PointsSettlement(session=session, previous=previous, delta=0, current=previous, already_settled=False)

    current = previous + delta
    write_current_points(root, current)

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    exists = ledger_path.exists() and ledger_path.stat().st_size > 0
    with ledger_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "session": session,
                "date": date.today().isoformat(),
                "previous": previous,
                "delta": delta,
                "current": current,
                "rule": "web completion report points",
                "correct": correct,
                "total": total,
            }
        )
    return PointsSettlement(session=session, previous=previous, delta=delta, current=current, already_settled=False)


def award_manual_points(root: Path, delta: int, reason: str, actor: str = "大副") -> PointsSettlement:
    if delta <= 0:
        raise ValueError("manual points must be positive")
    clean_reason = reason.strip()
    if not clean_reason:
        raise ValueError("manual points reason is required")

    previous = read_current_points(root)
    current = previous + delta
    write_current_points(root, current)

    session = f"manual-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    ledger_path = _ledger_path(root)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    exists = ledger_path.exists() and ledger_path.stat().st_size > 0
    with ledger_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "session": session,
                "date": date.today().isoformat(),
                "previous": previous,
                "delta": delta,
                "current": current,
                "rule": f"{actor}手动加分：{clean_reason}",
                "correct": "",
                "total": "",
            }
        )
    return PointsSettlement(session=session, previous=previous, delta=delta, current=current, already_settled=False)
