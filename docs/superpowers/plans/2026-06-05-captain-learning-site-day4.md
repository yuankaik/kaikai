# Captain Learning Site Day4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Day4 web-first learning loop: a child-friendly Captain Deck homepage, a Day4 practice page, local result export, and parent-side inputs that feed Day5.

**Architecture:** Keep the current spec-driven pipeline. Add a thin site layer that renders `practice/specs/*.json` into self-contained HTML and writes browser-captured results to a downloadable JSON file. Do not add accounts, cloud storage, server databases, or a large app framework until the Day4 loop proves useful.

**Tech Stack:** Python standard library, current `tutor_core` generators, current `rendering` package, static HTML/CSS/JavaScript, `unittest`.

---

## File Structure

- Create `tutor_core/day4_spec.py`: builds Day4 spec from Day3 result/grading inputs and known Day2/Day3 weak points.
- Modify `scripts/generate_daily_practice.py`: register `Day4` once Day4 spec builder exists.
- Modify `scripts/generate_web_practice.py`: accept any spec and optionally generate an index page.
- Create `rendering/captain_site.py`: renders the Captain Deck homepage from available daily specs and points state.
- Modify `rendering/day_web.py`: upgrade from single-page worksheet to learning session page with station flow, result export, and parent inputs.
- Create `tests/test_day4_site_flow.py`: tests Day4 spec, homepage, web result export markup, and data contract.
- Create `practice/results/README.md`: documents browser-exported result JSON contract.

## Data Contracts

### Daily Spec

Every web-first day spec must contain these fields:

```json
{
  "day": "Day4",
  "title": "Day4-虎鲸队长的除法航线",
  "mode": "web-first",
  "focus": "除法陷阱回炉 + 容量单位复测 + 三科课堂雷达",
  "points": {"current": 1876, "goal": 3500},
  "knowledge_fish": {"current": 2, "goal": 93},
  "sections": [
    {
      "title": "Normal Rod",
      "hint": "short hint",
      "questions": [
        {
          "id": "D4-R1",
          "subject": "数学",
          "knowledge": "除法陷阱",
          "kind": "practice",
          "prompt": "判断：420÷7 + 420÷3 = 420÷(7+3)  [ ]对 [ ]错",
          "answer": "错",
          "difficulty": 1,
          "unlock_reward": "抓回一条..."
        }
      ]
    }
  ],
  "feynman": {
    "target": "除数不能合并",
    "prompt": "请船长讲清楚：为什么 420÷7 + 420÷3 不能写成 420÷(7+3)？",
    "pass_rule": "能说出这是两次分，不是一次按10分；除数不能随便合并。"
  },
  "parent_card": {
    "before": ["先问精神状态：绿/黄/红。"],
    "during": ["不会时允许点提示，但记录提示次数。"],
    "after": ["导出 Day4-result.json。"],
    "inputs": ["Day4-result.json", "Boss讲题语音"]
  },
  "classroom_radar": ["语文今天讲到...", "数学今天讲到...", "英语今天讲到..."]
}
```

### Result JSON

The Day4 browser export must produce:

```json
{
  "day": "Day4",
  "title": "Day4-虎鲸队长的除法航线",
  "completed_at": "browser-local timestamp",
  "answers": {
    "D4-R1": {
      "answer": "student answer",
      "completed": true,
      "hint_count": 0,
      "revealed_answer": false
    }
  },
  "radar": {
    "1": "语文课堂内容",
    "2": "数学课堂内容",
    "3": "英语课堂内容"
  },
  "self_check": {
    "energy": "green",
    "feeling": "想继续"
  }
}
```

## Task 1: Day4 Spec Builder

**Files:**
- Create: `tutor_core/day4_spec.py`
- Test: `tests/test_day4_site_flow.py`

- [ ] **Step 1: Write the failing test**

Add this test file:

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Day4SiteFlowTests(unittest.TestCase):
    def test_builds_day4_web_first_spec(self) -> None:
        from tutor_core.day4_spec import build_day4_spec

        spec = build_day4_spec(ROOT)

        self.assertEqual(spec["day"], "Day4")
        self.assertEqual(spec["mode"], "web-first")
        self.assertIn("除法", spec["focus"])
        self.assertEqual(spec["points"]["current"], 1876)
        self.assertGreaterEqual(len(spec["sections"]), 3)
        ids = [q["id"] for section in spec["sections"] for q in section["questions"]]
        self.assertIn("D4-R1", ids)
        self.assertIn("D4-B1", ids)
        self.assertIn("D4-V1", ids)
        self.assertIn("feynman", spec)
        self.assertIn("classroom_radar", spec)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_day4_site_flow -v
