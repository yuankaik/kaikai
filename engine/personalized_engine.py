"""
王牌钓手 个性化学习引擎（上层）
==============================
核心循环：练习 → 批改 → 掌握度分析 → 根因追溯 → 变式生成 → 次日规划

依赖底层：
- knowledge_atlas.json (91知识点)
- question_bank.json (题库)
- prerequisite_graph.py (前置依赖)
- knowledge_bank.py (题库管理)
"""

import json
import random
import math
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, date
from collections import defaultdict
from typing import Optional

from prerequisite_graph import PrerequisiteGraph
from knowledge_bank import KnowledgeBank

BANK_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class QuestionResult:
    """单题批改结果（兼容现有 auto_grader.GradeResult）"""
    question_id: str
    knowledge_id: str = ""
    knowledge_name: str = ""
    subject: str = ""
    correct: bool = False
    state: str = "ok"       # ok / review / bad
    student_answer: str = ""
    expected_answer: str = ""
    difficulty: int = 1


@dataclass
class KnowledgeMastery:
    """知识点掌握度"""
    kp_id: str
    kp_name: str
    subject: str
    category: str = ""
    mastery_score: float = 0.0       # 0.0-1.0 掌握度
    total_attempts: int = 0
    correct_count: int = 0
    consecutive_correct: int = 0      # 连续正确次数
    last_seen: str = ""               # 最后练习日期
    state: str = "locked"             # locked/unlocked/practicing/mastered
    streak_best: int = 0              # 最佳连续正确


@dataclass
class DailyReport:
    """每日练习报告"""
    day: str
    title: str = ""
    total_questions: int = 0
    correct_count: int = 0
    accuracy: float = 0.0
    points_earned: int = 0
    weak_points: list = field(default_factory=list)       # 薄弱知识点
    root_causes: list = field(default_factory=list)        # 根因知识点
    newly_mastered: list = field(default_factory=list)     # 新掌握的知识点
    mood: str = ""                                         # 船长情绪：绿/黄/红


