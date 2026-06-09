"""
王牌钓手 知识点题库管理工具
========================
功能：
- 加载知识图谱和题库
- 按知识点/学科/难度查询题目
- 随机抽题生成每日练习
- 添加新题目
- 导出练习 spec JSON
"""

import json
import random
from pathlib import Path
from typing import Optional

BANK_DIR = Path(__file__).resolve().parent.parent / "data"


class KnowledgeBank:
    """知识点题库管理器"""

    def __init__(self, bank_dir: Path = BANK_DIR):
        self.bank_dir = bank_dir
        self.atlas = self._load("knowledge_atlas.json")
        self.questions = self._load("question_bank.json").get("questions", [])
        self._kp_index = self._build_kp_index()
        self._by_subject = self._build_subject_index()

    def _load(self, filename: str) -> dict:
        path = self.bank_dir / filename
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_kp_index(self) -> dict:
        """按知识点ID索引题目"""
        idx = {}
        for q in self.questions:
            kp_id = q.get("knowledge_id", "")
            if kp_id not in idx:
                idx[kp_id] = []
            idx[kp_id].append(q)
        return idx

    def _build_subject_index(self) -> dict:
        """按学科索引题目"""
        idx = {}
        for q in self.questions:
            subj = q.get("subject", "其他")
            if subj not in idx:
                idx[subj] = []
            idx[subj].append(q)
        return idx

    # ---------- 查询 ----------

    def get_knowledge_point(self, kp_id: str) -> Optional[dict]:
        """获取知识点详情"""
        for kp in self.atlas.get("knowledge_points", []):
            if kp["id"] == kp_id:
                return kp
        return None

    def get_kp_name(self, kp_id: str) -> str:
        kp = self.get_knowledge_point(kp_id)
        return kp["name"] if kp else kp_id

    def list_knowledge_points(
        self, subject: str = None, category: str = None, status: str = None
    ) -> list:
        """列出知识点"""
        result = []
        for kp in self.atlas.get("knowledge_points", []):
            if subject and kp["subject"] != subject:
                continue
            if category and kp["category"] != category:
                continue
            if status and kp["status"] != status:
                continue
            result.append(kp)
        return result

    def get_questions_by_kp(self, kp_id: str) -> list:
        """按知识点查询题目"""
        return self._kp_index.get(kp_id, [])

    def get_questions_by_subject(self, subject: str) -> list:
        """按学科查询题目"""
        return self._by_subject.get(subject, [])

    def query(
        self,
        kp_id: str = None,
        subject: str = None,
        difficulty: int = None,
        kind: str = None,
        limit: int = 100,
    ) -> list:
        """组合查询"""
        results = self.questions
        if kp_id:
            results = [q for q in results if q["knowledge_id"] == kp_id]
        if subject:
            results = [q for q in results if q["subject"] == subject]
        if difficulty:
            results = [q for q in results if q["difficulty"] == difficulty]
        if kind:
            results = [q for q in results if q["kind"] == kind]
        return results[:limit]

    # ---------- 抽题 ----------

    def pick(
        self,
        kp_id: str = None,
        subject: str = None,
        difficulty: int = None,
        count: int = 1,
        exclude_ids: set = None,
    ) -> list:
        """随机抽题"""
        pool = self.query(kp_id=kp_id, subject=subject, difficulty=difficulty)
        if exclude_ids:
            pool = [q for q in pool if q["id"] not in exclude_ids]
        if len(pool) <= count:
            return pool
        return random.sample(pool, count)

    # ---------- 生成每日练习 ----------

    def generate_daily_spec(
        self,
        day: str,
        title: str = "",
        focus: str = "",
        math_warmup: list = None,
        math_boss: list = None,
        math_skill: list = None,
        english_vocab: list = None,
        english_grammar: list = None,
        classroom_radar: bool = True,
        feynman_target: str = "",
    ) -> dict:
        """
        按知识点ID列表生成每日练习spec。
        math_warmup = ["M-CALC-003", ...] 等知识点ID列表。
        每个知识点随机抽1-2题。
        """
        sections = []
        exclude = set()

        if math_warmup:
            questions = []
            for kp_id in math_warmup:
                qs = self.pick(kp_id=kp_id, count=2, exclude_ids=exclude)
                for q in qs:
                    exclude.add(q["id"])
                questions.extend(qs)
            sections.append({
                "title": "Normal Rod - 热身航线",
                "hint": "先稳住基础分",
                "questions": questions,
            })

        if math_boss:
            questions = []
            for kp_id in math_boss:
                qs = self.pick(kp_id=kp_id, difficulty=2, count=2, exclude_ids=exclude)
                for q in qs:
                    exclude.add(q["id"])
                questions.extend(qs)
            sections.append({
                "title": "Monster Rod - Boss识别",
                "hint": "今天的目标Boss",
                "questions": questions,
            })

        if math_skill:
            questions = []
            for kp_id in math_skill:
                qs = self.pick(kp_id=kp_id, count=2, exclude_ids=exclude)
                for q in qs:
                    exclude.add(q["id"])
                questions.extend(qs)
            sections.append({
                "title": "Super Rod - 核心技能",
                "hint": "每题打一个明确技能点",
                "questions": questions,
            })

        if english_vocab:
            questions = []
            for kp_id in english_vocab:
                qs = self.pick(kp_id=kp_id, count=3, exclude_ids=exclude)
                for q in qs:
                    exclude.add(q["id"])
                questions.extend(qs)
            sections.append({
                "title": "English Rod - 词汇补给",
                "hint": "每天几词，日积月累",
                "questions": questions,
            })

        if english_grammar:
            questions = []
            for kp_id in english_grammar:
                qs = self.pick(kp_id=kp_id, count=2, exclude_ids=exclude)
                for q in qs:
                    exclude.add(q["id"])
                questions.extend(qs)
            sections.append({
                "title": "English Rod - 语法小Boss",
                "hint": "句型语法的专项练习",
                "questions": questions,
            })

        if classroom_radar:
            questions = [
                self._make_question("C-VOCAB-001", "写出今天语文课你记住的一个词，并造一个短句。", "开放题", 1),
                self._make_question("E-CLASS-001", "写出今天英语课你记住的一句话。", "开放题", 1),
                self._make_question("G-SYNC-001", "今天数学课讲到哪里？写一个关键词。", "开放题", 1),
            ]
            sections.append({
                "title": "Legend Rod - 三科课堂雷达",
                "hint": "和学校课堂保持对齐",
                "questions": questions,
            })

        total_q = sum(len(s.get("questions", [])) for s in sections)

        spec = {
            "day": day,
            "title": title or day,
            "mode": "bank-generated",
            "focus": focus,
            "total_questions": total_q,
            "sections": sections,
            "feynman": {
                "target": feynman_target or "未指定",
                "prompt": "请船长任选一道错题，用一句话讲清楚为什么错。",
                "pass_rule": "能说出关键规则即可。",
            },
        }
        return spec

    def _make_question(self, kp_id: str, prompt: str, answer: str, difficulty: int) -> dict:
        """构造一个简单的课堂雷达/开放题"""
        kp_name = self.get_kp_name(kp_id)
        kp = self.get_knowledge_point(kp_id)
        return {
            "id": f"GEN-{kp_id}-{random.randint(100,999)}",
            "knowledge_id": kp_id,
            "knowledge_name": kp_name,
            "subject": kp["subject"] if kp else "通用",
            "kind": "practice",
            "difficulty": difficulty,
            "prompt": prompt,
            "answer": answer,
            "unlock_reward": "",
            "source_day": "auto-generated",
            "source_section": "",
            "source": "题库自动生成",
            "tags": [],
        }

    # ---------- 添加/管理 ----------

    def add_question(
        self,
        kp_id: str,
        subject: str,
        prompt: str,
        answer: str,
        difficulty: int = 1,
        kind: str = "practice",
    ) -> str:
        """添加新题目到题库"""
        kp_name = self.get_kp_name(kp_id)
        new_id = f"Q{len(self.questions) + 1:04d}"
        q = {
            "id": new_id,
            "legacy_id": "",
            "knowledge_id": kp_id,
            "knowledge_name": kp_name,
            "subject": subject,
            "kind": kind,
            "difficulty": difficulty,
            "prompt": prompt,
            "answer": answer,
            "unlock_reward": "",
            "source_day": "manual-add",
            "source_section": "",
            "source": "手动添加",
            "tags": [],
        }
        self.questions.append(q)
        if kp_id not in self._kp_index:
            self._kp_index[kp_id] = []
        self._kp_index[kp_id].append(q)
        if subject not in self._by_subject:
            self._by_subject[subject] = []
        self._by_subject[subject].append(q)
        return new_id

    def save(self):
        """保存题库到磁盘"""
        bank = {
            "version": "1.0",
            "total_questions": len(self.questions),
            "questions": self.questions,
        }
        path = self.bank_dir / "question_bank.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(bank, f, ensure_ascii=False, indent=2)

    # ---------- 统计 ----------

    def stats(self) -> dict:
        """题库统计"""
        from collections import Counter

        kp_counts = Counter(q["knowledge_id"] for q in self.questions)
        subj_counts = Counter(q["subject"] for q in self.questions)
        kp_with_q = len(kp_counts)
        kp_total = len(self.atlas.get("knowledge_points", []))

        return {
            "total_questions": len(self.questions),
            "knowledge_points_covered": kp_with_q,
            "knowledge_points_total": kp_total,
            "coverage": f"{kp_with_q}/{kp_total} ({kp_with_q*100//kp_total}%)",
            "best_covered": [{"id": k, "name": self.get_kp_name(k), "count": c}
                             for k, c in kp_counts.most_common(5)],
            "by_subject": dict(subj_counts.most_common()),
        }


