"""
王牌钓手 真题爬虫与入库流水线
============================
数据源：道客巴巴(doc88)、百度文库、菁优网等公开资源
目标：2021-2026 上海小学四年级 语数英 期末/期中/月考真题

用法：
  python scrape_exams.py search   — 搜索并列出可用的试卷链接
  python scrape_exams.py fetch    — 批量下载试卷文本
  python scrape_exams.py import   — 解析试卷并导入题库
"""

import json
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

BANK_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = BANK_DIR / "raw_exams"  # 原始下载的试卷
INDEX_FILE = BANK_DIR / "exam_index.json"  # 试卷索引


# ========== 试卷索引管理 ==========

class ExamIndex:
    """管理已发现和已下载的真题试卷索引"""

    def __init__(self):
        self.index = self._load()
        RAW_DIR.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "1.0", "papers": [], "last_updated": ""}

    def save(self):
        self.index["last_updated"] = time.strftime("%Y-%m-%d %H:%M")
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def add_paper(self, paper: dict):
        """添加一张试卷到索引"""
        # 去重
        for p in self.index["papers"]:
            if p.get("url") == paper.get("url"):
                return
        self.index["papers"].append(paper)
        self.save()

    def list_by_subject(self, subject: str) -> list:
        return [p for p in self.index["papers"]
                if subject in p.get("subject", "")]

    def list_by_year(self, year: int) -> list:
        return [p for p in self.index["papers"]
                if p.get("year") == year]

    def stats(self) -> dict:
        from collections import Counter
        subjects = Counter(p.get("subject", "") for p in self.index["papers"])
        years = Counter(p.get("year", 0) for p in self.index["papers"])
        return {
            "total": len(self.index["papers"]),
            "downloaded": sum(1 for p in self.index["papers"] if p.get("downloaded")),
            "by_subject": dict(subjects.most_common()),
            "by_year": dict(sorted(years.items())),
        }


# ========== Doc88 搜索器 ==========

def search_doc88(keyword: str, max_pages: int = 3) -> list:
    """
    搜索道客巴巴上的试卷。
    注意：道客巴巴使用 POST 搜索，可能需要处理 CSRF token。
    如果直接搜索被拦截，请手动打开浏览器访问搜索页面获取结果。
    """
    results = []
    
    # Doc88 的搜索 API（可能变化）
    search_url = "https://www.doc88.com/search"
    
    # 尝试 GET 方式
    params = urllib.parse.urlencode({"q": keyword, "p": 1})
    url = f"{search_url}?{params}"
    
    # 注意：实际使用时需处理反爬虫（User-Agent, Cookie等）
    print(f"[INFO] 手动搜索建议：在浏览器打开 https://www.doc88.com")
    print(f"[INFO] 搜索：{keyword}")
    print(f"[INFO] 将结果页的链接复制到 data/raw_exams/urls.txt")
    
    return results


# ========== 试卷解析器 ==========