class PersonalizedEngine:
    """个性化学习引擎 —— 上层核心"""

    def __init__(self, bank_dir: Path = BANK_DIR):
        self.bank_dir = bank_dir
        self.bank = KnowledgeBank(bank_dir)
        self.graph = PrerequisiteGraph(bank_dir / "knowledge_atlas.json")
        self.mastery = self._load_mastery()
        self.history = self._load_history()

    # ========== 掌握度管理 ==========

    def _load_mastery(self) -> dict:
        """加载掌握度数据"""
        path = self.bank_dir / "mastery.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {kp["kp_id"]: KnowledgeMastery(**kp)
                    for kp in data.get("knowledge_mastery", [])}
        return {}

    def _save_mastery(self):
        """保存掌握度数据"""
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "knowledge_mastery": [
                {
                    "kp_id": m.kp_id,
                    "kp_name": m.kp_name,
                    "subject": m.subject,
                    "category": m.category,
                    "mastery_score": m.mastery_score,
                    "total_attempts": m.total_attempts,
                    "correct_count": m.correct_count,
                    "consecutive_correct": m.consecutive_correct,
                    "last_seen": m.last_seen,
                    "state": m.state,
                    "streak_best": m.streak_best,
                }
                for m in self.mastery.values()
            ],
        }
        with open(self.bank_dir / "mastery.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> list:
        """加载练习历史"""
        path = self.bank_dir / "practice_history.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("history", [])
        return []

    def _save_history(self):
        """保存练习历史"""
        with open(self.bank_dir / "practice_history.json", "w", encoding="utf-8") as f:
            json.dump({"version": "1.0", "history": self.history}, f,
                      ensure_ascii=False, indent=2)

    def get_or_create_mastery(self, kp_id: str) -> KnowledgeMastery:
        """获取或创建掌握度记录"""
        if kp_id in self.mastery:
            return self.mastery[kp_id]

        kp = self.graph.get_kp(kp_id)
        if not kp:
            return KnowledgeMastery(kp_id=kp_id, kp_name=kp_id, subject="")

        m = KnowledgeMastery(
            kp_id=kp_id,
            kp_name=kp.get("name", kp_id),
            subject=kp.get("subject", ""),
            category=kp.get("category", ""),
            state=kp.get("status", "locked"),
        )
        self.mastery[kp_id] = m
        return m

    # ========== 提交练习结果 ==========

    def submit_results(
        self,
        day: str,
        title: str,
        results: list[QuestionResult],
        mood: str = "",
    ) -> DailyReport:
        """
        提交一天的练习批改结果。
        自动更新掌握度、分析薄弱点、追溯根因。
        """
        report = DailyReport(
            day=day,
            title=title,
            total_questions=len(results),
            correct_count=sum(1 for r in results if r.correct),
            mood=mood,
        )
        report.accuracy = (report.correct_count / max(len(results), 1)) * 100

        # 更新每个知识点的掌握度
        today = date.today().isoformat()
        for r in results:
            if not r.knowledge_id:
                continue

            m = self.get_or_create_mastery(r.knowledge_id)
            m.total_attempts += 1
            m.last_seen = today

            if r.correct:
                m.correct_count += 1
                m.consecutive_correct += 1
                m.streak_best = max(m.streak_best, m.consecutive_correct)
            else:
                m.consecutive_correct = 0

            # 掌握度计算：考虑正确率 + 连续正确 + 最近表现
            accuracy = m.correct_count / max(m.total_attempts, 1)
            streak_bonus = min(m.consecutive_correct / 5, 0.3)  # 连续5次正确加0.3
            m.mastery_score = min(accuracy + streak_bonus, 1.0)

            # 状态判定
            if m.mastery_score >= 0.9 and m.total_attempts >= 5:
                if m.state != "mastered":
                    m.state = "mastered"
                    report.newly_mastered.append(r.knowledge_id)
            elif m.mastery_score >= 0.5 or m.total_attempts >= 1:
                m.state = "practicing"
            elif m.state == "locked" and m.total_attempts > 0:
                m.state = "unlocked"

            # 薄弱点
            if m.mastery_score < 0.6:
                if r.knowledge_id not in report.weak_points:
                    report.weak_points.append(r.knowledge_id)

        # 根因分析
        if report.weak_points:
            root_causes = self.graph.find_root_causes(report.weak_points)
            all_roots = set()
            for info in root_causes.values():
                all_roots.add(info["root_cause"])
            report.root_causes = list(all_roots)

        # 积分：每道正确数学/英语1分，boss题2分，开放题1分
        for r in results:
            if r.correct:
                if r.difficulty >= 2:
                    report.points_earned += 2
                else:
                    report.points_earned += 1

        # 保存
        self._save_mastery()
        self.history.append({
            "day": day,
            "title": title,
            "date": today,
            "accuracy": report.accuracy,
            "weak_points": report.weak_points,
            "root_causes": report.root_causes,
            "points_earned": report.points_earned,
            "mood": mood,
        })
        self._save_history()

        return report

    # ========== 生成次日练习 ==========

    def plan_next_day(
        self,
        next_day: str,
        title: str = "",
        target_questions: int = 20,
    ) -> dict:
        """
        根据当前掌握度，自动规划次日练习。
        
        策略：
        1. 优先回炉：根因知识点 > 薄弱知识点
        2. 巩固已掌握：随机抽查1-2道已掌握的防遗忘
        3. 新知识点：解锁一个前置条件满足的新知识点
        4. 课堂雷达：始终包含
        5. 费曼：针对最薄弱的知识点
        """
        # 1. 找出需要回炉的知识点（按掌握度排序，最低优先）
        weak_sorted = sorted(
            [m for m in self.mastery.values()
             if m.state in ("practicing", "unlocked") and m.mastery_score < 0.7],
            key=lambda m: m.mastery_score,
        )
        
        # 2. 已掌握的用于抽查
        mastered = [m for m in self.mastery.values()
                    if m.state == "mastered"]
        
        # 3. 可解锁的新知识点
        unlockable = [kp for kp in self.graph.get_unlockable()
                      if kp["id"] not in self.mastery
                      or self.mastery[kp["id"]].state == "locked"]

        sections = []
        exclude_ids = set()

        # --- Rod 1: 回炉薄弱点（最多6题，取最弱的3个知识点） ---
        warmup_kps = [m.kp_id for m in weak_sorted[:3]]
        if warmup_kps:
            warmup_qs = []
            for kp_id in warmup_kps:
                qs = self.bank.pick(kp_id=kp_id, count=2, exclude_ids=exclude_ids)
                for q in qs:
                    exclude_ids.add(q["id"])
                warmup_qs.extend(qs)
            if warmup_qs:
                sections.append({
                    "title": "Normal Rod - 回炉薄弱点",
                    "hint": f"上次没咬牢的鱼，再抓一次",
                    "questions": warmup_qs,
                })

        # --- Rod 2: 根因修复（最深层前置，2-4题） ---
        root_ids = set()
        if weak_sorted:
            for m in weak_sorted[:2]:
                root_result = self.graph.find_root_causes([m.kp_id])
                for info in root_result.values():
                    root_ids.add(info["root_cause"])
            
            root_qs = []
            for kp_id in list(root_ids)[:2]:
                qs = self.bank.pick(kp_id=kp_id, count=2, exclude_ids=exclude_ids)
                for q in qs:
                    exclude_ids.add(q["id"])
                root_qs.extend(qs)
            if root_qs:
                sections.append({
                    "title": "Monster Rod - 根因修复",
                    "hint": "从根源上堵住漏洞",
                    "questions": root_qs,
                })

        # --- Rod 3: 巩固抽查（随机抽已掌握的，1-2题） ---
        if mastered:
            spot_kp = random.choice(mastered).kp_id
            spot_qs = self.bank.pick(kp_id=spot_kp, count=1, exclude_ids=exclude_ids)
            if spot_qs:
                for q in spot_qs:
                    exclude_ids.add(q["id"])
                sections.append({
                    "title": "Super Rod - 巩固抽查",
                    "hint": "看看之前的鱼还在不在",
                    "questions": spot_qs,
                })

        # --- Rod 4: 新知识点（1个，3-4题） ---
        if unlockable:
            new_kp = unlockable[0]
            new_qs = self.bank.pick(kp_id=new_kp["id"], count=3, exclude_ids=exclude_ids)
            if new_qs:
                for q in new_qs:
                    exclude_ids.add(q["id"])
                sections.append({
                    "title": f"Legend Rod - 新海域：{new_kp['name']}",
                    "hint": new_kp.get("description", "新的知识鱼等你来钓"),
                    "questions": new_qs,
                })

        # --- Rod 5: 课堂雷达 ---
        sections.append({
            "title": "Classroom Radar - 三科课堂雷达",
            "hint": "和学校课堂保持对齐",
            "questions": [
                self._make_radar_q("C-VOCAB-001", "写出今天语文课你记住的一个词，并造一个短句。"),
                self._make_radar_q("E-CLASS-001", "写出今天英语课你记住的一句话。"),
                self._make_radar_q("G-SYNC-001", "今天数学课讲到哪里？写一个关键词。"),
            ],
        })

        # --- 费曼环节 ---
        feynman_target = ""
        if weak_sorted:
            weakest = weak_sorted[0]
            feynman_target = f"{weakest.kp_name}（掌握度 {weakest.mastery_score:.0%}）"

        total_q = sum(len(s.get("questions", [])) for s in sections)
        
        spec = {
            "day": next_day,
            "title": title or f"{next_day}-动态规划练习",
            "mode": "personalized",
            "focus": f"自动规划：{len(weak_sorted)}个薄弱点 + {len(unlockable)}个可解锁",
            "total_questions": total_q,
            "sections": sections,
            "feynman": {
                "target": feynman_target,
                "prompt": "请船长任选一道错题，用一句话讲清楚为什么错。",
                "pass_rule": "能说出关键规则即可。",
            },
            "plan_meta": {
                "weak_points": [m.kp_name for m in weak_sorted[:5]],
                "root_causes": [self.graph.get_name(rc) for rc in root_ids] if weak_sorted else [],
                "mastered_count": len(mastered),
                "unlockable_count": len(unlockable),
            },
        }
        return spec

    def _make_radar_q(self, kp_id: str, prompt: str) -> dict:
        kp = self.graph.get_kp(kp_id)
        return {
            "id": f"RADAR-{kp_id}-{random.randint(100,999)}",
            "knowledge_id": kp_id,
            "knowledge_name": kp.get("name", "") if kp else "",
            "subject": kp.get("subject", "") if kp else "",
            "kind": "practice",
            "difficulty": 1,
            "prompt": prompt,
            "answer": "开放题",
            "unlock_reward": "课堂贝壳",
            "source_day": "auto-radar",
            "source_section": "课堂雷达",
            "source": "自动生成",
            "tags": [],
        }

    # ========== 变式题生成 ==========

    def generate_variation(self, question: dict, kp_id: str) -> dict:
        """
        基于原题生成一道变式题。
        策略：改数字、换情境、调问题方向。
        """
        import re
        
        prompt = question.get("prompt", "")
        answer = question.get("answer", "")
        kind = question.get("kind", "practice")
        
        # 策略1：换数字（数学题最有效）
        numbers = re.findall(r'\d+', prompt)
        new_prompt = prompt
        new_answer = answer
        
        if numbers and kind != "vocab":
            for n in numbers[:3]:  # 最多换3个数字
                old_n = int(n)
                # 加/减一个小的随机偏移
                offset = random.choice([-2, -1, 1, 2, 3, 5, 10])
                new_n = max(1, old_n + offset)
                new_prompt = new_prompt.replace(n, str(new_n), 1)
                if n in answer:
                    new_answer = new_answer.replace(n, str(new_n), 1)

        # 策略2：换顺序/方向
        if "＞" in prompt or "＜" in prompt or "比较" in prompt:
            # 交换比较方向
            new_prompt = new_prompt.replace("最大", "最小") if "最大" in new_prompt else new_prompt

        # 策略3：英语词汇换词
        if kind == "vocab":
            common_words = ["morning", "afternoon", "evening", "night", "today", "tomorrow"]
            for w in common_words:
                if w in prompt.lower():
                    new_word = random.choice([x for x in common_words if x != w])
                    new_prompt = prompt.lower().replace(w, new_word)
                    new_answer = answer.lower().replace(w, new_word)
                    break

        return {
            "id": f"VAR-{question.get('id', 'UNK')}-{random.randint(10,99)}",
            "knowledge_id": kp_id,
            "knowledge_name": question.get("knowledge_name", ""),
            "subject": question.get("subject", ""),
            "kind": kind,
            "difficulty": question.get("difficulty", 1),
            "prompt": new_prompt,
            "answer": new_answer,
            "unlock_reward": "变式鱼",
            "source_day": "variation",
            "source_section": "变式生成",
            "source": f"变式自 {question.get('id', '?')}",
            "tags": ["variation"],
            "parent_id": question.get("id", ""),
        }

    # ========== 进度看板 ==========

    def dashboard(self) -> dict:
        """生成学习进度看板"""
        total_kp = len(self.graph.kp_map)
        all_mastery = list(self.mastery.values())
        
        mastered = [m for m in all_mastery if m.state == "mastered"]
        practicing = [m for m in all_mastery if m.state == "practicing"]
        weak = [m for m in all_mastery if m.mastery_score < 0.5 and m.total_attempts > 0]
        
        # 计算知识鱼数
        fish_caught = sum(
            self.graph.get_kp(m.kp_id).get("fish_value", 1)
            for m in mastered
        ) if mastered else 0

        # 课程雷达：最近练习的各学科准确率
        recent = self.history[-7:] if len(self.history) >= 7 else self.history
        
        return {
            "title": "航海图进度看板",
            "knowledge_mastery": {
                "total": total_kp,
                "mastered": len(mastered),
                "practicing": len(practicing),
                "weak": len(weak),
                "untouched": total_kp - len(all_mastery),
                "mastery_rate": f"{len(mastered)/max(total_kp,1)*100:.1f}%",
            },
            "fish_tally": {
                "caught": fish_caught,
                "target": 93,
                "progress": f"{fish_caught}/93",
            },
            "top_weak": [
                {"name": m.kp_name, "score": f"{m.mastery_score:.0%}",
                 "attempts": m.total_attempts, "category": m.category}
                for m in sorted(weak, key=lambda x: x.mastery_score)[:5]
            ],
            "recent_accuracy": [
                {"day": h.get("day", "?"), "accuracy": h.get("accuracy", 0)}
                for h in recent[-7:]
            ],
            "streak": {
                "best_kp": max(all_mastery, key=lambda m: m.streak_best).kp_name if all_mastery else "无",
                "best_streak": max((m.streak_best for m in all_mastery), default=0),
            },
        }

    def get_variations_for_weak_points(self, count: int = 5) -> list:
        """为当前薄弱点生成变式题"""
        weak = [m for m in self.mastery.values()
                if m.mastery_score < 0.6 and m.total_attempts > 0]
        
        variations = []
        for m in weak[:3]:  # 最多取3个薄弱知识点
            qs = self.bank.get_questions_by_kp(m.kp_id)
            if qs:
                for q in qs[:2]:  # 每个点取2题做变式
                    var = self.generate_variation(q, m.kp_id)
                    variations.append(var)
        
        return variations[:count]


# ========== CLI ==========

def cli():
    import sys

    engine = PersonalizedEngine()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python personalized_engine.py dashboard       — 进度看板")
        print("  python personalized_engine.py mastery [kp_id] — 查看掌握度")
        print("  python personalized_engine.py plan <day>      — 生成次日练习")
        print("  python personalized_engine.py variations      — 生成薄弱点变式题")
        print("  python personalized_engine.py simulate        — 模拟一轮练习循环")
        return

    cmd = sys.argv[1]

    if cmd == "dashboard":
        d = engine.dashboard()
        print(json.dumps(d, ensure_ascii=False, indent=2))

    elif cmd == "mastery":
        kp_id = sys.argv[2] if len(sys.argv) > 2 else None
        if kp_id:
            m = engine.get_or_create_mastery(kp_id)
            print(f"知识点: {m.kp_name} ({m.kp_id})")
            print(f"  掌握度: {m.mastery_score:.0%}")
            print(f"  状态: {m.state}")
            print(f"  总练习: {m.total_attempts} | 正确: {m.correct_count}")
            print(f"  连续正确: {m.consecutive_correct} | 最佳: {m.streak_best}")
        else:
            # 列出所有有数据的
            for m in sorted(engine.mastery.values(),
                           key=lambda x: x.mastery_score):
                if m.total_attempts > 0:
                    bar = "█" * int(m.mastery_score * 20)
                    print(f"  [{m.state:10s}] {m.kp_name:20s} {m.mastery_score:.0%} {bar} ({m.total_attempts}次)")

    elif cmd == "plan":
        day = sys.argv[2] if len(sys.argv) > 2 else f"Day{len(engine.history)+1}"
        title = sys.argv[3] if len(sys.argv) > 3 else ""
        spec = engine.plan_next_day(day, title)
        
        output_path = engine.bank_dir.parent / "practice" / "specs" / f"{day}-个性化规划.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        
        print(f"生成 {spec['total_questions']} 题，保存到 {output_path}")
        for s in spec["sections"]:
            print(f"  [{s['title']}] {len(s.get('questions',[]))}题")

    elif cmd == "variations":
        vars_q = engine.get_variations_for_weak_points(5)
        for v in vars_q:
            print(f"[{v['knowledge_name']}] {v['prompt'][:60]}...")
            print(f"  → {v['answer']}")

    elif cmd == "simulate":
        simulate(engine)


def simulate(engine: PersonalizedEngine):
    """模拟一轮练习循环：批改 → 分析 → 规划"""
    print("=" * 50)
    print("王牌钓手 模拟练习循环")
    print("=" * 50)
    
    # 从题库随机抽题模拟一次练习
    all_qs = engine.bank.questions
    if not all_qs:
        print("题库为空，请先加载题库")
        return

    # 模拟：随机取10题，随机对错
    results = []
    sample_qs = random.sample(all_qs, min(10, len(all_qs)))
    for q in sample_qs:
        correct = random.random() > 0.4  # 60%正确率
        results.append(QuestionResult(
            question_id=q["id"],
            knowledge_id=q.get("knowledge_id", ""),
            knowledge_name=q.get("knowledge_name", ""),
            subject=q.get("subject", ""),
            correct=correct,
            state="ok" if correct else "bad",
            student_answer="模拟答案",
            expected_answer=q.get("answer", ""),
            difficulty=q.get("difficulty", 1),
        ))

    # 提交结果
    report = engine.submit_results(
        day=f"Day{len(engine.history)+1}",
        title="模拟练习",
        results=results,
        mood="绿",
    )

    print(f"\n📊 练习报告: {report.day}")
    print(f"  准确率: {report.accuracy:.0f}% ({report.correct_count}/{report.total_questions})")
    print(f"  积分: +{report.points_earned}")
    print(f"  薄弱点: {[engine.graph.get_name(kp) for kp in report.weak_points]}")
    print(f"  根因: {[engine.graph.get_name(kp) for kp in report.root_causes]}")

    # 生成次日规划
    plan = engine.plan_next_day(f"Day{len(engine.history)+1}")
    print(f"\n📋 次日规划: {plan['title']}")
    print(f"  总题数: {plan['total_questions']}")
    for s in plan["sections"]:
        print(f"  [{s['title']}] {len(s.get('questions',[]))}题")
    
    print(f"\n🎯 费曼目标: {plan['feynman']['target']}")


if __name__ == "__main__":
    cli()