# ---------- CLI ----------

def cli():
    """命令行快速查询"""
    import sys

    bank = KnowledgeBank()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python knowledge_bank.py stats          — 题库统计")
        print("  python knowledge_bank.py kp <id>        — 查看知识点")
        print("  python knowledge_bank.py q <kp_id>      — 查题目")
        print("  python knowledge_bank.py list [数学|英语|语文] — 列出知识图谱")
        return

    cmd = sys.argv[1]

    if cmd == "stats":
        s = bank.stats()
        print(f"题目总数: {s['total_questions']}")
        print(f"覆盖知识点: {s['coverage']}")
        print(f"学科分布: {s['by_subject']}")
        print(f"最多题目的知识点:")
        for item in s["best_covered"]:
            print(f"  [{item['id']}] {item['name']}: {item['count']}题")

    elif cmd == "kp" and len(sys.argv) > 2:
        kp = bank.get_knowledge_point(sys.argv[2])
        if kp:
            print(json.dumps(kp, ensure_ascii=False, indent=2))
        else:
            print(f"知识点 {sys.argv[2]} 不存在")

    elif cmd == "q" and len(sys.argv) > 2:
        qs = bank.get_questions_by_kp(sys.argv[2])
        for q in qs:
            print(f"[{q['id']}] d{q['difficulty']} {q['prompt'][:60]}... → {q['answer']}")

    elif cmd == "list":
        subject = sys.argv[2] if len(sys.argv) > 2 else None
        kps = bank.list_knowledge_points(subject=subject)
        for kp in kps:
            emoji = "✅" if kp["status"] == "unlocked" else "🔒"
            print(f"{emoji} [{kp['id']}] {kp['name']} ({kp['category']})")


if __name__ == "__main__":
    cli()
