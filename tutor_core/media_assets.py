from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


VIDEO_EXTENSIONS = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
}


def _mime_for_path(path: Path) -> str:
    return VIDEO_EXTENSIONS.get(path.suffix.lower(), "video/mp4")


def _display_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip()


def discover_gameplay_media(root: Path) -> dict[str, Any]:
    source = root / "resources" / "gameplay"
    videos = []
    if source.exists():
        for path in sorted(source.iterdir()):
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
                videos.append(
                    {
                        "title": _display_title(path),
                        "path": f"../../resources/gameplay/{path.name}",
                        "mime_type": _mime_for_path(path),
                    }
                )
    posters = []
    poster_dir = source / "posters"
    if poster_dir.exists():
        for path in sorted(poster_dir.glob("*.jpg")):
            posters.append(
                {
                    "title": _display_title(path),
                    "path": f"../../resources/gameplay/posters/{path.name}",
                }
            )
    return {"kind": "gameplay-video", "videos": videos, "posters": posters}


def _find_ffmpeg(explicit_path: str | None = None) -> Path | None:
    if explicit_path:
        path = Path(explicit_path)
        if path.exists():
            return path
    found = shutil.which("ffmpeg")
    return Path(found) if found else None


def _read_bili_info(folder: Path) -> dict[str, Any] | None:
    info_path = folder / "videoInfo.json"
    if not info_path.exists():
        return None
    try:
        return json.loads(info_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _video_track(folder: Path) -> Path | None:
    candidates = sorted(
        [path for path in folder.glob("*.m4s") if path.stat().st_size > 50_000_000],
        key=lambda path: path.stat().st_size,
        reverse=True,
    )
    return candidates[0] if candidates else None


def import_bili_gameplay_assets(root: Path, bili_root: Path, ffmpeg_path: str | None = None, limit: int = 6) -> dict[str, Any]:
    output_root = root / "resources" / "gameplay"
    poster_root = output_root / "posters"
    clip_root = output_root / "clips"
    poster_root.mkdir(parents=True, exist_ok=True)
    clip_root.mkdir(parents=True, exist_ok=True)

    ffmpeg = _find_ffmpeg(ffmpeg_path)
    videos: list[dict[str, Any]] = []
    posters: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    for folder in sorted([path for path in bili_root.iterdir() if path.is_dir()])[:limit]:
        info = _read_bili_info(folder)
        track = _video_track(folder)
        if not info or not track:
            continue

        title = str(info.get("title") or folder.name)
        safe_id = folder.name
        poster_source = Path(info.get("coverPath") or folder / "image.jpg")
        poster_target = poster_root / f"{safe_id}.jpg"
        if poster_source.exists() and not poster_target.exists():
            shutil.copy2(poster_source, poster_target)
        if poster_target.exists():
            posters.append({"title": title, "path": f"../../resources/gameplay/posters/{poster_target.name}"})

        duration = int(info.get("duration") or 0)
        start = _clip_start_for(safe_id, duration)
        clip_target = clip_root / f"{safe_id}-clip.mp4"
        clip_created = False
        if ffmpeg and not clip_target.exists():
            command = [
                str(ffmpeg),
                "-y",
                "-f",
                "mp4",
                "-skip_initial_bytes",
                "9",
                "-ss",
                str(start),
                "-i",
                str(track),
                "-t",
                "18",
                "-an",
                "-vf",
                "scale=1280:-2",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "30",
                "-movflags",
                "+faststart",
                str(clip_target),
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            clip_created = True
        if clip_target.exists():
            videos.append(
                {
                    "title": title,
                    "path": f"../../resources/gameplay/clips/{clip_target.name}",
                    "mime_type": _mime_for_path(clip_target),
                }
            )

        sources.append(
            {
                "title": title,
                "source_folder": str(folder),
                "video_track": str(track),
                "duration": duration,
                "clip_start": start,
                "clip_created": clip_created or clip_target.exists(),
            }
        )

    manifest = {
        "kind": "gameplay-video",
        "source_root": str(bili_root),
        "ffmpeg_available": bool(ffmpeg),
        "videos": videos,
        "posters": posters,
        "sources": sources,
    }
    output = output_root / "manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_gameplay_manifest(root: Path) -> Path:
    manifest = discover_gameplay_media(root)
    output = root / "resources" / "gameplay" / "manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def read_gameplay_manifest(root: Path) -> dict[str, Any]:
    path = root / "resources" / "gameplay" / "manifest.json"
    if not path.exists():
        return discover_gameplay_media(root)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return json.loads(raw.decode("utf-8"))


def _clip_start_for(safe_id: str, duration: int) -> int:
    preferred_starts = {
        "34661468603": 150,
    }
    if safe_id in preferred_starts:
        return preferred_starts[safe_id]
    return max(8, duration // 3) if duration else 12