```

Expected: fail with `ModuleNotFoundError: No module named 'tutor_core.day4_spec'`.

- [ ] **Step 3: Implement Day4 spec builder**

Create `tutor_core/day4_spec.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from tutor_core.points import POINTS_GOAL, read_current_points


def _question(
    item_id: str,
    subject: str,
    knowledge: str,
    prompt: str,
    answer: str,
    kind: str = "practice",
    difficulty: int = 1,
    unlock_reward: str = "",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "subject": subject,
        "knowledge": knowledge,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
        "difficulty": difficulty,
        "unlock_reward": unlock_reward,
    }


def build_day4_spec(root: Path) -> dict[str, Any]:
    return {
        "day": "Day4",
        "title": "Day4-虎鲸队长的除法航线",
        "mode": "web-first",
        "focus": "除法陷阱回炉 + 容量单位复测 + 三科课堂雷达",
        "source_session": "2026-06-05-Day3",
        "points": {"current": read_current_points(root), "goal": POINTS_GOAL},
        "knowledge_fish": {"current": 2, "goal": 93},
        "sections": [
            {
                "title": "Normal Rod - 热身航线",
                "hint": "先确认昨天的鱼没有再逃走",
                "questions": [
                    _question("D4-R1", "数学", "除法计算与运算顺序", "640 ÷ 8 + 360 ÷ 6 = ____", "140", difficulty=1, unlock_reward="热身鱼"),
                    _question("D4-R2", "数学", "两位数退位减法", "61 - 28 = ____", "33", difficulty=1, unlock_reward="退位鱼"),
                    _question("D4-R3", "英语", "课堂句子复述", "写出今天英语课你记住的一句话：________________", "开放题", difficulty=1, unlock_reward="英语贝壳"),
                ],
            },
            {
                "title": "Monster Rod - Boss识别",
                "hint": "今天只打一个核心Boss：除数不能随便合并",
                "questions": [
                    _question("D4-B1", "数学", "除法陷阱", "判断：420÷7 + 420÷3 = 420÷(7+3)  [ ]对 [ ]错", "错", "boss", 2, "Boss鳞片"),
                    _question("D4-B2", "数学", "除法陷阱", "420÷7 + 420÷3 = ____。能不能写成 420÷10？", "200；不能", "boss", 2, "Boss牙齿"),
                    _question("D4-B3", "数学", "费曼解释", "用一句话解释：为什么除数不能合并？", "因为这是两次分，除数代表每次怎么分，不能相加变成一次分。", "boss", 3, "Boss核心"),
                ],
            },
            {
                "title": "Super Rod - 轻量变式",
                "hint": "做完就收工，不追加",
                "questions": [
                    _question("D4-V1", "数学", "容量单位换算和有余数除法", "2升500ml = ____ml；每瓶250ml，可装满____瓶。", "2500ml；10瓶", difficulty=2, unlock_reward="容量鱼"),
                    _question("D4-V2", "语文", "课堂词语回忆", "写出今天语文课你记住的一个词，并造一个短句。", "开放题", difficulty=1, unlock_reward="语文贝壳"),
                ],
            },
        ],
        "feynman": {
            "target": "除数不能合并",
            "prompt": "请船长讲清楚：为什么 420÷7 + 420÷3 不能写成 420÷(7+3)？",
            "pass_rule": "能说出这是两次分，不是一次按10分；除数不能随便合并。",
        },
        "parent_card": {
            "before": ["先问精神状态：绿/黄/红。", "告诉船长：今天只打一只Boss。"],
            "during": ["不会时允许点提示，但记录提示次数。", "大副只追问为什么，不连续讲课。"],
            "after": ["导出 Day4-result.json。", "录 Boss 讲题语音，放入 Day4 提交文件夹。"],
            "inputs": ["Day4-result.json", "Boss讲题语音", "课堂雷达"],
            "outputs": ["Day5回炉练习", "技能地图更新", "鱼币结算"],
        },
        "classroom_radar": [
            "语文今天讲到：________________  我记得一个词：________________",
            "数学今天讲到：________________  我觉得：[ ]会 [ ]半会 [ ]不会",
            "英语今天讲到：________________  我记得一句：________________",
        ],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m unittest tests.test_day4_site_flow -v
```

Expected: the new test passes.

## Task 2: Register Day4 In Daily Script

**Files:**
- Modify: `scripts/generate_daily_practice.py`
- Test: `tests/test_day4_site_flow.py`

- [ ] **Step 1: Add failing test**

Append to `Day4SiteFlowTests`:

```python
    def test_daily_script_registers_day4(self) -> None:
        from scripts.generate_daily_practice import build_config_for_day

        config = build_config_for_day("Day4", ROOT)

        self.assertEqual(config.day, "Day4")
        spec = config.spec_builder([])
        self.assertEqual(spec["title"], "Day4-虎鲸队长的除法航线")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_daily_script_registers_day4 -v
```

Expected: fail with `ValueError: No daily builder registered for Day4.`

- [ ] **Step 3: Register Day4 with the daily engine**

Modify `scripts/generate_daily_practice.py` so `build_config_for_day` has:

```python
    if normalized == "Day4":
        from tutor_core.day4_spec import build_day4_spec

        spec = build_day4_spec(root)
        from tutor_core.daily_engine import DailyBuildConfig

        return DailyBuildConfig(
            day="Day4",
            source_grading_path=root / "submissions" / "2026-06-05-Day3" / "web-result-placeholder.json",
            row_reader=lambda _path: [],
            spec_builder=lambda _rows: spec,
        )
```

Keep the existing `Day3` block unchanged.

Also modify `main()` so Day4 does not accidentally settle an empty points ledger before the real Day3 result is graded:

```python
rows = config.row_reader(config.source_grading_path)
if rows:
    settle_session_points(args.root, config.source_grading_path.parent.name, rows)
result = generate_daily_materials(args.root, config)
```

This preserves Day3 behavior because Day3 grading rows are non-empty.

- [ ] **Step 4: Run test**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_daily_script_registers_day4 -v
```

Expected: pass.

## Task 3: Result Export In Day Web Renderer

**Files:**
- Modify: `rendering/day_web.py`
- Test: `tests/test_day4_site_flow.py`

- [ ] **Step 1: Add failing test**

Append:

```python
    def test_day_web_exports_result_json_contract(self) -> None:
        from rendering.day_web import render_practice_html
        from tutor_core.day4_spec import build_day4_spec

        html = render_practice_html(build_day4_spec(ROOT))

        self.assertIn("导出结果", html)
        self.assertIn("downloadResult", html)
        self.assertIn("Day4-result.json", html)
        self.assertIn("hint_count", html)
        self.assertIn("revealed_answer", html)
        self.assertIn("self_check", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_day_web_exports_result_json_contract -v
```

Expected: fail because export fields are missing.

- [ ] **Step 3: Add export button and self-check UI**

In `rendering/day_web.py`, add to the `#progress` section:

```html
<div class="self-check">
  <label>今日能量
    <select data-self-check="energy">
      <option value="green">绿：精神不错</option>
      <option value="yellow">黄：有点累</option>
      <option value="red">红：今天只收工</option>
    </select>
  </label>
  <label>船长感觉
    <input data-self-check="feeling" type="text" placeholder="例如：想继续 / 有点难 / Boss被我抓住了" />
  </label>
</div>
<button type="button" id="downloadResult">导出结果</button>
```

Add JavaScript:

```javascript
function buildResult() {
  const spec = JSON.parse(document.getElementById('practice-spec').textContent);
  const answers = {};
  document.querySelectorAll('[data-answer-for]').forEach((input) => {
    const id = input.dataset.answerFor;
    answers[id] = {
      answer: input.value,
      completed: Boolean(saved['done:' + id]),
      hint_count: Number(saved['hint:' + id] || 0),
      revealed_answer: Boolean(saved['revealed:' + id])
    };
  });
  const radar = {};
  document.querySelectorAll('[data-radar]').forEach((textarea) => {
    radar[textarea.dataset.radar] = textarea.value;
  });
  const self_check = {};
  document.querySelectorAll('[data-self-check]').forEach((input) => {
    self_check[input.dataset.selfCheck] = input.value;
  });
  return {
    day: spec.day,
    title: spec.title,
    completed_at: new Date().toISOString(),
    answers,
    radar,
    self_check
  };
}

document.getElementById('downloadResult').addEventListener('click', () => {
  const spec = JSON.parse(document.getElementById('practice-spec').textContent);
  const blob = new Blob([JSON.stringify(buildResult(), null, 2)], { type: 'application/json;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = spec.day + '-result.json';
  link.click();
  URL.revokeObjectURL(link.href);
});
```

When answer is revealed, also set:

```javascript
saved['revealed:' + button.dataset.answerToggle] = true;
localStorage.setItem(storageKey, JSON.stringify(saved));
```

- [ ] **Step 4: Run test**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_day_web_exports_result_json_contract -v
```

Expected: pass.

## Task 4: Captain Deck Homepage

**Files:**
- Create: `rendering/captain_site.py`
- Modify: `scripts/generate_web_practice.py`
- Test: `tests/test_day4_site_flow.py`

- [ ] **Step 1: Add failing test**

Append:

```python
    def test_renders_captain_deck_homepage(self) -> None:
        from rendering.captain_site import render_captain_deck
        from tutor_core.day4_spec import build_day4_spec

        html = render_captain_deck([build_day4_spec(ROOT)])

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Captain Deck", html)
        self.assertIn("今日航线", html)
        self.assertIn("Day4-虎鲸队长的除法航线.html", html)
        self.assertIn("Switch2 1876/3500", html)
        self.assertIn("知识鱼图鉴", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_renders_captain_deck_homepage -v
```

Expected: fail with `ModuleNotFoundError: No module named 'rendering.captain_site'`.

- [ ] **Step 3: Implement homepage renderer**

Create `rendering/captain_site.py`:

```python
from __future__ import annotations

import html
from typing import Any


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_captain_deck(specs: list[dict[str, Any]]) -> str:
    latest = specs[-1]
    points = latest["points"]
    cards = "\n".join(
        f"""
        <a class="mission" href="{_escape(spec['title'])}.html">
          <span>{_escape(spec['day'])}</span>
          <strong>{_escape(spec['title'])}</strong>
          <em>{_escape(spec['focus'])}</em>
        </a>
        """
        for spec in specs
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Captain Deck</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif; background: #f5f5f7; color: #1d1d1f; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 32px 22px; }}
    h1 {{ font-size: 46px; margin: 0 0 10px; }}
    .summary {{ color: #6e6e73; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; margin-top: 22px; }}
    .panel, .mission {{ background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 8px; padding: 22px; text-decoration: none; color: inherit; }}
    .missions {{ display: grid; gap: 12px; }}
    .mission span {{ color: #0071e3; font-weight: 800; }}
    .mission strong {{ display: block; font-size: 24px; margin: 8px 0; }}
    .mission em {{ color: #6e6e73; font-style: normal; }}
    .stat {{ font-size: 28px; font-weight: 800; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} h1 {{ font-size: 36px; }} }}
  </style>
</head>
<body>
  <main>
    <h1>Captain Deck</h1>
    <p class="summary">袁佳乐的专属学习游戏账号</p>
    <section class="grid">
      <div class="panel">
        <h2>今日航线</h2>
        <div class="missions">{cards}</div>
      </div>
      <aside class="panel">
        <h2>知识鱼图鉴</h2>
        <p class="stat">Switch2 {points["current"]}/{points["goal"]}</p>
        <p class="summary">今日目标：完成练习，抓回一条薄弱点知识鱼。</p>
      </aside>
    </section>
  </main>
</body>
</html>
"""
```

- [ ] **Step 4: Run test**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_renders_captain_deck_homepage -v
```

Expected: pass.

## Task 5: Generate Day4 Website Files

**Files:**
- Modify: `scripts/generate_web_practice.py`
- Test: `tests/test_day4_site_flow.py`

- [ ] **Step 1: Add failing test**

Append:

```python
    def test_generates_day4_site_files(self) -> None:
        import tempfile
        from scripts.generate_web_practice import generate_web_practice_from_spec, generate_captain_deck
        from tutor_core.day4_spec import build_day4_spec

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            spec = build_day4_spec(ROOT)
            page = generate_web_practice_from_spec(spec, out)
            index = generate_captain_deck([spec], out)

            self.assertEqual(page.name, "Day4-虎鲸队长的除法航线.html")
            self.assertEqual(index.name, "index.html")
            self.assertTrue(page.exists())
            self.assertTrue(index.exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_generates_day4_site_files -v
```

Expected: fail because `generate_web_practice_from_spec` and `generate_captain_deck` are missing.

- [ ] **Step 3: Add generation helpers**

Modify `scripts/generate_web_practice.py`:

```python
from rendering.captain_site import render_captain_deck


def generate_web_practice_from_spec(spec: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{spec['title']}.html"
    output.write_text(render_practice_html(spec), encoding="utf-8")
    return output


def generate_web_practice(spec_path: Path, output_dir: Path) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    return generate_web_practice_from_spec(spec, output_dir)


def generate_captain_deck(specs: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "index.html"
    output.write_text(render_captain_deck(specs), encoding="utf-8")
    return output
```

Add optional CLI flag:

```python
parser.add_argument("--index", action="store_true", help="Also generate Captain Deck index.html.")
```

After generating the practice page:

```python
output = generate_web_practice(args.spec, args.output_dir)
if args.index:
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    generate_captain_deck([spec], args.output_dir)
print(output)
```

- [ ] **Step 4: Run test**

Run:

```powershell
python -m unittest tests.test_day4_site_flow.Day4SiteFlowTests.test_generates_day4_site_files -v
```

Expected: pass.

## Task 6: Documentation For Nightly Operation

**Files:**
- Create: `practice/results/README.md`
- Modify: `项目运行手册.md`

- [ ] **Step 1: Create result contract README**

Create `practice/results/README.md`:

```markdown
# Web Practice Results

Browser practice pages export `DayN-result.json` files here after the user downloads them from the page.

Required nightly files:

- `DayN-result.json`: exported from the web practice page
- `Boss讲题音频`: 30-60 seconds, child explains the Boss concept
- `课堂雷达音频或文字`: Chinese, math, English classroom progress
- Optional paper photo: scratch work or vertical calculations

The next day's generator reads these files to decide:

- which skills were mastered
- which wrong or hinted questions return tomorrow
- whether the child was tired
- how many Switch2 fish coins to add
```

- [ ] **Step 2: Update runbook**

Append to `项目运行手册.md`:

```markdown
## Day4 网页优先流程

1. 生成 Day4 spec/PDF/submission packet:
   `python scripts\generate_daily_practice.py --day Day4`
2. 生成网页练习台和首页:
   `python scripts\generate_web_practice.py --spec practice\specs\Day4-虎鲸队长的除法航线.json --index`
3. 打开:
   `practice\web\index.html`
4. 船长完成网页练习后点击“导出结果”。
5. 大副把 `Day4-result.json`、Boss讲题音频、课堂雷达放入 `submissions\2026-06-06-Day4\`。
6. 第二天由 Day5 生成器读取结果并安排回炉。
```

- [ ] **Step 3: Run full tests**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass.

## Task 7: Manual Verification

**Files:**
- Generated: `practice/web/index.html`
- Generated: `practice/web/Day4-虎鲸队长的除法航线.html`

- [ ] **Step 1: Generate Day4 materials**

Run:

```powershell
python scripts\generate_daily_practice.py --day Day4
python scripts\generate_web_practice.py --spec practice\specs\Day4-虎鲸队长的除法航线.json --index
```

Expected:

```text
practice\specs\Day4-虎鲸队长的除法航线.json
Day4-虎鲸队长的除法航线.pdf
submissions\2026-06-06-Day4
practice\web\Day4-虎鲸队长的除法航线.html
practice\web\index.html
```

- [ ] **Step 2: Static HTML sanity check**

Run:

```powershell
Select-String -Path practice\web\index.html -Pattern "Captain Deck|今日航线|Switch2 1876/3500"
Select-String -Path practice\web\Day4-虎鲸队长的除法航线.html -Pattern "导出结果|Day4-result.json|D4-B1|费曼"
Select-String -Path practice\web\Day4-虎鲸队长的除法航线.html -Pattern "https://"
```

Expected:

- First command finds all homepage terms.
- Second command finds all Day4 terms.
- Third command finds nothing.

## Non-Goals For Day4 Night Build

- No user account login.
- No payment, membership, ranking, or social features.
- No online database.
- No unlimited animations during problem solving.
- No auto-grading open-ended Chinese/English responses until we have several real samples.
- No replacing paper scratch work; paper remains allowed for vertical calculation and drafts.

## Self-Review

- Spec coverage: The plan covers Day4 spec generation, website homepage, web practice flow, result export, parent inputs, and next-day data handoff.
- Placeholder scan: No `TBD`, `TODO`, or open implementation blanks remain. The only optional items are explicitly marked as non-goals or manual verification.
- Type consistency: The planned functions are `build_day4_spec`, `render_captain_deck`, `generate_web_practice_from_spec`, and `generate_captain_deck`; tests use the same names.