class ExamParser:
    """从原始试卷文本中提取题目"""

    # 常见题型识别模式
    QUESTION_PATTERNS = [
        # 数学
        r"(\d+)[.、．]\s*(.+?)(?=\d+[.、．]|$|二[、.]|三[、.]|四[、.]|五[、.])",
        # 语文看拼音写汉字
        r"(\d+)[.、．]\s*看拼音[^。]+。",
        # 英语填空
        r"(\d+)[.、．]\s*([A-Z].+?[_.]{2,})",
    ]

    # 知识点关键词映射
    KP_KEYWORDS = {
        "除法陷阱": ["÷", "除以", "能不能写成", "不能合并"],
        "括号与混合运算": ["[", "]", "先算", "再算"],
        "小数加减": ["小数", "0.", "对齐"],
        "退位减法": ["退位", "不够减", "退一"],
        "容量换算": ["升", "毫升", "ml", "L"],
        "三单": ["likes", "goes", "第三人称"],
        "进行时": ["ing", "正在", "is running"],
        "be动词": ["am", "is", "are", "be"],
        "成语": ["成语", "补充完整"],
        "修改病句": ["修改病句", "病句"],
        "古诗词": ["默写", "古诗", "填空"],
    }

    def parse_questions(self, text: str, subject: str) -> list:
        """从文本中解析题目"""
        questions = []
        
        # 按行分割，找题号
        lines = text.split("\n")
        current_q = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测题号 （1. 2、 (1) 等）
            match = re.match(r"^[\(（]?(\d+)[\)）]?[.、．\s]", line)
            if match:
                if current_q:
                    questions.append(current_q)
                
                # 猜测知识点
                kp = self._guess_kp(line, subject)
                current_q = {
                    "prompt": line,
                    "subject": subject,
                    "knowledge_guess": kp,
                    "source": "exam_parse",
                }
            elif current_q:
                current_q["prompt"] += " " + line
        
        if current_q:
            questions.append(current_q)
        
        return questions

    def _guess_kp(self, text: str, subject: str) -> str:
        """根据文本内容猜测属于哪个知识点"""
        for kp_name, keywords in self.KP_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    return kp_name
        return ""

    def extract_answer_section(self, text: str) -> str:
        """尝试提取参考答案部分"""
        patterns = [
            r"参考[答案答][：:](.+?)(?=参考|$)",
            r"[答案答][：:](.+?)(?=$)",
        ]
        for pat in patterns:
            match = re.search(pat, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""


# ========== 真题入库 ==========

def import_exam_to_bank(exam_text: str, subject: str, year: int, source: str = ""):
    """
    将一份真题试卷的题目解析并导入题库。
    需要 knowledge_bank.py 配合。
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from knowledge_bank import KnowledgeBank
    
    bank = KnowledgeBank()
    parser = ExamParser()
    
    questions = parser.parse_questions(exam_text, subject)
    
    imported = 0
    for q in questions:
        kp_id = q.get("knowledge_guess", "")
        if not kp_id:
            # 尝试通过名称匹配知识点ID
            for kp in bank.atlas.get("knowledge_points", []):
                if kp.get("name") == kp_id or kp_id in kp.get("alias", ""):
                    kp_id = kp["id"]
                    break
        
        if kp_id:
            qid = bank.add_question(
                kp_id=kp_id,
                subject=subject,
                prompt=q["prompt"],
                answer="",  # 答案需手动标注
                difficulty=2,
                kind="exam",
            )
            imported += 1
    
    bank.save()
    print(f"导入完成：{imported}/{len(questions)} 题")
    return imported


# ========== 超纲题分析器 ==========

class ExamScopeAnalyzer:
    """分析试卷中的超纲题"""
    
    # 四年级上海课标范围（简化版）
    GRADE4_SCOPE = {
        "数学": {
            "in_scope": [
                "四则运算", "小数加减", "分数认识", "面积周长",
                "角的认识", "统计图", "应用题", "简便计算"
            ],
            "out_of_scope_indicators": [
                "方程", "负数运算", "小数乘除", "体积",
                "百分数", "比例", "代数式", "概率"
            ]
        },
        "英语": {
            "in_scope": [
                "词汇", "三单", "进行时", "be动词", "There be",
                "疑问句", "祈使句", "介词"
            ],
            "out_of_scope_indicators": [
                "过去时", "将来时", "完成时", "被动语态",
                "定语从句", "比较级最高级"
            ]
        },
        "语文": {
            "in_scope": [
                "字词", "成语", "近反义词", "标点", "修改病句",
                "阅读", "古诗", "写作"
            ],
            "out_of_scope_indicators": [
                "文言文虚词", "复杂修辞", "议论文"
            ]
        }
    }
    
    def analyze(self, questions: list, subject: str) -> dict:
        """分析题目是否超纲"""
        scope = self.GRADE4_SCOPE.get(subject, {})
        in_scope = []
        out_of_scope = []
        
        for q in questions:
            text = q.get("prompt", "") if isinstance(q, dict) else q
            is_out = False
            for indicator in scope.get("out_of_scope_indicators", []):
                if indicator in text:
                    out_of_scope.append({"question": text, "reason": f"含超纲概念: {indicator}"})
                    is_out = True
                    break
            if not is_out:
                in_scope.append(text)
        
        return {
            "total": len(questions),
            "in_scope": len(in_scope),
            "out_of_scope": len(out_of_scope),
            "out_of_scope_details": out_of_scope,
            "rate": f"{len(in_scope)/max(len(questions),1)*100:.0f}% 课内",
        }


# ========== CLI ==========

def cli():
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "stats":
        idx = ExamIndex()
        s = idx.stats()
        print(f"真题索引统计:")
        print(f"  总试卷数: {s['total']}")
        print(f"  已下载: {s['downloaded']}")
        print(f"  学科分布: {s['by_subject']}")
        print(f"  年份分布: {s['by_year']}")

    elif cmd == "search":
        keyword = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "上海 四年级 期末试卷"
        print(f"[搜索] {keyword}")
        print("[提示] 请手动在浏览器访问以下网站搜索：")
        print("  1. https://www.doc88.com — 搜索后复制结果URL")
        print("  2. https://wenku.baidu.com — 百度文库")
        print("  3. https://zujuan.xkw.com — 学科网组卷（需登录）")
        print(f"  将URL保存到 {RAW_DIR}/urls.txt")

    elif cmd == "analyze":
        # 分析超纲题
        parser = ExamParser()
        analyzer = ExamScopeAnalyzer()
        
        # 示例：从已下载的试卷文本分析
        subject = sys.argv[2] if len(sys.argv) > 2 else "数学"
        sample_path = RAW_DIR / f"sample_{subject}.txt"
        
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                text = f.read()
            questions = parser.parse_questions(text, subject)
            result = analyzer.analyze(questions, subject)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"[提示] 将试卷文本保存到 {sample_path} 后运行分析")

    elif cmd == "import":
        # 导入试卷到题库
        subject = sys.argv[2] if len(sys.argv) > 2 else "数学"
        year = int(sys.argv[3]) if len(sys.argv) > 3 else 2024
        path = RAW_DIR / f"sample_{subject}.txt"
        
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            import_exam_to_bank(text, subject, year, source=str(path))
        else:
            print(f"文件不存在: {path}")

    else:
        print("用法: python scrape_exams.py [stats|search|analyze|import]")


if __name__ == "__main__":
    cli()
