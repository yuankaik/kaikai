from __future__ import annotations

import html
import json
from typing import Any

from engine.rod_system import ROD_LEVELS, rod_status_for_spec


def render_captain_day(
    spec: dict[str, Any],
    media_manifest: dict[str, Any] | None = None,
    mistakes: list[Any] | None = None,
    school_stats: dict[str, int] | None = None,
    school_uploads: list[Any] | None = None,
    school_drafts: list[Any] | None = None,
    practice_history: list[dict[str, Any]] | None = None,
) -> str:
    spec_json = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")
    title = _escape(spec.get("title", "今日出海"))
    day = _escape(spec.get("day", "Day"))
    focus = _escape(spec.get("focus", "今日任务"))
    points = spec.get("points", {})
    fish = spec.get("knowledge_fish", {})
    rod = rod_status_for_spec(spec)
    hero = _hero_media(media_manifest, spec, rod)
    school_stats = school_stats or {"total": 0, "today": 0}
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{
      --ink: #f6f7fb;
      --muted: #aab1c5;
      --panel: rgba(13, 22, 39, .88);
      --panel-strong: rgba(9, 14, 26, .96);
      --line: rgba(255, 255, 255, .13);
      --gold: #ffd166;
      --cyan: #5eead4;
      --blue: #60a5fa;
      --ok: #7ddf96;
      --bad: #ff8a8a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #09111f;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
      letter-spacing: 0;
    }}
    .sea {{
      min-height: 100vh;
      background:
        radial-gradient(circle at 70% 10%, rgba(94, 234, 212, .23), transparent 28%),
        linear-gradient(180deg, #12233d 0%, #09111f 56%, #050814 100%);
    }}
    .shell {{ max-width: 1120px; margin: 0 auto; padding: 28px 20px 48px; }}
    .hero {{
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, .28);
    }}
    .mission {{ padding: 28px; }}
    .eyebrow {{ color: var(--cyan); font-size: 14px; font-weight: 800; margin: 0 0 10px; }}
    h1 {{ margin: 0; font-size: 44px; line-height: 1.08; }}
    .focus {{ margin: 14px 0 0; color: var(--muted); font-size: 18px; line-height: 1.55; }}
    .hero-media {{ overflow: hidden; min-height: 260px; position: relative; }}
    .hero-media img, .hero-media video {{ width: 100%; height: 100%; min-height: 260px; object-fit: cover; display: block; }}
    .hero-media::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, transparent, rgba(5, 8, 20, .35));
      pointer-events: none;
    }}
    .mission-scene {{
      position: relative;
      min-height: 260px;
      height: 100%;
      overflow: hidden;
      isolation: isolate;
      background: #071827;
    }}
    .mission-scene .scene-bg {{
      position: absolute;
      inset: -8%;
      background-image: var(--scene-image);
      background-size: cover;
      background-position: center;
      filter: saturate(1.12) contrast(1.08);
      transform: scale(1.05);
      animation: driftZoom 12s ease-in-out infinite alternate;
      z-index: -3;
    }}
    .mission-scene .scene-video {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      min-height: 260px;
      object-fit: cover;
      z-index: -4;
      filter: saturate(1.08) contrast(1.06);
    }}
    .mission-scene .scene-bg::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, rgba(5, 8, 20, .78), rgba(5, 8, 20, .2) 54%, rgba(5, 8, 20, .68)),
        radial-gradient(circle at 72% 34%, rgba(94, 234, 212, .34), transparent 26%);
    }}
    .mission-scene .scan {{
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent, rgba(94, 234, 212, .3), transparent);
      transform: translateX(-80%);
      animation: scanSweep 3.8s ease-in-out infinite;
      z-index: -1;
    }}
    .mission-scene .wave {{
      position: absolute;
      left: -12%;
      right: -12%;
      bottom: -18px;
      height: 86px;
      background:
        radial-gradient(ellipse at 18% 0%, rgba(96, 165, 250, .54), transparent 56%),
        radial-gradient(ellipse at 52% 12%, rgba(94, 234, 212, .42), transparent 58%),
        radial-gradient(ellipse at 82% 0%, rgba(96, 165, 250, .48), transparent 56%);
      opacity: .9;
      animation: waveFloat 4.6s ease-in-out infinite;
    }}
    .mission-scene .hook {{
      position: absolute;
      top: 18px;
      right: 30px;
      width: 68px;
      height: 116px;
      border-right: 4px solid rgba(255, 255, 255, .78);
      border-bottom: 4px solid rgba(255, 255, 255, .78);
      border-radius: 0 0 38px 0;
      animation: hookDrop 2.8s ease-in-out infinite;
    }}
    .mission-scene .hook::after {{
      content: "";
      position: absolute;
      right: -10px;
      bottom: -12px;
      width: 17px;
      height: 17px;
      border-radius: 50%;
      background: var(--gold);
      box-shadow: 0 0 20px rgba(255, 209, 102, .72);
    }}
    .scene-copy {{
      position: absolute;
      left: 24px;
      right: 24px;
      bottom: 24px;
      display: grid;
      gap: 8px;
      z-index: 2;
    }}
    .scene-copy .boss-line {{ color: var(--cyan); font-size: 14px; font-weight: 900; }}
    .scene-copy h2 {{ margin: 0; font-size: 30px; line-height: 1.08; text-shadow: 0 3px 18px rgba(0,0,0,.46); }}
    .scene-copy p {{ margin: 0; color: rgba(246,247,251,.84); font-size: 15px; line-height: 1.45; }}
    .case-badge {{
      width: fit-content;
      max-width: 100%;
      color: #06111f;
      background: var(--gold);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 13px;
      font-weight: 900;
      box-shadow: 0 8px 24px rgba(0, 0, 0, .26);
    }}
    .status {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 12px;
      margin-bottom: 18px;
    }}
    .stat {{ padding: 18px; }}
    .stat b {{ display: block; font-size: 24px; margin-top: 6px; }}
    .stat span {{ color: var(--muted); font-size: 13px; font-weight: 700; }}
    .stat-button {{
      display: block;
      width: 100%;
      min-height: 100%;
      text-align: left;
      color: var(--ink);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, .28);
    }}
    .stat-button:hover {{ border-color: rgba(94, 234, 212, .55); transform: translateY(-1px); }}
    .stat-button small {{ display: block; color: var(--muted); margin-top: 6px; font-size: 12px; }}
    .history-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .history-card {{
      display: grid;
      gap: 8px;
      padding: 16px;
      color: #0f172a;
      text-decoration: none;
      background: rgba(255, 255, 255, .94);
      border: 1px solid rgba(148, 163, 184, .42);
      border-radius: 8px;
    }}
    .history-card span {{ color: #2563eb; font-weight: 900; }}
    .history-card b {{ font-size: 20px; }}
    .history-card small {{ color: #475569; line-height: 1.45; }}
    .steam-review {{
      position: relative;
      overflow: hidden;
      background:
        linear-gradient(135deg, rgba(28, 74, 132, .96), rgba(12, 18, 33, .98) 56%),
        radial-gradient(circle at 82% 12%, rgba(94, 234, 212, .28), transparent 34%);
      border-color: rgba(96, 165, 250, .46);
    }}
    .steam-review::after {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(110deg, transparent 12%, rgba(255,255,255,.12) 46%, transparent 72%);
      transform: translateX(-120%);
      transition: transform .45s ease;
      pointer-events: none;
    }}
    .steam-review:hover {{
      border-color: rgba(94, 234, 212, .9);
      box-shadow: 0 18px 52px rgba(8, 47, 73, .48), 0 0 0 1px rgba(94, 234, 212, .18) inset;
    }}
    .steam-review:hover::after {{ transform: translateX(120%); }}
    .school-collection {{
      background:
        linear-gradient(135deg, rgba(22, 101, 52, .9), rgba(12, 18, 33, .98) 58%),
        radial-gradient(circle at 78% 18%, rgba(255, 209, 102, .28), transparent 34%);
      border-color: rgba(125, 223, 150, .42);
    }}
    .school-collection:hover {{
      border-color: rgba(255, 209, 102, .86);
      box-shadow: 0 18px 52px rgba(20, 83, 45, .42), 0 0 0 1px rgba(255, 209, 102, .18) inset;
    }}
    .rod-panel {{ padding: 20px; margin-bottom: 18px; display: grid; gap: 14px; }}
    .rod-head {{ display: flex; justify-content: space-between; gap: 14px; align-items: end; }}
    .rod-head h2 {{ margin: 0; font-size: 28px; }}
    .rod-head strong {{ color: var(--gold); font-size: 20px; }}
    .rod-track {{ height: 14px; background: rgba(255,255,255,.12); border-radius: 999px; overflow: hidden; }}
    .rod-track span {{ display: block; height: 100%; width: var(--rod-progress); background: linear-gradient(90deg, var(--cyan), var(--gold)); }}
    .material-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .material {{ color: #06111f; background: rgba(255, 209, 102, .95); border-radius: 999px; padding: 7px 10px; font-size: 13px; font-weight: 850; }}
    .section-title {{ margin: 28px 0 12px; display: flex; justify-content: space-between; gap: 12px; align-items: end; }}
    .section-title h2 {{ margin: 0; font-size: 25px; }}
    .section-title p {{ margin: 0; color: var(--muted); }}
    .questions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(410px, 1fr)); gap: 10px; align-items: start; }}
    .card {{ padding: 16px; display: grid; gap: 10px; }}
    .meta {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .tag {{ color: #06111f; background: var(--cyan); border-radius: 999px; padding: 5px 9px; font-size: 13px; font-weight: 800; }}
    .tag.soft {{ color: var(--ink); background: rgba(255, 255, 255, .12); }}
    .prompt {{ margin: 0; font-size: 20px; line-height: 1.45; }}
    input, textarea {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, .08);
      color: var(--ink);
      padding: 11px 12px;
      font: inherit;
      font-size: 18px;
    }}
    textarea {{ min-height: 86px; resize: vertical; }}
    input:focus, textarea:focus {{ outline: 3px solid rgba(94, 234, 212, .2); border-color: var(--cyan); }}
    .actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    button {{
      border: 0;
      border-radius: 8px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 850;
      color: #06111f;
      background: var(--gold);
      cursor: pointer;
    }}
    button.secondary {{ background: rgba(255, 255, 255, .12); color: var(--ink); border: 1px solid var(--line); }}
    button:disabled {{ opacity: .55; cursor: not-allowed; }}
    .feedback {{ margin: 0; min-height: 24px; font-weight: 800; }}
    .feedback.ok {{ color: var(--ok); }}
    .feedback.review {{ color: var(--gold); }}
    .feedback.bad {{ color: var(--bad); }}
    .finish {{ padding: 22px; margin-top: 22px; display: grid; gap: 14px; }}
    .voice-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .voice-card {{ padding: 18px; background: var(--panel-strong); border-radius: 8px; border: 1px solid var(--line); }}
    .voice-card h3 {{ margin: 0 0 8px; }}
    .tiny {{ color: var(--muted); font-size: 14px; line-height: 1.5; }}
    .toast {{ color: var(--cyan); min-height: 22px; font-weight: 800; }}
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 22px;
      background: rgba(2, 6, 23, .72);
      z-index: 20;
    }}
    .modal-backdrop.open {{ display: flex; }}
    .modal {{
      width: min(1280px, 96vw);
      max-height: min(820px, 90vh);
      overflow: auto;
      padding: 22px;
      background: rgba(9, 14, 26, .98);
      border: 1px solid rgba(255, 255, 255, .16);
      border-radius: 8px;
      box-shadow: 0 24px 80px rgba(0, 0, 0, .5);
    }}
    .modal-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 18px; }}
    .modal-head h2 {{ margin: 0; font-size: 28px; }}
    .modal-close {{ padding: 9px 12px; color: var(--ink); background: rgba(255,255,255,.12); border: 1px solid var(--line); }}
    .skill-map {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
    .skill-node {{ padding: 14px; border-radius: 8px; background: rgba(255,255,255,.08); border: 1px solid var(--line); }}
    .skill-node b {{ display: block; margin-bottom: 6px; }}
    .skill-node.done {{ border-color: rgba(125, 223, 150, .7); }}
    .skill-node.active {{ border-color: rgba(255, 209, 102, .75); }}
    .jar-stage {{ position: relative; min-height: 280px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: center; }}
    .coin-jar {{ position: relative; width: 180px; height: 250px; margin: 0 auto; border: 5px solid rgba(255,255,255,.7); border-top-width: 12px; border-radius: 18px 18px 34px 34px; overflow: hidden; background: rgba(255,255,255,.08); }}
    .coin-fill {{ position: absolute; left: 0; right: 0; bottom: 0; height: var(--coin-fill); background: linear-gradient(180deg, rgba(255, 209, 102, .52), rgba(255, 159, 10, .9)); }}
    .coin {{ position: absolute; top: -34px; width: 24px; height: 24px; border-radius: 50%; background: var(--gold); box-shadow: inset -3px -4px 0 rgba(0,0,0,.15); animation: coinDrop 2.4s linear infinite; }}
    .coin.c1 {{ left: 34px; animation-delay: 0s; }}
    .coin.c2 {{ left: 82px; animation-delay: .65s; }}
    .coin.c3 {{ left: 126px; animation-delay: 1.2s; }}
    .mate-award {{
      grid-column: 1 / -1;
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 8px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255, 209, 102, .32);
    }}
    .mate-award h3 {{ margin: 0; font-size: 20px; }}
    .mate-award-grid {{ display: grid; grid-template-columns: 120px 1fr auto; gap: 10px; align-items: center; }}
    .mate-award-status {{ min-height: 22px; color: var(--cyan); font-weight: 850; }}
    .rod-wall {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }}
    .wall-slot {{ min-height: 132px; padding: 12px; border-radius: 8px; background: rgba(255,255,255,.07); border: 1px dashed rgba(255,255,255,.2); display: grid; align-content: end; gap: 8px; }}
    .wall-slot.hung {{ border-style: solid; border-color: rgba(94, 234, 212, .6); background: rgba(94, 234, 212, .12); }}
    .rod-icon {{ height: 58px; border-left: 6px solid var(--gold); transform: rotate(18deg); transform-origin: bottom; margin: 0 auto; border-radius: 999px; }}
    .school-upload {{
      margin-top: 14px;
      display: grid;
      gap: 12px;
      padding: 16px;
      border-radius: 8px;
      background: rgba(255, 255, 255, .08);
      border: 1px solid rgba(94, 234, 212, .26);
    }}
    .school-upload h3 {{ margin: 0; font-size: 20px; }}
    .school-upload input[type="file"] {{ background: rgba(255,255,255,.06); font-size: 15px; }}
    .school-upload-status {{ min-height: 22px; color: var(--cyan); font-weight: 850; }}
    .school-queue {{
      display: grid;
      gap: 10px;
      padding: 14px;
      border-radius: 8px;
      background: #fff;
      border: 1px solid #e5e7eb;
    }}
    .school-queue h3 {{ margin: 0; color: #0f172a; font-size: 18px; }}
    .school-queue-card {{
      display: grid;
      gap: 4px;
      padding: 10px 12px;
      border-radius: 8px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
    }}
    .school-queue-card b {{ color: #0f172a; }}
    .school-queue-card span {{ color: #2563eb; font-size: 13px; font-weight: 850; }}
    .school-queue-card p {{ margin: 0; color: #475569; line-height: 1.45; }}
    .school-vault {{
      display: grid;
      gap: 14px;
      color: #111827;
      background: #f7f8fb;
      border-radius: 8px;
      padding: 16px;
    }}
    .vault-top {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .vault-number {{
      padding: 16px;
      border-radius: 8px;
      background: #fff;
      border: 1px solid #e5e7eb;
      box-shadow: 0 10px 28px rgba(15, 23, 42, .07);
    }}
    .vault-number span {{ display: block; color: #6b7280; font-size: 13px; font-weight: 800; }}
    .vault-number b {{ display: block; color: #111827; font-size: 34px; margin-top: 5px; }}
    .vault-tank {{
      position: relative;
      min-height: 190px;
      overflow: hidden;
      border-radius: 8px;
      background: linear-gradient(180deg, #e0f2fe, #f8fafc);
      border: 1px solid #bae6fd;
    }}
    .vault-fill {{
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: var(--school-fill);
      background: linear-gradient(180deg, rgba(94, 234, 212, .46), rgba(34, 197, 94, .7));
      transition: height .4s ease;
    }}
    .vault-card {{
      position: absolute;
      width: 48px;
      height: 34px;
      border-radius: 6px;
      background: #fff;
      border: 2px solid #38bdf8;
      box-shadow: 0 10px 20px rgba(15, 23, 42, .12);
      animation: paperFloat 3.2s ease-in-out infinite alternate;
    }}
    .vault-card.c1 {{ left: 18%; bottom: 18%; transform: rotate(-8deg); }}
    .vault-card.c2 {{ left: 46%; bottom: 38%; animation-delay: .45s; transform: rotate(7deg); }}
    .vault-card.c3 {{ right: 16%; bottom: 26%; animation-delay: .9s; transform: rotate(-3deg); }}
    .vault-copy {{ position: relative; padding: 16px; z-index: 1; }}
    .vault-copy h3 {{ margin: 0 0 6px; color: #0f172a; font-size: 22px; }}
    .vault-copy p {{ margin: 0; color: #475569; line-height: 1.5; }}
    .lamp-road {{ position: relative; display: grid; grid-template-columns: repeat(10, 1fr); gap: 12px; padding: 22px 0 8px; }}
    .lamp {{ display: grid; justify-items: center; gap: 8px; color: var(--muted); font-size: 12px; }}
    .lamp::before {{ content: ""; width: 14px; height: 42px; border-radius: 999px 999px 0 0; background: rgba(255,255,255,.18); box-shadow: none; }}
    .lamp.on::before {{ background: var(--gold); box-shadow: 0 0 18px rgba(255, 209, 102, .85); animation: lampGlow 1.8s ease-in-out infinite alternate; }}
    .mistake-review {{
      display: grid;
      gap: 12px;
      color: #111827;
      background: #f7f8fb;
      border-radius: 8px;
      padding: 14px;
    }}
    .mistake-summary {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      color: #4b5563;
      padding: 8px 4px 14px;
      border-bottom: 1px solid #e5e7eb;
    }}
    .mistake-summary b {{ color: #111827; font-size: 24px; }}
    .mistake-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .mistake-tab {{
      color: #334155;
      background: #eef2f7;
      border: 1px solid #dbe2ea;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 14px;
    }}
    .mistake-tab.active {{
      color: #0f172a;
      background: #fff;
      border-color: #93c5fd;
      box-shadow: 0 8px 22px rgba(59, 130, 246, .14);
    }}
    .mistake-sheet {{ display: none; gap: 12px; }}
    .mistake-sheet.active {{ display: grid; }}
    .mistake-table-wrap {{
      overflow-x: auto;
      border: 1px solid #dbe2ea;
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 12px 34px rgba(15, 23, 42, .08);
    }}
    .mistake-table {{
      width: 100%;
      min-width: 1120px;
      table-layout: fixed;
      border-collapse: separate;
      border-spacing: 0;
      font-size: 13px;
    }}
    .mistake-table th {{
      position: sticky;
      top: 0;
      z-index: 1;
      text-align: left;
      color: #475569;
      background: #f8fafc;
      border-bottom: 1px solid #dbe2ea;
      padding: 9px 10px;
      font-weight: 900;
      white-space: nowrap;
    }}
    .mistake-table td {{
      vertical-align: top;
      color: #1f2937;
      background: #fff;
      border-bottom: 1px solid #edf2f7;
      padding: 9px 10px;
      line-height: 1.35;
      word-break: break-word;
    }}
    .mistake-table tr:nth-child(even) td {{ background: #fbfcfe; }}
    .mistake-table tr.boss td {{ background: #f3f8ff; }}
    .mistake-table tr:last-child td {{ border-bottom: 0; }}
    .mistake-id {{ font-weight: 950; color: #0f172a; white-space: nowrap; }}
    .mistake-badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 8px;
      color: #075985;
      background: #e0f2fe;
      font-size: 12px;
      font-weight: 900;
      white-space: nowrap;
    }}
    .mistake-table tr.boss .mistake-badge {{ color: #1d4ed8; background: #dbeafe; }}
    .mistake-topic {{ font-weight: 850; color: #111827; }}
    .mistake-question {{ color: #111827; }}
    .mistake-answer {{ color: #1f2937; }}
    .mistake-note-cell {{ color: #4b5563; }}
    .mistake-action {{ color: #334155; }}
    .rematch-button {{
      color: #0f172a;
      background: #fbbf24;
      border: 1px solid rgba(217, 119, 6, .35);
      padding: 7px 9px;
      font-size: 13px;
      white-space: nowrap;
    }}
    .rematch-panel {{
      margin-top: 12px;
      display: none;
      gap: 10px;
      padding: 14px;
      color: #111827;
      background: #fff;
      border: 1px solid #dbe2ea;
      border-radius: 8px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, .07);
    }}
    .rematch-panel.open {{ display: grid; }}
    .rematch-panel h3 {{ margin: 0; font-size: 18px; }}
    .rematch-line {{ margin: 0; color: #475569; line-height: 1.5; }}
    .rematch-panel input {{ color: #111827; background: #f8fafc; border-color: #dbe2ea; }}
    .rematch-status {{ min-height: 22px; color: #166534; font-weight: 900; }}
    .mistake-empty {{ margin: 0; padding: 16px; color: #4b5563; }}
    .instant-report {{
      display: none;
      margin-top: 18px;
      padding: 18px;
      color: #111827;
      background: #f7f8fb;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, .2);
    }}
    .instant-report.open {{ display: grid; gap: 14px; }}
    .report-head {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #e5e7eb;
    }}
    .report-head h2 {{ margin: 0; color: #111827; font-size: 26px; }}
    .report-score {{ color: #0f172a; font-size: 30px; font-weight: 950; }}
    .report-grid {{ display: grid; gap: 10px; }}
    .report-card {{
      display: grid;
      gap: 8px;
      padding: 14px;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-left: 5px solid #94a3b8;
      border-radius: 8px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, .07);
    }}
    .report-card.ok {{ border-left-color: #22c55e; }}
    .report-card.review {{ border-left-color: #f59e0b; }}
    .report-card.bad {{ border-left-color: #ef4444; }}
    .report-title {{ display: flex; justify-content: space-between; gap: 10px; color: #111827; font-weight: 950; }}
    .report-card p {{ margin: 0; color: #4b5563; line-height: 1.5; }}
    .report-next {{ color: #0f172a; background: #eef6ff; border-radius: 8px; padding: 10px; }}
    .voice-explain {{
      width: fit-content;
      color: #f8fafc;
      background: #2563eb;
      border: 1px solid rgba(37, 99, 235, .35);
      padding: 7px 9px;
      font-size: 13px;
      white-space: nowrap;
    }}
    @media (max-width: 820px) {{
      .hero, .status, .voice-grid, .questions {{ grid-template-columns: 1fr; }}
      .mistake-row {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 34px; }}
      .prompt {{ font-size: 20px; }}
    }}
    @keyframes driftZoom {{
      from {{ transform: scale(1.05) translate3d(-6px, -4px, 0); }}
      to {{ transform: scale(1.13) translate3d(8px, 5px, 0); }}
    }}
    @keyframes scanSweep {{
      0% {{ transform: translateX(-85%); opacity: 0; }}
      18% {{ opacity: .85; }}
      60% {{ opacity: .65; }}
      100% {{ transform: translateX(85%); opacity: 0; }}
    }}
    @keyframes waveFloat {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-9px); }}
    }}
    @keyframes hookDrop {{
      0%, 100% {{ transform: translateY(-4px) rotate(-2deg); }}
      50% {{ transform: translateY(8px) rotate(2deg); }}
    }}
    @keyframes coinDrop {{
      0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
      12% {{ opacity: 1; }}
      100% {{ transform: translateY(260px) rotate(420deg); opacity: .95; }}
    }}
    @keyframes lampGlow {{
      from {{ filter: brightness(1); }}
      to {{ filter: brightness(1.35); }}
    }}
    @keyframes paperFloat {{
      from {{ translate: 0 0; }}
      to {{ translate: 0 -12px; }}
    }}
  </style>
</head>
<body>
  <div class="sea">
    <div class="shell">
      <header class="hero">
        <section class="panel mission">
          <p class="eyebrow">{day} 今日海域</p>
          <h1>{title}</h1>
          <p class="focus">{focus}</p>
        </section>
        <aside class="panel hero-media">{hero}</aside>
      </header>
      <section class="status">
        <button type="button" class="stat stat-button" data-open-modal="coin"><span>Switch2 渔币</span><b><span data-current-points>{_escape(points.get("current", 0))}</span>/{_escape(points.get("goal", 3500))}</b><small>看看鱼币罐</small></button>
        <button type="button" class="stat stat-button" data-open-modal="skills"><span>知识鱼图鉴</span><b>{_escape(fish.get("current", 0))}/{_escape(fish.get("goal", 93))}</b><small>打开技能地图</small></button>
        <button type="button" class="stat stat-button" data-open-modal="rods"><span>当前鱼竿</span><b>{_escape(rod["current"].name)} Lv.{_escape(rod["current"].level)}</b><small>看看鱼竿墙</small></button>
        <button type="button" class="stat stat-button school-collection" data-open-modal="school"><span>学校错题收集</span><b><span data-school-count>{_escape(school_stats.get("total", 0))}</span> 张</b><small>上传试卷作业</small></button>
        <button type="button" class="stat stat-button steam-review" data-open-modal="mistakes"><span>错误回顾</span><b>Boss 雷达</b><small>看清失误，下一网更准</small></button>
        <button type="button" class="stat stat-button" data-open-modal="history"><span>往日练习</span><b>Day 记录</b><small>打开以前的出海任务</small></button>
      </section>
      {_rod_panel(rod)}
      {_growth_modals(spec, points, fish, rod, mistakes or _fallback_mistakes(), school_stats, school_uploads or [], school_drafts or [], practice_history or [])}
      <main>
        {_question_sections(spec)}
        <section class="panel finish">
          <h2>船长复盘</h2>
          <p class="tiny">可以说 20-30 秒：今天哪一题像 Boss？哪里突然想明白了？</p>
          <div class="voice-grid">
            <div class="voice-card">
              <h3>今日课堂</h3>
              <p class="tiny">说一说今天语数外上到哪里。</p>
              <div class="actions">
                <button type="button" data-voice-start="classroom">开始说话</button>
                <button type="button" class="secondary" data-voice-stop="classroom" disabled>结束并上传</button>
              </div>
              <p class="toast" data-voice-status="classroom"></p>
            </div>
            <div class="voice-card">
              <h3>Boss 讲给我听</h3>
              <p class="tiny">用自己的话讲今天最重要的知识点。</p>
              <div class="actions">
                <button type="button" data-voice-start="boss">开始说话</button>
                <button type="button" class="secondary" data-voice-stop="boss" disabled>结束并上传</button>
              </div>
              <p class="toast" data-voice-status="boss"></p>
            </div>
          </div>
          <label>今天的感觉
            <textarea data-self-check="feeling" placeholder="例如：今天有点累，但 Boss 被我抓住了。"></textarea>
          </label>
          <button type="button" id="submitResult">完成今日出海</button>
          <p class="toast" id="submitStatus"></p>
          <section class="instant-report" id="instantReport" aria-live="polite"></section>
        </section>
      </main>
    </div>
  </div>
  <script type="application/json" id="practice-spec">{spec_json}</script>
  <script>
    const spec = JSON.parse(document.getElementById('practice-spec').textContent);
    const storageKey = 'yuanjiale-local-app-' + spec.day;
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{{}}');

    document.querySelectorAll('[data-open-modal]').forEach((button) => {{
      button.addEventListener('click', () => {{
        const modal = document.querySelector(`[data-modal="${{button.dataset.openModal}}"]`);
        if (modal) {{
          modal.classList.add('open');
          modal.setAttribute('aria-hidden', 'false');
        }}
      }});
    }});
    document.querySelectorAll('[data-modal]').forEach((modal) => {{
      modal.addEventListener('click', (event) => {{
        if (event.target === modal || event.target.matches('[data-close-modal]')) {{
          modal.classList.remove('open');
          modal.setAttribute('aria-hidden', 'true');
        }}
      }});
    }});
    window.addEventListener('keydown', (event) => {{
      if (event.key === 'Escape') {{
        document.querySelectorAll('[data-modal].open').forEach((modal) => {{
          modal.classList.remove('open');
          modal.setAttribute('aria-hidden', 'true');
        }});
      }}
    }});

    function normalize(value) {{
      return String(value || '').replace(/\\s+/g, '').replace(/[，,。.;；]/g, '').toLowerCase();
    }}

    function allQuestions() {{
      return (spec.sections || []).flatMap(section => section.questions || []);
    }}

    function numbersIn(value) {{
      return String(value || '').match(/\\d+(?:\\.\\d+)?/g) || [];
    }}

    function numbersMatch(value, expected) {{
      const left = numbersIn(value);
      const right = numbersIn(expected);
      return right.length > 0 && right.every((number) => left.includes(number));
    }}

    function feedbackFor(question, value) {{
      const answer = String(value || '').trim();
      const expected = String(question.answer || '');
      const id = String(question.id || '');
      const knowledge = String(question.knowledge || '这个知识点');
      const isOpen = expected.includes('开放题');
      const bossWords = ['两次', '2次', '不同', '不能', '不可以', '分'];
      const semanticBoss = knowledge.includes('费曼') && bossWords.some(word => answer.includes(word));

      if (!answer) {{
        return {{
          id,
          knowledge,
          state: 'bad',
          label: '未完成',
          points: 0,
          reason: '这题还没有下笔，先算作逃脱鱼。',
          caution: '遇到 Boss 题，哪怕不会，也先写“我卡在……”这句话。',
          next: variationFor(question)
        }};
      }}
      if (isOpen) {{
        return {{
          id,
          knowledge,
          state: answer.length >= 4 ? 'review' : 'bad',
          label: answer.length >= 4 ? '已完成，待大副精批' : '表达太短',
          points: answer.length >= 4 ? 12 : 4,
          reason: answer.length >= 4 ? '开放题先看完成度，稍后我会结合语音和课堂内容精批。' : '开放题需要写出完整词句。',
          caution: '语文英语开放题要尽量写成一句完整的话。',
          next: answer.length >= 4 ? '加分：完成课堂雷达。下一步看表达是否更准确。' : variationFor(question)
        }};
      }}
      const completeness = completenessFor(question, answer, expected);
      if (!completeness.ok) {{
        return {{
          id,
          knowledge,
          state: 'review',
          label: '差一点，先补完整',
          points: 8,
          reason: completeness.message,
          caution: '一题里有两个空或两个问时，先逐个打勾：第一问、第二问、单位。',
          next: variationFor(question)
        }};
      }}
      if (normalize(answer) === normalize(expected) || numbersMatch(answer, expected) || semanticBoss) {{
        const unitWarning = numbersMatch(answer, expected) && normalize(answer) !== normalize(expected);
        return {{
          id,
          knowledge,
          state: unitWarning ? 'review' : 'ok',
          label: unitWarning ? '核心正确，单位要补齐' : '命中',
          points: unitWarning ? 16 : 20,
          reason: unitWarning ? `关键数字对了，标准答案是：${{expected}}。` : '答案命中，说明这个知识点正在变稳。',
          caution: unitWarning ? '以后最后一步要把单位和答句补完整。' : '保持先看题意、再下笔的节奏。',
          next: unitWarning ? variationFor(question) : `奖励：获得“${{question.unlock_reward || knowledge}}”。`
        }};
      }}
      return {{
        id,
        knowledge,
        state: 'bad',
        label: '需要回炉',
        points: 4,
        reason: `船长答案：${{answer}}；正确方向：${{expected}}。`,
        caution: cautionFor(question),
        next: variationFor(question)
      }};
    }}

    function completenessFor(question, answer, expected) {{
      const prompt = String(question.prompt || '');
      const blankCount = (prompt.match(/____/g) || []).length;
      const numberCount = numbersIn(answer).length;
      if (blankCount >= 2 && numberCount < blankCount) {{
        return {{ ok: false, message: `这题有 ${{blankCount}} 个空，已经看到 ${{numberCount}} 个数字。第一空、第二空都要填。` }};
      }}
      const judgementWords = ['不能', '不可以', '可以', '能'];
      if ((prompt.includes('能不能') || expected.includes('不能') || expected.includes('不可以')) && !judgementWords.some(word => answer.includes(word))) {{
        return {{ ok: false, message: '计算后还有一个判断题：能不能这样写？别忘了回答“能/不能”。' }};
      }}
      const unitWords = ['ml', '毫升', '瓶'];
      if ((expected.includes('ml') || expected.includes('瓶')) && numberCount >= numbersIn(expected).length && !unitWords.some(word => answer.includes(word))) {{
        return {{ ok: true, message: '数字对了，但单位要补。' }};
      }}
      return {{ ok: true, message: '' }};
    }}

    function cautionFor(question) {{
      const id = String(question.id || '');
      const knowledge = String(question.knowledge || '');
      if (id === 'D4-B2') return '先分别算两次除法，再相加；不能看到同一个被除数就把除数合并。';
      if (knowledge.includes('费曼')) return '费曼题要讲“为什么”，固定口令：这是两次分，除数不能合并。';
      if (knowledge.includes('容量')) return '容量题先统一单位，再做除法，最后补单位。';
      if (knowledge.includes('退位')) return '退位减法先借位，再检查个位。';
      return '先把题目关系说出来，再写算式。';
    }}

    function variationFor(question) {{
      const id = String(question.id || '');
      if (id === 'D4-B2') return '变化题：360÷6 + 360÷4 = ____，能不能写成360÷10？';
      if (String(question.knowledge || '').includes('费曼')) return '变化题：用一句话解释，300÷5 + 300÷10 为什么不能写成300÷15。';
      if (id === 'D4-V1') return '变化题：3升600ml，每瓶300ml，可以装满几瓶？';
      if (id === 'D4-R1') return '变化题：720÷9 + 420÷7 = ____。';
      if (id === 'D4-R2') return '变化题：72 - 38 = ____。';
      return '变化题：把这题换一组数字，再试一次。';
    }}

    function normalizedPoints(item) {{
      if (item.state === 'ok') return 2;
      if (item.state === 'review') return 1;
      return 0;
    }}

    function solutionStepsFor(question, item) {{
      const knowledge = String(question.knowledge || '');
      const prompt = String(question.prompt || '');
      const expected = String(question.answer || item.expected || '');
      const text = `${{knowledge}} ${{prompt}} ${{expected}}`;
      if (text.includes('480') || text.includes('除数') || text.includes('除法陷阱')) {{
        return '解题步骤：先分别算每一道除法；再把两个结果相加；最后判断，除数不能合并。';
      }}
      if (text.includes('括号') || text.includes('混合运算')) {{
        return '解题步骤：先算小括号，再算中括号；乘除优先；最后一步再写答案。';
      }}
      if (text.includes('小数')) {{
        return '解题步骤：先写清位值关系；小数点对齐；最后检查结果有没有超过或少算一位。';
      }}
      if (text.includes('容量') || text.includes('ml') || text.includes('升')) {{
        return '解题步骤：先统一单位；再列除法或乘法；最后把单位和答句补完整。';
      }}
      if (text.includes('三单') || text.includes('he') || text.includes('she') || text.includes('it')) {{
        return '解题步骤：先找主语；如果是 he、she、it 或单个人名，动词要加 s 或 es。';
      }}
      if (text.includes('进行时') || text.includes('V-ing')) {{
        return '解题步骤：先找 be 动词；再把动作改成 V-ing；最后读一遍句子是否通顺。';
      }}
      if (text.includes('概括')) {{
        return '解题步骤：先圈人物或对象；再圈发生了什么；最后压缩成一句完整的话。';
      }}
      if (text.includes('修辞') || text.includes('拟人') || text.includes('比喻')) {{
        return '解题步骤：先问像不像另一种东西，再问有没有人的动作；像是比喻，会做人动作是拟人。';
      }}
      return '解题步骤：先把题目关系说清楚；再列式或写句子；最后检查答案、单位和答句。';
    }}

    function enrichFeedback(question, item, value) {{
      const expected = String(question.answer || item.expected || '');
      const prompt = String(question.prompt || '');
      item.prompt = prompt || '这题没有记录到原题，请大副补录后再回看。';
      item.student_answer = String(value || '').trim() || '未作答';
      item.expected = expected || '待大副核对';
      item.steps = solutionStepsFor(question, item);
      item.points = normalizedPoints(item);
      return item;
    }}

    function buildFeedbackReport() {{
      const items = allQuestions().map((question) => {{
        const input = document.querySelector(`[data-answer-for="${{question.id}}"]`);
        const value = input ? input.value : '';
        return enrichFeedback(question, feedbackFor(question, value), value);
      }});
      const base = 15;
      const perfectBonus = items.every(item => item.state === 'ok') ? 10 : 0;
      const points = base + items.reduce((sum, item) => sum + item.points, 0);
      return {{
        items,
        points: points + perfectBonus,
        correct: items.filter(item => item.state === 'ok').length,
        review: items.filter(item => item.state === 'review').length,
        wrong: items.filter(item => item.state === 'bad').length
      }};
    }}

    function renderFeedbackReport(report) {{
      const target = document.getElementById('instantReport');
      const cards = report.items.map((item) => `
        <article class="report-card ${{item.state}}">
          <div class="report-title">
            <span>${{item.id}} · ${{item.knowledge}}</span>
            <span>${{item.label}} +${{item.points}}</span>
          </div>
          <p><b>错题原题：</b>${{item.prompt}}</p>
          <p><b>船长答案：</b>${{item.student_answer}}</p>
          <p><b>正确方向：</b>${{item.expected}}</p>
          <p>${{item.reason}}</p>
          <p><b>具体解法：</b>${{item.steps}}</p>
          <p><b>注意：</b>${{item.caution}}</p>
          <div class="report-next">${{item.next}}</div>
          ${{item.state === 'ok' ? '' : `<button type="button" class="voice-explain" data-speak="${{escapeAttr(speechTextFor(item))}}">听讲解</button>`}}
        </article>
      `).join('');
      target.innerHTML = `
        <div class="report-head">
          <div>
            <h2>今日即时反馈报告</h2>
            <p>命中 ${{report.correct}} 题，待精批 ${{report.review}} 题，需要回炉 ${{report.wrong}} 题。</p>
          </div>
          <div class="report-score">+${{report.points}} 渔币</div>
        </div>
        <div class="report-grid">${{cards}}</div>
      `;
      target.classList.add('open');
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function speechTextFor(item) {{
      return `${{item.id}}。原题：${{item.prompt}}。正确方向：${{item.expected}}。${{item.steps}} 下一步：${{item.next}}`;
    }}

    function escapeAttr(value) {{
      return String(value || '')
        .replaceAll('&', '&amp;')
        .replaceAll('"', '&quot;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');
    }}

    function speak(text) {{
      if (!('speechSynthesis' in window)) {{
        alert('当前浏览器暂不支持语音朗读。');
        return;
      }}
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance.rate = 0.92;
      utterance.pitch = 1;
      const voice = window.speechSynthesis.getVoices().find(item => item.lang && item.lang.toLowerCase().startsWith('zh'));
      if (voice) utterance.voice = voice;
      window.speechSynthesis.speak(utterance);
    }}

    document.addEventListener('click', (event) => {{
      const button = event.target.closest('[data-speak]');
      if (button) speak(button.dataset.speak);
    }});

    document.addEventListener('click', (event) => {{
      const tab = event.target.closest('[data-mistake-tab]');
      if (!tab) return;
      const subject = tab.dataset.mistakeTab;
      document.querySelectorAll('[data-mistake-tab]').forEach(item => {{
        item.classList.toggle('active', item.dataset.mistakeTab === subject);
      }});
      document.querySelectorAll('[data-mistake-sheet]').forEach(sheet => {{
        sheet.classList.toggle('active', sheet.dataset.mistakeSheet === subject);
      }});
    }});

    let activeRematch = null;
    document.addEventListener('click', (event) => {{
      const button = event.target.closest('[data-rematch-trigger]');
      if (!button) return;
      activeRematch = {{
        id: button.dataset.rematchId,
        question: button.dataset.rematchQuestion,
        answer: button.dataset.rematchAnswer
      }};
      const panel = document.querySelector('[data-rematch-panel]');
      panel.classList.add('open');
      document.querySelector('[data-rematch-question-text]').textContent = activeRematch.question;
      document.querySelector('[data-rematch-answer]').value = '';
      document.querySelector('[data-rematch-status]').textContent = '答对这道变式题，立即 +1 积分。';
      panel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }});

    document.addEventListener('click', (event) => {{
      if (!event.target.matches('[data-check-rematch]')) return;
      const status = document.querySelector('[data-rematch-status]');
      const input = document.querySelector('[data-rematch-answer]');
      if (!activeRematch) {{
        status.textContent = '先点一行错题的“变换题型再战一次”。';
        return;
      }}
      if (!input.value.trim()) {{
        status.textContent = '先写下再战答案。';
        return;
      }}
      if (activeRematch.answer.includes('开放题') || normalize(input.value) === normalize(activeRematch.answer) || numbersMatch(input.value, activeRematch.answer)) {{
        const key = `rematch:${{activeRematch.id}}`;
        const already = Boolean(saved[key]);
        saved[key] = true;
        save();
        status.textContent = already ? '这道再战已经成功过，积分不重复加。' : '再战成功，+1 积分。这个错题正在被你拆掉。';
      }} else {{
        status.textContent = `还差一点。正确方向：${{activeRematch.answer}}。听讲解后再试一次。`;
      }}
    }});

    document.addEventListener('click', async (event) => {{
      if (!event.target.matches('[data-mate-award]')) return;
      const pointsInput = document.querySelector('[data-mate-points]');
      const reasonInput = document.querySelector('[data-mate-reason]');
      const passwordInput = document.querySelector('[data-mate-password]');
      const status = document.querySelector('[data-mate-award-status]');
      const delta = parseInt(pointsInput.value, 10);
      const reason = reasonInput.value.trim();
      const password = passwordInput.value.trim();
      if (!Number.isInteger(delta) || delta <= 0) {{
        status.textContent = '请填写正整数分数。';
        return;
      }}
      if (!reason) {{
        status.textContent = '请写一句加分理由，后台要留记录。';
        return;
      }}
      if (password !== '1234') {{
        status.textContent = '请输入正确的大副密码。';
        return;
      }}
      status.textContent = '正在记录大副加分...';
      try {{
        const response = await fetch('/api/points/manual', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ delta, reason, password }})
        }});
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || '加分失败');
        document.querySelectorAll('[data-current-points]').forEach(node => {{
          node.textContent = String(data.current);
        }});
        pointsInput.value = '';
        reasonInput.value = '';
        passwordInput.value = '';
        status.textContent = `已加 ${{data.delta}} 分，当前鱼币 ${{data.current}}。理由已进入后台流水。`;
      }} catch (error) {{
        status.textContent = `没有记录成功：${{error.message}}`;
      }}
    }});

    function save() {{
      localStorage.setItem(storageKey, JSON.stringify(saved));
    }}

    document.querySelectorAll('[data-answer-for]').forEach((input) => {{
      const id = input.dataset.answerFor;
      input.value = saved['answer:' + id] || '';
      input.addEventListener('input', () => {{
        saved['answer:' + id] = input.value;
        save();
      }});
    }});

    document.querySelectorAll('[data-check]').forEach((button) => {{
      button.addEventListener('click', () => {{
        const id = button.dataset.check;
        const input = document.querySelector(`[data-answer-for="${{id}}"]`);
        const feedback = document.querySelector(`[data-feedback-for="${{id}}"]`);
        const question = allQuestions().find(item => item.id === id) || {{ id, answer: button.dataset.expected || '' }};
        const value = input.value;
        const result = feedbackFor(question, value);
        saved['checked:' + id] = true;
        feedback.textContent = `${{result.label}}：${{result.reason}}`;
        feedback.className = `feedback ${{result.state === 'bad' ? 'bad' : result.state}}`;
        save();
      }});
    }});

    document.querySelectorAll('[data-self-check]').forEach((input) => {{
      const id = input.dataset.selfCheck;
      input.value = saved['self:' + id] || '';
      input.addEventListener('input', () => {{
        saved['self:' + id] = input.value;
        save();
      }});
    }});

    function buildResult(report) {{
      const answers = {{}};
      document.querySelectorAll('[data-answer-for]').forEach((input) => {{
        const id = input.dataset.answerFor;
        answers[id] = {{
          answer: input.value,
          checked: Boolean(saved['checked:' + id])
        }};
      }});
      const self_check = {{}};
      document.querySelectorAll('[data-self-check]').forEach((input) => {{
        self_check[input.dataset.selfCheck] = input.value;
      }});
      return {{
        day: spec.day,
        title: spec.title,
        completed_at: new Date().toISOString(),
        answers,
        self_check,
        feedback_report: report,
        source: 'local-tutor-web-app'
      }};
    }}

    async function submitResult() {{
      const status = document.getElementById('submitStatus');
      const report = buildFeedbackReport();
      renderFeedbackReport(report);
      status.textContent = '反馈报告已生成，正在保存今日出海...';
      try {{
        const response = await fetch('/api/result', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(buildResult(report))
        }});
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        if (data.points && Number.isInteger(data.points.current)) {{
          document.querySelectorAll('[data-current-points]').forEach(node => {{
            node.textContent = String(data.points.current);
          }});
        }}
        let nextText = '';
        try {{
          const nextResponse = await fetch('/api/next-day', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ completed_day: spec.day, result_id: data.id }})
          }});
          const nextData = await nextResponse.json();
          if (nextResponse.ok && nextData.ok) {{
            nextText = ` 下一日练习已准备：${{nextData.day}}。固定入口 /captain/today 会自动打开最新练习。`;
          }}
        }} catch (nextError) {{
          nextText = ' 下一日练习暂未自动生成，大副稍后再处理。';
        }}
        const settledDelta = data.points ? data.points.delta : report.points;
        const repeatText = data.points && data.points.already_settled ? '这一天的奖励之前已入账，本次不重复加分。' : `本次即时奖励 +${{settledDelta}} 渔币。`;
        status.textContent = `已保存，第 ${{data.id}} 次出海记录。${{repeatText}}${{nextText}}`;
      }} catch (error) {{
        status.textContent = '反馈报告已生成；本地服务没有响应，答案仍已保存在浏览器。';
      }}
    }}
    document.getElementById('submitResult').addEventListener('click', submitResult);

    document.querySelectorAll('[data-upload-school-mistakes]').forEach((button) => {{
      button.addEventListener('click', async () => {{
        const input = document.querySelector('[data-school-mistake-files]');
        const status = document.querySelector('[data-school-mistake-status]');
        const files = Array.from(input?.files || []);
        if (!files.length) {{
          status.textContent = '先选择学校作业或试卷照片。';
          return;
        }}
        status.textContent = `正在收藏 ${{files.length}} 张学校错题...`;
        let okCount = 0;
        for (const file of files) {{
          try {{
            const response = await fetch(`/api/school-mistake?day=${{encodeURIComponent(spec.day)}}&name=${{encodeURIComponent(file.name)}}`, {{
              method: 'POST',
              headers: {{ 'Content-Type': file.type || 'application/octet-stream' }},
              body: file
            }});
            if (!response.ok) throw new Error(await response.text());
            okCount += 1;
          }} catch (error) {{
            status.textContent = `已收藏 ${{okCount}} 张；${{file.name}} 上传失败，请稍后再试。`;
            return;
          }}
        }}
        const totalNode = document.querySelector('[data-school-count]');
        const todayNode = document.querySelector('[data-school-today]');
        const nextTotal = (parseInt(totalNode?.textContent || '0', 10) || 0) + okCount;
        const nextToday = (parseInt(todayNode?.textContent || '0', 10) || 0) + okCount;
        document.querySelectorAll('[data-school-count]').forEach(node => node.textContent = String(nextTotal));
        document.querySelectorAll('[data-school-today]').forEach(node => node.textContent = String(nextToday));
        const vault = document.querySelector('[data-school-vault]');
        if (vault) vault.style.setProperty('--school-fill', `${{Math.max(8, Math.min(nextTotal / 30 * 100, 100))}}%`);
        status.textContent = `已收藏 ${{okCount}} 张学校错题，累计 ${{nextTotal}} 张，接下来会进入错题本识别队列。`;
      }});
    }});

    const recorders = {{}};
    const chunks = {{}};
    document.querySelectorAll('[data-voice-start]').forEach((button) => {{
      button.addEventListener('click', async () => {{
        const clip = button.dataset.voiceStart;
        const status = document.querySelector(`[data-voice-status="${{clip}}"]`);
        try {{
          const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
          chunks[clip] = [];
          const recorder = new MediaRecorder(stream);
          recorders[clip] = recorder;
          recorder.addEventListener('dataavailable', event => {{
            if (event.data.size) chunks[clip].push(event.data);
          }});
          recorder.addEventListener('stop', async () => {{
            stream.getTracks().forEach(track => track.stop());
            const blob = new Blob(chunks[clip], {{ type: recorder.mimeType || 'audio/webm' }});
            status.textContent = '正在上传声音...';
            try {{
              const response = await fetch(`/api/recording?day=${{encodeURIComponent(spec.day)}}&clip=${{encodeURIComponent(clip)}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': blob.type || 'audio/webm' }},
                body: blob
              }});
              if (!response.ok) throw new Error(await response.text());
              status.textContent = '声音已保存。';
            }} catch (error) {{
              status.textContent = '声音没有上传成功，稍后再试。';
            }}
          }});
          recorder.start();
          button.disabled = true;
          document.querySelector(`[data-voice-stop="${{clip}}"]`).disabled = false;
          status.textContent = '正在听你说。';
        }} catch (error) {{
          status.textContent = '浏览器没有拿到麦克风权限。';
        }}
      }});
    }});
    document.querySelectorAll('[data-voice-stop]').forEach((button) => {{
      button.addEventListener('click', () => {{
        const clip = button.dataset.voiceStop;
        const recorder = recorders[clip];
        if (recorder && recorder.state !== 'inactive') recorder.stop();
        button.disabled = true;
        document.querySelector(`[data-voice-start="${{clip}}"]`).disabled = false;
      }});
    }});
  </script>
</body>
</html>
"""


def _question_sections(spec: dict[str, Any]) -> str:
    sections: list[str] = []
    for section in spec.get("sections", []):
        title = _escape(section.get("title", "任务"))
        hint = _escape(section.get("hint", ""))
        cards = "".join(_question_card(question) for question in section.get("questions", []))
        sections.append(
            f"""
            <section>
              <div class="section-title">
                <h2>{title}</h2>
                <p>{hint}</p>
              </div>
              <div class="questions">{cards}</div>
            </section>
            """
        )
    return "\n".join(sections)


def _question_card(question: dict[str, Any]) -> str:
    qid = _escape(question.get("id", "Q"))
    knowledge = _escape(question.get("knowledge", "知识点"))
    prompt = _escape(question.get("prompt", ""))
    kind = _escape(question.get("kind", "practice"))
    answer = _escape(question.get("answer", ""))
    return f"""
    <article class="panel card" data-question-id="{qid}">
      <div class="meta">
        <span class="tag">{qid}</span>
        <span class="tag soft">{knowledge}</span>
        <span class="tag soft">{kind}</span>
      </div>
      <p class="prompt">{prompt}</p>
      <input data-answer-for="{qid}" autocomplete="off" placeholder="写下船长答案" />
      <div class="actions">
        <button type="button" data-check="{qid}" data-expected="{answer}">确认命中</button>
      </div>
      <p class="feedback" data-feedback-for="{qid}"></p>
    </article>
    """


def _growth_modals(
    spec: dict[str, Any],
    points: dict[str, Any],
    fish: dict[str, Any],
    rod: dict[str, Any],
    mistakes: list[Any],
    school_stats: dict[str, int],
    school_uploads: list[Any],
    school_drafts: list[Any],
    practice_history: list[dict[str, Any]],
) -> str:
    return "\n".join(
        [
            _modal("skills", "知识鱼图鉴", "每条鱼都是一个正在变稳的技能点。", _skill_map(spec, fish)),
            _modal("coin", "Switch2 鱼币罐", "鱼币会自己结算，船长只负责认真出海。", _coin_jar(points)),
            _modal("rods", "鱼竿墙", "已经拥有的鱼竿挂在墙上，后面的装备等你解锁。", _rod_wall(rod)),
            _modal("school", "学校错题收集", "把学校里的真实错题变成训练素材，越收集越有底气。", _school_mistake_collection(school_stats, school_uploads, school_drafts)),
            _modal("mistakes", "错误回顾", "错题不是扣分点，是下一次抓住 Boss 的雷达。", _mistake_review(mistakes)),
            _modal("history", "往日练习", "以前做过的每一天，都可以回来看题、复盘和补练。", _practice_history(practice_history)),
        ]
    )


def _practice_history(practice_history: list[dict[str, Any]]) -> str:
    cards = []
    for spec in sorted(practice_history, key=lambda item: str(item.get("day", ""))):
        day = str(spec.get("day") or "Day")
        title = str(spec.get("title") or day)
        focus = str(spec.get("focus") or "复盘当天练习")
        question_count = sum(len(section.get("questions", [])) for section in spec.get("sections", []))
        cards.append(
            f"""
            <a class="history-card" href="/captain/{_escape(day)}">
              <span>{_escape(day)}</span>
              <b>{_escape(title)}</b>
              <small>{_escape(question_count)} 题 · {_escape(focus)}</small>
            </a>
            """
        )
    if not cards:
        return '<p class="tiny">还没有往日练习记录。</p>'
    return f'<div class="history-grid">{"".join(cards)}</div>'


def _modal(modal_id: str, title: str, subtitle: str, body: str) -> str:
    return f"""
    <div class="modal-backdrop" data-modal="{_escape(modal_id)}" aria-hidden="true">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title-{_escape(modal_id)}">
        <div class="modal-head">
          <div>
            <h2 id="modal-title-{_escape(modal_id)}">{_escape(title)}</h2>
            <p class="tiny">{_escape(subtitle)}</p>
          </div>
          <button type="button" class="modal-close" data-close-modal>关闭</button>
        </div>
        {body}
      </section>
    </div>
    """


def _skill_map(spec: dict[str, Any], fish: dict[str, Any]) -> str:
    nodes = []
    seen: set[str] = set()
    for section in spec.get("sections", []):
        for question in section.get("questions", []):
            knowledge = str(question.get("knowledge", "")).strip()
            if knowledge and knowledge not in seen:
                seen.add(knowledge)
                nodes.append((knowledge, "active"))
    for knowledge in ["整数四则运算", "容量单位", "小数意义", "语文词语表达", "英语课堂句型", "应用题单位意识"]:
        if knowledge not in seen:
            nodes.append((knowledge, "locked"))
    current = int(fish.get("current", 0) or 0)
    cards = []
    for index, (name, state) in enumerate(nodes[:9], 1):
        cls = "done" if index <= current else ("active" if state == "active" else "")
        label = "已捕获" if index <= current else ("攻克中" if state == "active" else "待解锁")
        cards.append(
            f"""
            <div class="skill-node {cls}">
              <b>{_escape(name)}</b>
              <span class="tiny">{_escape(label)}</span>
            </div>
            """
        )
    return f'<div class="skill-map">{"".join(cards)}</div>'


def _coin_jar(points: dict[str, Any]) -> str:
    current = int(points.get("current", 0) or 0)
    goal = int(points.get("goal", 3500) or 3500)
    remain = max(goal - current, 0)
    fill = max(4, min(current / goal * 100, 100)) if goal else 4
    return f"""
    <div class="jar-stage" style="--coin-fill:{fill:.1f}%">
      <div class="coin-jar">
        <div class="coin-fill"></div>
        <span class="coin c1"></span>
        <span class="coin c2"></span>
        <span class="coin c3"></span>
      </div>
      <div>
        <p class="eyebrow">距离装满鱼币罐</p>
        <h2 style="margin:0 0 10px">{_escape(remain)} 枚</h2>
        <p class="tiny">当前 <span data-current-points>{_escape(current)}</span> / {_escape(goal)}。每天完成、讲清楚、修正错题，鱼币罐就会更满一点。</p>
      </div>
      <section class="mate-award">
        <h3>大副加分</h3>
        <p class="tiny">用于记录今天额外值得肯定的努力，例如主动讲题、坚持完成、修正错题。必须写理由，后台会留下积分流水。</p>
        <div class="mate-award-grid">
          <input data-mate-points type="number" min="1" step="1" placeholder="分数" />
          <input data-mate-password type="password" inputmode="numeric" autocomplete="off" placeholder="大副密码" />
          <input data-mate-reason autocomplete="off" placeholder="加分理由，例如：主动讲清一道错题" />
          <button type="button" data-mate-award>确认加分</button>
        </div>
        <p class="mate-award-status" data-mate-award-status></p>
      </section>
    </div>
    """


def _rod_wall(rod: dict[str, Any]) -> str:
    current_level = int(rod["current"].level)
    slots = []
    for level in ROD_LEVELS:
        owned = level.level <= current_level
        slots.append(
            f"""
            <div class="wall-slot {'hung' if owned else ''}">
              <div class="rod-icon"></div>
              <b>{_escape(level.name)} Lv.{_escape(level.level)}</b>
              <span class="tiny">{_escape(level.sea)} · {'已挂上墙' if owned else '等待解锁'}</span>
            </div>
            """
        )
    return f'<div class="rod-wall">{"".join(slots)}</div>'


def _school_mistake_collection(stats: dict[str, int], uploads: list[Any] | None = None, drafts: list[Any] | None = None) -> str:
    total = int(stats.get("total", 0) or 0)
    today = int(stats.get("today", 0) or 0)
    uploads = uploads or []
    drafts = drafts or []
    draft_by_upload = {str(_mistake_value(draft, "upload_id", "")): draft for draft in drafts}
    goal = 30
    fill = max(8, min(total / goal * 100, 100))
    remain = max(goal - total, 0)
    queue_cards = []
    for upload in uploads[:6]:
        upload_id = _mistake_value(upload, "id", "")
        draft = draft_by_upload.get(upload_id)
        status = _mistake_value(draft, "status", _mistake_value(upload, "status", "queued")) if draft else _mistake_value(upload, "status", "queued")
        subject = _mistake_value(draft, "subject", "待识别") if draft else "待识别"
        knowledge = _mistake_value(draft, "knowledge", "待识别") if draft else "待识别"
        prompt = _mistake_value(draft, "prompt", "等待进入识别队列。") if draft else "等待进入识别队列。"
        status_label = "已入错题回顾" if status == "ready" else "待 OCR/人工校准"
        queue_cards.append(
            f"""
            <div class="school-queue-card">
              <b>{_escape(_mistake_value(upload, "original_name", "学校错题"))}</b>
              <span>{_escape(status_label)} · {_escape(subject)} · {_escape(knowledge)}</span>
              <p>{_escape(prompt)}</p>
            </div>
            """
        )
    queue = "".join(queue_cards) or '<p class="tiny">还没有上传学校试卷。上传后会先进入这里，再进入错题回顾。</p>'
    return f"""
    <div class="school-vault" data-school-vault style="--school-fill:{fill:.1f}%">
      <div class="vault-top">
        <div class="vault-number"><span>累计收藏</span><b><span data-school-count>{_escape(total)}</span> 张</b></div>
        <div class="vault-number"><span>今日新增</span><b><span data-school-today>{_escape(today)}</span> 张</b></div>
      </div>
      <div class="vault-tank">
        <div class="vault-fill"></div>
        <span class="vault-card c1"></span>
        <span class="vault-card c2"></span>
        <span class="vault-card c3"></span>
        <div class="vault-copy">
          <h3>错题收藏舱</h3>
          <p>再收集 {_escape(remain)} 张，就能装满第一阶段错题素材库。学校里的每一张真实错题，都会变成后续回炉训练的雷达。</p>
        </div>
      </div>
      <section class="school-upload">
        <h3>上传学校作业 / 试卷照片</h3>
        <p class="tiny">支持照片、PDF 和结构化 txt。照片/PDF 会先归档并进入识别队列；结构化 txt 可直接进入错题回顾。</p>
        <input type="file" data-school-mistake-files accept="image/*,.pdf,.txt,.md,text/plain" multiple />
        <div class="actions">
          <button type="button" data-upload-school-mistakes>上传学校错题</button>
        </div>
        <p class="school-upload-status" data-school-mistake-status></p>
      </section>
      <section class="school-queue">
        <h3>最近上传队列</h3>
        {queue}
      </section>
    </div>
    """


def _mistake_review(mistakes: list[Any]) -> str:
    subjects = ["数学", "语文", "英语"]
    grouped = {subject: [] for subject in subjects}
    for mistake in mistakes:
        subject = _mistake_value(mistake, "subject", "数学")
        grouped.setdefault(subject, []).append(mistake)
    total = sum(len(grouped.get(subject, [])) for subject in subjects)
    active_subject = next((subject for subject in subjects if grouped.get(subject)), "数学")
    tabs = "".join(
        f'<button type="button" class="mistake-tab {"active" if subject == active_subject else ""}" data-mistake-tab="{_escape(subject)}">{_escape(subject)} · {_escape(len(grouped.get(subject, [])))}</button>'
        for subject in subjects
    )
    sheets = "".join(_mistake_sheet(subject, grouped.get(subject, []), subject == active_subject) for subject in subjects)
    return f"""
    <div class="mistake-review">
      <div class="mistake-summary">
        <div>
          <b>{_escape(total)}</b>
          <span>个待回顾点</span>
        </div>
        <span>每次只打开一科，先抓一个关键动作。</span>
      </div>
      <div class="mistake-tabs" role="tablist" aria-label="错题科目切换">{tabs}</div>
      {sheets}
      <section class="rematch-panel" data-rematch-panel>
        <h3>变换题型再战一次</h3>
        <p class="rematch-line" data-rematch-question-text>先点一行错题的“变换题型再战一次”。</p>
        <input data-rematch-answer autocomplete="off" placeholder="写下再战答案" />
        <div class="actions">
          <button type="button" data-check-rematch>确认再战</button>
        </div>
        <p class="rematch-status" data-rematch-status></p>
      </section>
    </div>
    """


def _mistake_sheet(subject: str, mistakes: list[Any], active: bool) -> str:
    rows = []
    for index, mistake in enumerate(mistakes[:6], 1):
        category = _mistake_value(mistake, "category", "小题失误")
        cls = "boss" if category == "Boss失误" else ""
        knowledge = _mistake_value(mistake, "knowledge", "待回炉知识点")
        prompt = _mistake_value(mistake, "prompt", "")
        student_answer = _display_student_answer(subject, _mistake_value(mistake, "student_answer", "未记录"))
        expected_answer = _display_expected_answer(subject, knowledge, _mistake_value(mistake, "expected_answer", "待核对"))
        note = _mistake_value(mistake, "note", "") or _mistake_value(mistake, "status", "需要回炉")
        item_id = _mistake_value(mistake, "item_id", f"{subject}-{index}")
        next_action = _next_action_for(knowledge, note, subject)
        rematch = _rematch_for(knowledge, subject)
        rows.append(
            f"""
            <tr class="{cls}">
              <td><button type="button" class="voice-explain" data-speak="{_escape(next_action)}">听讲解</button></td>
              <td><button type="button" class="rematch-button" data-rematch-trigger data-rematch-question="{_escape(rematch['question'])}" data-rematch-answer="{_escape(rematch['answer'])}" data-rematch-id="{_escape(item_id)}">变换题型</button></td>
              <td class="mistake-id">{_escape(index)}</td>
              <td><span class="mistake-badge">{_escape(category)}</span></td>
              <td class="mistake-topic">{_escape(knowledge)}</td>
              <td class="mistake-question">{_escape(prompt)}</td>
              <td class="mistake-answer">{_escape(student_answer)}</td>
              <td class="mistake-answer">{_escape(expected_answer)}</td>
              <td class="mistake-note-cell">{_escape(note)}</td>
              <td class="mistake-action">{_escape(next_action)}</td>
            </tr>
            """
        )
    if not rows:
        body = f'<p class="mistake-empty">{_escape(subject)}今天暂时没有待回顾错题。保持轻装，只做该做的一点点。</p>'
    else:
        body = f"""
        <div class="mistake-table-wrap">
          <table class="mistake-table">
            <colgroup>
              <col style="width:72px" />
              <col style="width:110px" />
              <col style="width:48px" />
              <col style="width:86px" />
              <col style="width:128px" />
              <col style="width:310px" />
              <col style="width:120px" />
              <col style="width:150px" />
              <col style="width:175px" />
              <col style="width:175px" />
            </colgroup>
            <thead>
              <tr>
                <th>语音</th>
                <th>再战</th>
                <th>序号</th>
                <th>类型</th>
                <th>知识点</th>
                <th>题目</th>
                <th>船长答案</th>
                <th>正确方向</th>
                <th>错因</th>
                <th>下一步</th>
              </tr>
            </thead>
            <tbody>{"".join(rows)}</tbody>
          </table>
        </div>
        """
    return f'<section class="mistake-sheet {"active" if active else ""}" data-mistake-sheet="{_escape(subject)}">{body}</section>'


def _display_student_answer(subject: str, answer: str) -> str:
    if subject in {"语文", "英语"} and answer in {"等第“合格须努力”", '等第"合格须努力"', "卷面有错"}:
        return f"卷面提示：{answer}"
    return answer


def _display_expected_answer(subject: str, knowledge: str, answer: str) -> str:
    if subject == "语文" and answer == "需加强":
        if "概括" in knowledge:
            return "人物/对象 + 主要事件 + 结果"
        if "修辞" in knowledge:
            return "先找本体、喻体或人的动作"
    if subject == "英语" and answer == "需加强":
        if "三单" in knowledge:
            return "he/she/it 后动词加 s/es"
        if "进行时" in knowledge:
            return "be 动词 + V-ing"
    return answer


def _next_action_for(knowledge: str, note: str, subject: str = "数学") -> str:
    if subject == "语文":
        if "概括" in knowledge:
            return "先圈人物和事件，再压成一句话。"
        if "修辞" in knowledge:
            return "先问像不像、会不会做人动作，再判断修辞。"
        return "先找关键词，再用自己的话说清楚。"
    if subject == "英语":
        if "三单" in knowledge:
            return "先看主语是不是he/she/it，再检查动词。"
        if "进行时" in knowledge:
            return "先找be动词，再检查动词ing形式。"
        return "先对齐句型，再检查动词形式。"
    text = f"{knowledge} {note}"
    if "除法" in text:
        return "先分别算，再判断能不能合并。"
    if "容量" in text:
        return "先统一单位，再除法，最后补单位。"
    if "小数" in text:
        return "先写位值关系，再下笔计算。"
    if "应用题" in text or "转移" in text:
        return "先画关系变化，再列式。"
    if "答句" in text or "单位" in text:
        return "算完检查答句和单位。"
    return "先把题目关系说清楚，再下笔。"


def _rematch_for(knowledge: str, subject: str = "数学") -> dict[str, str]:
    if subject == "语文":
        if "概括" in knowledge:
            return {
                "question": "再战：读句子“放学后，小明发现同桌没带伞，就把自己的伞借给了他。”用一句话概括主要内容。",
                "answer": "小明借伞给同桌",
            }
        if "修辞" in knowledge:
            return {
                "question": "再战：判断修辞：“小河唱着歌向前跑。”这是比喻还是拟人？",
                "answer": "拟人",
            }
        return {"question": "再战：把这道语文错题用一句完整的话重新说明理由。", "answer": "开放题"}
    if subject == "英语":
        if "三单" in knowledge:
            return {"question": "再战：He ____ (like) fishing after school.", "answer": "likes"}
        if "进行时" in knowledge:
            return {"question": "再战：Look! The boy is ____ (run).", "answer": "running"}
        return {"question": "再战：按今天句型重新造一个正确句子。", "answer": "开放题"}
    if "除法" in knowledge:
        return {"question": "再战：480÷6 + 480÷8 = ____。能不能写成480÷14？", "answer": "140；不能"}
    if "容量" in knowledge:
        return {"question": "再战：4升200ml = ____ml；每瓶300ml，可装满____瓶。", "answer": "4200ml；14瓶"}
    if "小数" in knowledge:
        return {"question": "再战：0.406 + 0.194 = ____。", "answer": "0.6"}
    if "商和余数" in knowledge:
        return {"question": "再战：a÷b商9余7，a、b都乘10后，商____，余数____。", "answer": "9；70"}
    if "应用题" in knowledge or "转移" in knowledge:
        return {"question": "再战：小明给小红0.4元后，比小红少0.2元，原来小明比小红多____元。", "answer": "0.6"}
    if "括号" in knowledge or "混合运算" in knowledge:
        return {"question": "再战：[3600-(20+80×10)]÷20 = ____。", "answer": "139"}
    if "单位" in knowledge or "答句" in knowledge:
        return {"question": "再战：计划每天180个，10天完成；提前1天完成，实际每天____个。", "answer": "200个"}
    return {"question": "再战：把这道错题换一组数字，再完整写一遍答案。", "answer": "开放题"}


def _fallback_mistakes() -> list[dict[str, str]]:
    return [
        {
            "item_id": "D3-B3",
            "category": "Boss失误",
            "knowledge": "除法陷阱概念语言",
            "prompt": "填空：被除数（ ）拆开，除数（ ）拆开。",
            "student_answer": "被除数可拆开；除数表述不稳",
            "expected_answer": "被除数可以拆开；除数不能拆开",
            "note": "会判断，但概念语言要固定成一句话。",
        },
        {
            "item_id": "D3-V1",
            "category": "小题失误",
            "knowledge": "容量单位换算和有余数除法",
            "prompt": "3升120ml分装240ml瓶，可装满几瓶，剩几ml。",
            "student_answer": "11瓶，剩8ml",
            "expected_answer": "13瓶，剩0ml",
            "note": "先统一成3120ml，再做除法。",
        },
    ]


def _mistake_value(mistake: Any, key: str, default: str) -> str:
    if isinstance(mistake, dict):
        return str(mistake.get(key) or default)
    return str(getattr(mistake, key, default) or default)


def _streak_lights(spec: dict[str, Any]) -> str:
    day_number = int(rod_status_for_spec(spec)["day_number"])
    lamps = []
    for index in range(1, 21):
        lamps.append(f'<span class="lamp {"on" if index <= day_number else ""}">D{index}</span>')
    return f"""
    <p class="tiny">今天只要认真完成，就是把路上的一盏灯点亮。</p>
    <div class="lamp-road">{"".join(lamps)}</div>
    """


def _encouragement(spec: dict[str, Any]) -> str:
    day_number = int(rod_status_for_spec(spec)["day_number"])
    lines = [
        "今天稳住一小步。",
        "做完就是胜利。",
        "Boss会被你看穿。",
        "坚持会发光。",
    ]
    return lines[(day_number - 1) % len(lines)]


def _hero_media(media_manifest: dict[str, Any] | None, spec: dict[str, Any], rod: dict[str, Any]) -> str:
    if media_manifest:
        videos = media_manifest.get("videos") or []
        if videos:
            video = videos[0]
            return _video_success_case(video, spec, rod)
        posters = media_manifest.get("posters") or []
        if posters:
            poster = posters[0]
            return _animated_mission_scene(_web_asset_path(poster.get("path", "")), spec, rod)
    return _animated_mission_scene("", spec, rod)


def _animated_mission_scene(image_path: str, spec: dict[str, Any], rod: dict[str, Any]) -> str:
    current = rod["current"]
    scene_image = f"url('{_escape(image_path)}')" if image_path else "linear-gradient(135deg, #12365d, #071827)"
    focus = _escape(spec.get("focus", "今日任务"))
    boss = _escape(current.boss)
    sea = _escape(current.sea)
    rod_name = _escape(current.name)
    return f"""
    <div class="mission-scene" style="--scene-image:{scene_image}">
      <div class="scene-bg"></div>
      <div class="scan"></div>
      <div class="hook"></div>
      <div class="wave"></div>
      <div class="scene-copy">
        <span class="boss-line">Boss雷达 · {boss}</span>
        <h2>{sea} 出海任务</h2>
        <p>{rod_name} 已装备。今日目标：{focus}</p>
      </div>
    </div>
    """


def _video_success_case(video: dict[str, Any], spec: dict[str, Any], rod: dict[str, Any]) -> str:
    current = rod["current"]
    src = _escape(_web_asset_path(video.get("path", "")))
    mime_type = _escape(video.get("mime_type", "video/mp4"))
    focus = _escape(spec.get("focus", "今日任务"))
    boss = _escape(current.boss)
    sea = _escape(current.sea)
    rod_name = _escape(current.name)
    title = _escape(video.get("title", "王牌钓手短视频"))
    return f"""
    <div class="mission-scene">
      <video class="scene-video" muted playsinline autoplay loop controls preload="metadata">
        <source src="{src}" type="{mime_type}" />
      </video>
      <div class="scan"></div>
      <div class="hook"></div>
      <div class="wave"></div>
      <div class="scene-copy">
        <span class="case-badge">短视频成功样例 · {title}</span>
        <span class="boss-line">Boss雷达 · {boss}</span>
        <h2>{sea} 出海任务</h2>
        <p>{rod_name} 已装备。今日目标：{focus}</p>
      </div>
    </div>
    """


def render_home(specs: list[dict[str, Any]]) -> str:
    cards = []
    for spec in specs:
        day = _escape(spec.get("day", "Day"))
        title = _escape(spec.get("title", day))
        focus = _escape(spec.get("focus", ""))
        cards.append(
            f"""
            <a class="card" href="/captain/{day}">
              <strong>{title}</strong>
              <span>{focus}</span>
            </a>
            """
        )
    body = "\n".join(cards) or "<p>还没有每日任务。</p>"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>袁佳乐船长训练站</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", system-ui, sans-serif; background: #09111f; color: #f6f7fb; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 34px 20px; }}
    h1 {{ font-size: 42px; margin: 0 0 20px; }}
    .grid {{ display: grid; gap: 12px; }}
    .card {{ display: grid; gap: 8px; padding: 20px; border-radius: 8px; background: rgba(255,255,255,.08); color: inherit; text-decoration: none; border: 1px solid rgba(255,255,255,.14); }}
    .card strong {{ font-size: 22px; }}
    .card span {{ color: #aab1c5; }}
  </style>
</head>
<body>
  <main>
    <h1>袁佳乐船长训练站</h1>
    <div class="grid">{body}</div>
  </main>
</body>
</html>
"""


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _rod_panel(rod: dict[str, Any]) -> str:
    current = rod["current"]
    next_level = rod["next"]
    next_text = f"下一竿：{next_level.name} Lv.{next_level.level}" if next_level else "最高等级"
    materials = "".join(f'<span class="material">{_escape(item)}</span>' for item in rod["materials"])
    if not materials:
        materials = '<span class="material">完成今日出海</span>'
    progress = max(0, min(float(rod["progress"]) * 100, 100))
    return f"""
      <section class="panel rod-panel" style="--rod-progress:{progress:.0f}%">
        <div class="rod-head">
          <div>
            <p class="eyebrow">鱼竿升级</p>
            <h2>{_escape(current.name)} Lv.{_escape(current.level)} · {_escape(current.sea)}</h2>
          </div>
          <strong>{_escape(next_text)}</strong>
        </div>
        <div class="rod-track"><span></span></div>
        <p class="tiny">海域进度：{_escape(rod["completed_in_sea"])}/{_escape(rod["days_in_sea"])}。{_escape(rod["upgrade_text"])}</p>
        <div class="material-row">{materials}</div>
      </section>
    """


def _web_asset_path(value: object) -> str:
    path = str(value).replace("\\", "/")
    while path.startswith("../"):
        path = path[3:]
    if not path.startswith("/"):
        path = "/" + path
    return path
