"""Dashboard renderer for 王牌钓手 — progress visualization."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

from engine.rod_system import ROD_LEVELS, rod_status_for_spec
from tutor_core.next_day import latest_day_spec
from tutor_core.points import POINTS_GOAL, read_current_points


def render_dashboard(root: Path) -> str:
    """Render the progress dashboard page."""
    spec = latest_day_spec(root) or {}
    points = read_current_points(root)
    rod = rod_status_for_spec(spec) if spec else _default_rod()
    day = str(spec.get('day', 'Day6'))
    day_num = rod.get('day_number', 6)
    
    # Read grading log for recent stats
    grading_stats = _read_grading_stats(root)
    mood = _read_latest_mood(root)
    
    # First mate script
    mate_script = _first_mate_script(day_num, points, grading_stats)
    
    # Progress data
    progress_pct = min(100, int(points / POINTS_GOAL * 100))
    rod_name = rod['current'].name if rod.get('current') else '竹竿'
    rod_level = rod['current'].level if rod.get('current') else 1
    sea = rod['current'].sea if rod.get('current') else '新手沙滩'
    completed = rod.get('completed_in_sea', 1)
    total_days = rod.get('days_in_sea', 3)
    sea_pct = min(100, int(completed / total_days * 100))
    
    # Knowledge fish from grading
    knowledge_fish = grading_stats.get('knowledge_count', 0)
    fish_goal = 93
    
    # Encouragement
    encouragements = [
        "今天的浪再大，船长也稳得住。",
        "每一次出海，航海图就多画一笔。",
        "Boss 雷达已经启动，逃不掉的。",
        "Switch2 在港口等你。",
        "坚持是最锋利的鱼钩。",
    ]
    enc = encouragements[(day_num - 1) % len(encouragements)]
    
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>船长航海图 · {day}</title>
  <style>
    :root {{
      --ink: #f6f7fb; --muted: #aab1c5; --panel: rgba(13,22,39,.88);
      --gold: #ffd166; --cyan: #5eead4; --blue: #60a5fa; --ok: #7ddf96; --bad: #ff8a8a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; color: var(--ink);
      background: radial-gradient(circle at 70% 10%, rgba(94,234,212,.18), transparent 28%),
                  linear-gradient(180deg, #12233d 0%, #09111f 56%, #050814 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
      min-height: 100vh;
    }}
    .shell {{ max-width: 960px; margin: 0 auto; padding: 28px 20px 48px; }}
    h1 {{ font-size: 36px; margin: 0 0 6px; }}
    .sub {{ color: var(--muted); font-size: 16px; margin: 0 0 28px; }}
    .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{
      background: var(--panel); border: 1px solid rgba(255,255,255,.13);
      border-radius: 8px; padding: 22px;
      box-shadow: 0 18px 60px rgba(0,0,0,.28);
    }}
    .card.wide {{ grid-column: 1 / -1; }}
    .card h2 {{ margin: 0 0 14px; font-size: 22px; }}
    .stat-row {{ display: flex; justify-content: space-between; gap: 12px; align-items: end; }}
    .stat-row .value {{ font-size: 42px; font-weight: 950; }}
    .stat-row .label {{ color: var(--muted); font-size: 14px; }}
    .bar-track {{ height: 18px; background: rgba(255,255,255,.12); border-radius: 999px; overflow: hidden; margin-top: 10px; }}
    .bar-fill {{ height: 100%; border-radius: 999px; transition: width .6s ease; }}
    .bar-fill.gold {{ background: linear-gradient(90deg, var(--cyan), var(--gold)); }}
    .bar-fill.blue {{ background: linear-gradient(90deg, var(--blue), var(--cyan)); }}
    .bar-fill.green {{ background: linear-gradient(90deg, #34d399, #22c55e); }}
    
    .fish-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 12px; }}
    .fish-stat {{ text-align: center; padding: 12px 8px; background: rgba(255,255,255,.06); border-radius: 8px; }}
    .fish-stat .num {{ font-size: 28px; font-weight: 950; }}
    .fish-stat .lbl {{ color: var(--muted); font-size: 12px; margin-top: 4px; }}
    
    .sea-map {{ display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }}
    .sea-node {{
      flex: 1; min-width: 100px; padding: 12px; border-radius: 8px;
      text-align: center; font-size: 13px; font-weight: 800;
      background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12);
    }}
    .sea-node.done {{ border-color: var(--ok); background: rgba(125,223,150,.12); }}
    .sea-node.active {{ border-color: var(--gold); background: rgba(255,209,102,.12); }}
    .sea-node .sea-boss {{ color: var(--muted); font-size: 11px; margin-top: 4px; }}
    
    .mate-card {{
      background: linear-gradient(135deg, rgba(28,74,132,.92), rgba(12,18,33,.98) 56%),
                  radial-gradient(circle at 82% 12%, rgba(255,209,102,.22), transparent 34%);
      border-color: rgba(255,209,102,.35);
    }}
    .mate-script {{ margin-top: 12px; }}
    .mate-script p {{
      margin: 6px 0; padding: 10px 14px;
      background: rgba(255,255,255,.08); border-radius: 8px; font-size: 18px; line-height: 1.55;
    }}
    .mate-script p b {{ color: var(--gold); }}
    
    .mood-badge {{
      display: inline-block; padding: 6px 12px; border-radius: 999px;
      font-size: 14px; font-weight: 900;
    }}
    .mood-badge.green {{ background: rgba(125,223,150,.25); color: var(--ok); }}
    .mood-badge.yellow {{ background: rgba(255,209,102,.25); color: var(--gold); }}
    .mood-badge.red {{ background: rgba(255,138,138,.25); color: var(--bad); }}
    
    .nav {{ display: flex; gap: 12px; margin-bottom: 28px; }}
    .nav a {{
      color: var(--ink); text-decoration: none; padding: 10px 16px;
      background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16);
      border-radius: 8px; font-weight: 800;
    }}
    .nav a:hover {{ border-color: var(--cyan); }}
    .nav a.here {{ background: rgba(94,234,212,.18); border-color: var(--cyan); }}
    
    .encouragement {{
      text-align: center; padding: 28px; color: var(--cyan); font-size: 22px; font-weight: 900;
    }}
    
    @media (max-width: 700px) {{
      .dashboard {{ grid-template-columns: 1fr; }}
      .fish-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="nav">
      <a href="/captain/today">今日出海</a>
      <a href="/captain/dashboard" class="here">航海图</a>
      <a href="/">历史记录</a>
    </div>
    
    <h1>船长航海图 · {_esc(day)}</h1>
    <p class="sub">{_esc(sea)} — {_esc(rod_name)} Lv.{rod_level}</p>
    
    <div class="dashboard">
      <!-- Switch2 Progress -->
      <div class="card">
        <h2>Switch2 渔币</h2>
        <div class="stat-row">
          <span class="value" style="color:var(--gold)">{points}</span>
          <span class="label">目标 {POINTS_GOAL}</span>
        </div>
        <div class="bar-track"><div class="bar-fill gold" style="width:{progress_pct}%"></div></div>
        <p style="color:var(--muted);margin:10px 0 0;font-size:14px">还差 {POINTS_GOAL-points} 分。每做对一题 +2 分，每日完成 +15 分。</p>
      </div>
      
      <!-- Sea Progress -->
      <div class="card">
        <h2>海域进度</h2>
        <div class="stat-row">
          <span class="value" style="color:var(--cyan)">{completed}/{total_days}</span>
          <span class="label">{_esc(sea)}</span>
        </div>
        <div class="bar-track"><div class="bar-fill blue" style="width:{sea_pct}%"></div></div>
        <div class="sea-map">
          {_sea_map(day_num)}
        </div>
      </div>
      
      <!-- Fish stats -->
      <div class="card wide">
        <h2>今日渔获统计</h2>
        <div class="fish-grid">
          <div class="fish-stat"><span class="num" style="color:var(--ok)">{grading_stats.get('ok', 0)}</span><span class="lbl">命中 🎯</span></div>
          <div class="fish-stat"><span class="num" style="color:var(--gold)">{grading_stats.get('review', 0)}</span><span class="lbl">差一点 🪝</span></div>
          <div class="fish-stat"><span class="num" style="color:var(--bad)">{grading_stats.get('bad', 0)}</span><span class="lbl">逃脱鱼 🐟</span></div>
          <div class="fish-stat"><span class="num" style="color:var(--blue)">{grading_stats.get('points', 0)}</span><span class="lbl">今日鱼币 💰</span></div>
        </div>
      </div>
      
      <!-- First Mate Script -->
      <div class="card wide mate-card">
        <h2>大副今日台词</h2>
        <p style="color:var(--muted);margin:0 0 8px">爸爸只需要说这三句话，照着念就行：</p>
        <div class="mate-script">
          {mate_script}
        </div>
      </div>
      
      <!-- Mood -->
      {_mood_card(mood)}
      
      <!-- Encouragement -->
      <div class="card wide encouragement">
        {_esc(enc)}
      </div>
    </div>
  </div>
</body>
</html>"""


