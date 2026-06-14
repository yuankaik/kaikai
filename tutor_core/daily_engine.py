from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from rendering.day_pdf import render_practice_pdf
from tutor_core.submission_packet import prepare_submission_packet

RowReader = Callable[[Path], list[dict[str, str]]]
SpecBuilder = Callable[[list[dict[str, str]]], dict[str, Any]]


@dataclass(frozen=True)
class DailyBuildConfig:
    day: str
    source_grading_path: Path
    row_reader: RowReader
    spec_builder: SpecBuilder


@dataclass(frozen=True)
class DailyBuildResult:
    spec: dict[str, Any]
    spec_path: Path
    pdf_path: Path
    submission_folder: Path


def spec_output_path(root: Path, spec: dict[str, Any]) -> Path:
    return root / "practice" / "specs" / f"{spec['title']}.json"


def pdf_output_path(root: Path, spec: dict[str, Any]) -> Path:
    return root / f"{spec['title']}.pdf"


def generate_daily_materials(root: Path, config: DailyBuildConfig) -> DailyBuildResult:
    rows = config.row_reader(config.source_grading_path)
    spec = config.spec_builder(rows)
    if spec.get("day") != config.day:
        raise ValueError(f"Spec day {spec.get('day')} does not match config day {config.day}.")

    spec_path = spec_output_path(root, spec)
    pdf_path = pdf_output_path(root, spec)
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(_json_text(spec), encoding="utf-8")
    render_practice_pdf(spec, pdf_path)
    submission_folder = prepare_submission_packet(spec, root)

    return DailyBuildResult(
        spec=spec,
        spec_path=spec_path,
        pdf_path=pdf_path,
        submission_folder=submission_folder,
    )


def _json_text(spec: dict[str, Any]) -> str:
    import json

    return json.dumps(spec, ensure_ascii=False, indent=2)
