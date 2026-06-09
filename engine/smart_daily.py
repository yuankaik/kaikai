"""
王牌钓手 智能每日练习生成器
========================
手写题做骨架 + 真题按题型填充 + 每日1阅读 + 每日1应用题
"""

import json
import re
import random
from pathlib import Path
from collections import defaultdict
from typing import Optional

BANK_DIR = Path(__file__).resolve().parent.parent / "data"


class SmartDailyGenerator:
    """智能选题器"""
    
    def __init__(self):
        from knowledge_bank import KnowledgeBank
        self.bank = KnowledgeBank()
        self.hand_qs = [q for q in self.bank.questions 
                        if q.get("legacy_id", "").startswith(("D3-","D4-","D5-","D6-"))]
        self.exam_qs = [q for q in self.bank.questions 
                        if q.get("kind") == "exam"]
        
        # Index by type
        self.by_type = defaultdict(list)
        for q in self.exam_qs:
            t = self._classify(q)
            self.by_type[t].append(q)
        
        # Index hand-written by kp
        self.hand_by_kp = defaultdict(list)
        for q in self.hand_qs:
            self.hand_by_kp[q["knowledge_id"]].append(q)
    
    def _classify(self, q: dict) -> str:
        prompt = q.get("prompt", "")
        subject = q.get("subject", "")
        if subject == "数学":
            if "____" in prompt or "＝" in prompt:
                return "math_blank"
            if re.search(r'[\d]\s*[＋＋÷×\-]\s*[\d]', prompt) and len(prompt) < 80:
                return "math_calc"
            if re.search(r'[A-D][.、．]', prompt):
                return "math_choice"
            if any(w in prompt for w in ["多少", "总共", "一共", "每天", "每", "计划", "需要"]) and len(prompt) > 40:
                return "math_word"
            if len(prompt) < 60:
                return "math_short"
            return "math_other"
        if subject == "英语":
            if re.search(r'[A-D][.、．]', prompt) and len(prompt) < 120:
                return "eng_choice"
            if "____" in prompt or "___" in prompt:
                return "eng_blank"
            if any(w in prompt for w in ["阅读", "read", "Read", "短文", "passage", "判断"]):
                return "eng_reading"
            if len(prompt) < 80:
                return "eng_short"
            return "eng_other"
        if subject == "语文":
            if any(w in prompt for w in ["看拼音", "拼音写"]):
                return "chn_pinyin"
            if "____" in prompt and len(prompt) < 60:
                return "chn_blank"
            if any(w in prompt for w in ["阅读", "短文"]):
                return "chn_reading"
            if any(w in prompt for w in ["修改", "病句", "改错"]):
                return "chn_correct"
            if len(prompt) < 60:
                return "chn_short"
            return "chn_other"
        return "other"
    
    def _quality_ok(self, q: dict, qtype: str) -> bool:
        """快速质量检查：答案和题型是否匹配"""
        answer = q.get("answer", "").strip()
        prompt = q.get("prompt", "")
        
        # 基础过滤
        if not answer or len(answer) < 1 or len(answer) > 100:
            return False
        if len(prompt) < 5 or len(prompt) > 400:
            return False
        if answer in prompt:
            return False
        
        # 按题型检查
        if qtype in ("math_blank", "math_calc"):
            # 答案应该是数字
            if not any(c.isdigit() for c in answer):
                return False
        elif qtype == "math_choice":
            # 答案应该是 A/B/C/D
            if answer.strip() not in "ABCD":
                return False
        elif qtype in ("eng_choice",):
            if answer.strip() not in "ABCD":
                return False
        elif qtype in ("eng_blank", "eng_short"):
            # 英语填空答案应该是单词或短句
            if len(answer) > 40:
                return False
        
        # 排除明显错误的（只有1个数字且是0/1的答案多数是错的）
        if qtype.startswith("math") and answer.strip() in ("0", "1", "A", "B", "C", "D"):
            return False
        
        return True
    
    def _pick_exam(self, qtype: str, count: int, exclude_ids: set) -> list:
        """从真题中选题，带质量过滤"""
        pool = [q for q in self.by_type.get(qtype, []) 
                if q["id"] not in exclude_ids and self._quality_ok(q, qtype)]
        if len(pool) < count:
            return random.sample(pool, len(pool)) if pool else []
        return random.sample(pool, count)
    
    def _pick_hand(self, kp_id: str, count: int, exclude_ids: set) -> list:
        pool = [q for q in self.hand_by_kp.get(kp_id, []) 
                if q["id"] not in exclude_ids]
        return random.sample(pool, min(count, len(pool))) if pool else []
    
    def _clean_prompt(self, prompt: str, qtype: str) -> str:
        """清洗题目文字，去掉OCR残留"""
        # 去掉题号前缀 "1. " "1、" "(1)"
        prompt = re.sub(r'^[\(（]?\d+[\)）]?[.、．)\s]+', '', prompt)
        # 去掉【答案】【解析】残留
        prompt = re.sub(r'【答案】.*|【解析】.*|【详解】.*|【分析】.*|【解答】.*', '', prompt)
        # 去掉多余空白
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        return prompt
    
    def generate(self, day: str, title: str = "", focus: str = "") -> dict:
        """
        生成每日练习。
        
        布局：
        - 进门测（数学热身）：3道手写 + 2道真题填空
        - Boss战（数学核心）：2道手写Boss
        - 技能练习（数学变式）：2道手写 + 2道真题计算
        - 英语词汇：2道手写 + 2道真题填空
        - 英语语法：3道手写
        - 应用题（日更1道）：真题
        - 阅读（英/中交替）：真题缩减版
        - 课堂雷达：3道开放题
        - 费曼
        """
        exclude = set()
        sections = []
        
        # 确定今天是英语阅读还是语文阅读（隔日交替）
        day_num = int(re.search(r'\d+', day).group()) if re.search(r'\d+', day) else 7
        reading_lang = "eng" if day_num % 2 == 1 else "chn"
        
        # === 进门测：数学热身 ===
        warmup_qs = []
        # 手写2道
        for kp in ["M-CALC-003", "M-CALC-002"]:
            qs = self._pick_hand(kp, 1, exclude)
            for q in qs:
                exclude.add(q["id"])
                warmup_qs.append(self._format_q(q, "practice", "热身鱼"))
        # 真题填空3道
        for q in self._pick_exam("math_blank", 3, exclude):
            exclude.add(q["id"])
            warmup_qs.append(self._format_q(q, "practice", "热身鱼"))
        sections.append({"title": "Normal Rod - 进门热身", "hint": "先捞基础分", "questions": warmup_qs})
        
        # === Boss战 ===
        boss_qs = []
        for kp in ["M-CALC-001"]:
            qs = self._pick_hand(kp, 2, exclude)
            for q in qs:
                exclude.add(q["id"])
                boss_qs.append(self._format_q(q, "boss", "Boss鳞片"))
        sections.append({"title": "Monster Rod - Boss挑战", "hint": "今天的Boss：除法陷阱", "questions": boss_qs})
        
        # === 技能练习 ===
        skill_qs = []
        # 手写2道
        for kp in ["M-CALC-005", "M-CALC-004"]:
            qs = self._pick_hand(kp, 1, exclude)
            for q in qs:
                exclude.add(q["id"])
                skill_qs.append(self._format_q(q, "practice", "技能鱼"))
        # 真题计算2道
        for q in self._pick_exam("math_calc", 2, exclude):
            exclude.add(q["id"])
            skill_qs.append(self._format_q(q, "practice", "技能鱼"))
        sections.append({"title": "Super Rod - 技能练习", "hint": "每道打一个技能点", "questions": skill_qs})
        
        # === 应用题（1道） ===
        word_qs = []
        for q in self._pick_exam("math_word", 1, exclude):
            exclude.add(q["id"])
            word_qs.append(self._format_q(q, "boss", "应用鱼"))
        if word_qs:
            sections.append({"title": "Legend Rod - 今日应用题", "hint": "一天一道，读懂再算", "questions": word_qs})
        
        # === 英语词汇 ===
        eng_vocab = []
        for kp in ["E-VOCAB-001"]:
            qs = self._pick_hand(kp, 2, exclude)
            for q in qs:
                exclude.add(q["id"])
                eng_vocab.append(self._format_q(q, "vocab", "单词贝壳"))
        for q in self._pick_exam("eng_blank", 2, exclude):
            exclude.add(q["id"])
            eng_vocab.append(self._format_q(q, "vocab", "单词贝壳"))
        sections.append({"title": "English Rod - 词汇", "hint": "每天几词，日积月累", "questions": eng_vocab})
        
        # === 英语语法 ===
        eng_grammar = []
        for kp in ["E-GRAM-001", "E-GRAM-002", "E-GRAM-003"]:
            qs = self._pick_hand(kp, 1, exclude)
            for q in qs:
                exclude.add(q["id"])
                eng_grammar.append(self._format_q(q, "practice", "语法鱼"))
        sections.append({"title": "English Rod - 语法", "hint": "三单/进行时/be动词", "questions": eng_grammar})
        
        # === 每日阅读 ===
        reading_qs = []
        if reading_lang == "eng":
            for q in self._pick_exam("eng_reading", 1, exclude):
                exclude.add(q["id"])
                reading_qs.append(self._format_q(q, "reading", "阅读贝壳"))
        else:
            for q in self._pick_exam("chn_reading", 1, exclude):
                exclude.add(q["id"])
                reading_qs.append(self._format_q(q, "reading", "阅读贝壳"))
        if reading_qs:
            label = "英语阅读" if reading_lang == "eng" else "语文阅读"
            sections.append({"title": f"Reading Rod - {label}", "hint": "读短文，回答3个问题", "questions": reading_qs})
        
        # === 课堂雷达 ===
        sections.append({"title": "课堂雷达", "hint": "和学校课堂对齐", "questions": [
            {"id": "R1", "knowledge": "课堂词语回忆", "subject": "语文", "kind": "practice",
             "difficulty": 1, "prompt": "写出今天语文课你记住的一个词，并造句。", "answer": "开放题", "unlock_reward": "语文贝壳", "source": "每日雷达"},
            {"id": "R2", "knowledge": "课堂句子复述", "subject": "英语", "kind": "practice",
             "difficulty": 1, "prompt": "写出今天英语课你记住的一句话。", "answer": "开放题", "unlock_reward": "英语贝壳", "source": "每日雷达"},
            {"id": "R3", "knowledge": "课堂同步", "subject": "数学", "kind": "practice",
             "difficulty": 1, "prompt": "今天数学课讲到哪里？写一个关键词。", "answer": "开放题", "unlock_reward": "课堂雷达", "source": "每日雷达"},
        ]})
        
        total = sum(len(s["questions"]) for s in sections)
        spec = {
            "day": day, "title": title or day, "mode": "web-first",
            "focus": focus or "智能混搭", "source_session": "smart-generator",
            "points": {"current": 2038, "goal": 3500},
            "knowledge_fish": {"current": 3, "goal": 93},
            "sections": sections,
            "feynman": {"target": "除法陷阱：为什么除数不能合并",
                        "prompt": "任选一道Boss题，用一句话讲清楚为什么错。",
                        "pass_rule": "能说出关键规则即可。"},
            "total_questions": total,
        }
        return spec
    
    def _format_q(self, q: dict, kind: str, reward: str) -> dict:
        prompt = self._clean_prompt(q.get("prompt", ""), kind)
        return {
            "id": q.get("id", ""),
            "knowledge": q.get("knowledge_name", ""),
            "subject": q.get("subject", ""),
            "kind": kind,
            "difficulty": q.get("difficulty", 1),
            "prompt": prompt,
            "answer": q.get("answer", "").strip(),
            "unlock_reward": reward,
            "source": "智能混搭",
        }


# === CLI ===
def cli():
    import sys
    gen = SmartDailyGenerator()
    day = sys.argv[1] if len(sys.argv) > 1 else "Day7"
    title = sys.argv[2] if len(sys.argv) > 2 else ""
    
    spec = gen.generate(day, title)
    
    output = BANK_DIR.parent / "practice" / "specs" / f"{day}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    
    print(f"生成: {spec['total_questions']} 题")
    for s in spec["sections"]:
        n = len(s["questions"])
        if n:
            print(f"  [{s['title']}] {n}题")
            for q in s["questions"][:2]:
                print(f"    {q['prompt'][:60]} → {q['answer'][:20]}")
    print(f"\n保存: {output}")


if __name__ == "__main__":
    cli()