def _sea_map(day_num: int) -> str:
    nodes = []
    for rl in ROD_LEVELS:
        cls = ""
        if day_num > rl.end_day:
            cls = "done"
        elif rl.start_day <= day_num <= rl.end_day:
            cls = "active"
        nodes.append(
            f'<div class="sea-node {cls}">'
            f'{_esc(rl.sea)}<br>{_esc(rl.name)}'
            f'<div class="sea-boss">Boss: {_esc(rl.boss)}</div>'
            f'</div>'
        )
    return "".join(nodes)


def _first_mate_script(day_num: int, points: int, stats: dict) -> str:
    sea_names = ["新手沙滩", "珊瑚礁", "沉船湾", "深海裂谷", "远古深渊"]
    sea_idx = min((day_num - 1) // 4, 4)
    sea = sea_names[sea_idx]
    remaining = POINTS_GOAL - points
    
    lines = [
        f'<p>1️⃣ <b>"船长，今天我们去<b>{sea}</b>海域，准备好了吗？"</b></p>',
        f'<p>2️⃣ <b>（做完后）"这道Boss题你是怎么想的？教教大副。"</b>（录10秒语音）</p>',
    ]
    if remaining > 0:
        lines.append(
            f'<p>3️⃣ <b>（结束后）"今天真棒！离Switch2还差<b>{remaining}</b>分，继续加油！"</b></p>'
        )
    else:
        lines.append(
            '<p>3️⃣ <b>"Switch2 目标达成！🎉 你是最棒的船长！"</b></p>'
        )
    return "".join(lines)


def _mood_card(mood: dict) -> str:
    if not mood:
        return ""
    color = mood.get('color', 'green')
    text = mood.get('text', '今天感觉正常')
    return f"""
    <div class="card wide">
      <h2>情绪状态</h2>
      <span class="mood-badge {color}">{'🟢 绿灯' if color == 'green' else '🟡 黄灯' if color == 'yellow' else '🔴 红灯'}</span>
      <p style="margin:10px 0 0;color:var(--muted)">{_esc(text)}</p>
      {'<p style="color:var(--bad);margin:8px 0 0">今天红灯：不推进新内容，只做轻量复练。</p>' if color == 'red' else ''}
    </div>"""


def _read_grading_stats(root: Path) -> dict[str, int]:
    path = root / 'records' / 'grading-log.csv'
    if not path.exists():
        return {'ok': 0, 'review': 0, 'bad': 0, 'points': 0, 'knowledge_count': 0}
    stats = {'ok': 0, 'review': 0, 'bad': 0, 'points': 0, 'knowledge_count': 0}
    knowledges: set[str] = set()
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                state = (row.get('status') or '').strip()
                if state == 'ok':
                    stats['ok'] += 1
                elif state == 'review':
                    stats['review'] += 1
                elif state == 'bad':
                    stats['bad'] += 1
                k = (row.get('knowledge') or '').strip()
                if k and state == 'ok':
                    knowledges.add(k)
    except Exception:
        pass
    stats['knowledge_count'] = len(knowledges)
    return stats


def _read_latest_mood(root: Path) -> dict:
    path = root / 'records' / 'mood-log.csv'
    if not path.exists():
        return {}
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return {}
        last = rows[-1]
        return {'color': (last.get('color') or 'green').strip(), 'text': (last.get('note') or '').strip()}
    except Exception:
        return {}


def _default_rod() -> dict:
    return {
        'day_number': 6,
        'current': ROD_LEVELS[1],
        'next': ROD_LEVELS[2],
        'completed_in_sea': 3,
        'days_in_sea': 4,
        'progress': 0.75,
        'materials': [],
        'upgrade_text': '击败沧龙后解锁合金竿 Lv.3',
    }


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)
