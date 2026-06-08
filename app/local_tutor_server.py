from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from app.captain_renderer import render_captain_day, render_home
from app.captain_dashboard import render_dashboard
from engine.auto_grader import entry_test_questions, grade_session, save_grading_log
from engine.learning_store import LearningStore
from engine.mistake_review import read_recent_mistakes
from engine.school_mistake_pipeline import read_school_mistake_drafts
from tutor_core.media_assets import read_gameplay_manifest
from tutor_core.next_day import generate_next_day_spec, latest_day_spec
from tutor_core.points import POINTS_GOAL, award_manual_points, award_report_points, read_current_points


class LocalTutorServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], root: Path) -> None:
        super().__init__(server_address, LocalTutorHandler)
        self.root = root
        self.store = LearningStore(root)
        self.store.initialize()
        self.media_manifest = read_gameplay_manifest(root)


class LocalTutorHandler(BaseHTTPRequestHandler):
    server: LocalTutorServer

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/":
            self._send_html(render_home(_load_specs(self.server.root)))
            return
        if path == "/captain/today":
            spec = latest_day_spec(self.server.root)
            if not spec:
                self._send_text("Daily mission not found.", HTTPStatus.NOT_FOUND)
                return
            self._send_captain_spec(spec, str(spec.get("day") or "today"))
            return
        if path == "/captain/dashboard":
            self._send_html(render_dashboard(self.server.root))
            return
        if path.startswith("/captain/"):
            day = path.removeprefix("/captain/").strip("/")
            spec = _find_spec(self.server.root, day)
            if not spec:
                self._send_text("Daily mission not found.", HTTPStatus.NOT_FOUND)
                return
            self._send_captain_spec(spec, day)
            return
        if path.startswith("/resources/") or path.startswith("/content/"):
            self._send_file(path.strip("/"))
            return
        self._send_text("Not found.", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/result":
            self._handle_result()
            return
        if parsed.path == "/api/auto-grade":
            self._handle_auto_grade()
            return
        if parsed.path == "/api/recording":
            self._handle_recording(parse_qs(parsed.query))
            return
        if parsed.path == "/api/school-mistake":
            self._handle_school_mistake(parse_qs(parsed.query))
            return
        if parsed.path == "/api/points/manual":
            self._handle_manual_points()
            return
        if parsed.path == "/api/next-day":
            self._handle_next_day()
            return
        self._send_text("Not found.", HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_captain_spec(self, spec: dict[str, Any], day: str) -> None:
        spec = dict(spec)
        spec["points"] = {"current": read_current_points(self.server.root), "goal": POINTS_GOAL}
        self._send_html(
            render_captain_day(
                spec,
                read_gameplay_manifest(self.server.root),
                read_recent_mistakes(self.server.root),
                self.server.store.school_mistake_stats(day),
                self.server.store.list_school_mistake_uploads(),
                read_school_mistake_drafts(self.server.root),
                _load_specs(self.server.root),
            )
        )

    def _handle_auto_grade(self) -> None:
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
            day = str(payload.get("day") or "today")
            questions = payload.get("questions") or []
            answers = payload.get("answers") or {}
            
            # Generate entry test if needed
            entry = []
            if payload.get("include_entry_test"):
                recent_mistakes = read_recent_mistakes(self.server.root, limit=6)
                mistake_knowledges = [m.knowledge if hasattr(m, 'knowledge') else str(m.get('knowledge', '')) 
                                      for m in recent_mistakes[:3]]
                entry = entry_test_questions(mistake_knowledges)
            
            all_questions = entry + questions
            report = grade_session(day, all_questions, answers)
            
            # Save to grading log
            log_path = save_grading_log(self.server.root, report)
            
            # Award points
            from tutor_core.points import award_report_points
            settlement = award_report_points(
                self.server.root, day, report.total_points,
                report.ok_count, report.total_questions,
            )
            
            self._send_json({
                "ok": True,
                "day": day,
                "report": {
                    "total": report.total_questions,
                    "ok": report.ok_count,
                    "review": report.review_count,
                    "bad": report.bad_count,
                    "points": report.total_points,
                    "items": report.items,
                    "recovered_fish": report.recovered_fish,
                    "escaped_fish": report.escaped_fish,
                    "new_fish": report.new_knowledge_fish,
                },
                "points": {
                    "session": settlement.session,
                    "previous": settlement.previous,
                    "delta": settlement.delta,
                    "current": settlement.current,
                },
                "entry_test": entry,
            })
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _handle_result(self) -> None:
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
            stored = self.server.store.save_result(payload)
            report = payload.get("feedback_report") or {}
            settlement = award_report_points(
                self.server.root,
                str(payload.get("day") or stored.day),
                int(report.get("points") or 0),
                int(report.get("correct") or 0),
                len(report.get("items") or []),
            )
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(
            {
                "ok": True,
                "id": stored.id,
                "day": stored.day,
                "points": {
                    "session": settlement.session,
                    "previous": settlement.previous,
                    "delta": settlement.delta,
                    "current": settlement.current,
                    "already_settled": settlement.already_settled,
                },
            }
        )

    def _handle_recording(self, query: dict[str, list[str]]) -> None:
        day = _query_value(query, "day", "unknown-day")
        clip = _query_value(query, "clip", "captain-brief")
        content_type = self.headers.get("Content-Type", "audio/webm")
        data = self._read_body()
        if not data:
            self._send_json({"ok": False, "error": "empty recording"}, HTTPStatus.BAD_REQUEST)
            return
        stored = self.server.store.save_recording(day, clip, content_type, data)
        self._send_json({"ok": True, "id": stored.id, "path": str(stored.path.relative_to(self.server.root))})

    def _handle_school_mistake(self, query: dict[str, list[str]]) -> None:
        day = _query_value(query, "day", "unknown-day")
        name = _query_value(query, "name", "school-work.jpg")
        content_type = self.headers.get("Content-Type", "application/octet-stream")
        data = self._read_body()
        if not data:
            self._send_json({"ok": False, "error": "empty upload"}, HTTPStatus.BAD_REQUEST)
            return
        stored = self.server.store.save_school_mistake_upload(day, name, content_type, data)
        self._send_json(
            {
                "ok": True,
                "id": stored.id,
                "path": str(stored.path.relative_to(self.server.root)),
                "status": stored.status,
            }
        )

    def _handle_manual_points(self) -> None:
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
            if str(payload.get("password") or "") != "1234":
                raise PermissionError("password required")
            delta = int(payload.get("delta") or 0)
            reason = str(payload.get("reason") or "")
            settlement = award_manual_points(self.server.root, delta, reason, "大副")
        except PermissionError as exc:
            self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.FORBIDDEN)
            return
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(
            {
                "ok": True,
                "session": settlement.session,
                "previous": settlement.previous,
                "delta": settlement.delta,
                "current": settlement.current,
            }
        )

    def _handle_next_day(self) -> None:
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
            completed_day = str(payload.get("completed_day") or payload.get("day") or "")
            spec = generate_next_day_spec(self.server.root, completed_day)
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json({"ok": True, "day": spec["day"], "title": spec["title"], "url": f"/captain/{spec['day']}"})

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length)

    def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(body.encode("utf-8"), "text/html; charset=utf-8", status)

    def _send_text(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(body.encode("utf-8"), "text/plain; charset=utf-8", status)

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def _send_file(self, relative_path: str) -> None:
        root = self.server.root.resolve()
        target = (root / relative_path).resolve()
        if not str(target).startswith(str(root)) or not target.exists() or not target.is_file():
            self._send_text("Not found.", HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self._send_bytes(target.read_bytes(), mime)

    def _send_bytes(self, data: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def create_server(root: Path, host: str = "127.0.0.1", port: int = 8000) -> LocalTutorServer:
    return LocalTutorServer((host, port), root)


def run(root: Path, host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(root, host, port)
    print(f"袁佳乐船长训练站: http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        server.server_close()


def _load_specs(root: Path) -> list[dict[str, Any]]:
    specs = []
    for path in sorted((root / "practice" / "specs").glob("*.json")):
        try:
            specs.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return specs


def _find_spec(root: Path, day: str) -> dict[str, Any] | None:
    for spec in _load_specs(root):
        if str(spec.get("day")) == day:
            return spec
    return None


def _query_value(query: dict[str, list[str]], key: str, default: str) -> str:
    values = query.get(key)
    if not values:
        return default
    return values[0] or default
