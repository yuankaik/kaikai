"""
王牌钓手 真题批量导入引擎
======================
从 raw_exams/ 目录批量解析 docx/pdf 试卷，
提取题目→匹配知识点→导入题库。

用法：
  python batch_import.py scan          — 扫描所有试卷，统计概况
  python batch_import.py parse <dir>   — 解析指定目录的试卷
  python batch_import.py import-all    — 解析全部四年级试卷并导入
  python batch_import.py stats         — 导入后题库统计
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Optional

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

BANK_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = BANK_DIR / "raw_exams"

# 知识点关键词映射（用于自动匹配题目到知识点）
KP_KEYWORDS = {
    # 数学 — 数与运算
    "M-CALC-001": ["除法陷阱", "能不能写成", "不能合并", "除数不能", "被除数可以拆"],
    "M-CALC-002": ["÷", "除以", "除法计算", "运算顺序", "先估后算"],
    "M-CALC-003": ["退位", "不够减", "退一当十", "两位数减"],
    "M-CALC-004": ["中括号", "脱括号", "混合运算", "先算", "再算"],
    "M-CALC-005": ["商不变", "余数", "被除数和除数同时", "商不变余数"],
    "M-CALC-006": ["商的变化", "被除数变化", "除数变化"],
    "M-CALC-007": ["小数加减", "小数点对齐", "0.", "小数加", "小数减"],
    "M-CALC-008": ["小数巧算", "小数混合", "小数四则"],
    "M-CALC-009": ["小数位值", "小数的意义", "小数点移动"],
    "M-CALC-010": ["纯小数", "小数比较", "最大纯小数", "最小纯小数"],
    "M-CALC-011": ["四则运算", "加减乘除", "万以内", "直接写出"],
    "M-CALC-012": ["分配律", "结合律", "简便计算", "简便方法"],
    "M-CALC-013": ["分数", "几分之", "几分之一"],
    "M-CALC-017": ["近似数", "四舍五入", "估算"],
    "M-CALC-021": ["递等式", "脱式计算", "递等"],
    "M-CALC-022": ["竖式计算", "列竖式", "竖式"],
    "M-CALC-023": ["综合算式", "列综合", "综合式"],
    "M-CALC-024": ["计数单位", "数位", "数位顺序"],
    "M-CALC-025": ["读写", "改写", "读作", "写作", "万千米"],
    "M-CALC-026": ["加法交换律", "交换律", "a+b"],
    "M-CALC-027": ["减法性质", "差不变", "减法运算"],
    
    # 数学 — 图形与几何
    "M-MEAS-001": ["升", "毫升", "ml", "L", "容量"],
    "M-MEAS-002": ["容量", "装满", "余", "分装"],
    "M-MEAS-003": ["千米", "米", "分米", "厘米", "毫米", "km", "m", "cm", "mm", "长度"],
    "M-MEAS-004": ["吨", "千克", "克", "kg", "g", "重量"],
    "M-MEAS-005": ["平方", "面积单位", "m²", "cm²", "km²"],
    "M-MEAS-006": ["时", "分", "秒", "年月日", "时间"],
    "M-GEOM-001": ["角", "锐角", "直角", "钝角", "平角", "周角", "量角器"],
    "M-GEOM-002": ["平行", "垂直", "垂线", "平行线"],
    "M-GEOM-003": ["三角形", "内角和", "等腰", "等边"],
    "M-GEOM-004": ["平行四边形", "梯形"],
    "M-GEOM-005": ["对称", "轴对称", "平移"],
    "M-GEOM-006": ["周长", "长方形周长", "正方形周长"],
    "M-GEOM-007": ["面积", "长方形面积", "正方形面积"],
    
    # 数学 — 统计
    "M-STAT-001": ["条形统计图", "条形图"],
    "M-STAT-002": ["折线统计图", "折线图"],
    "M-STAT-003": ["平均数", "平均"],
    
    # 数学 — 应用题
    "M-WORD-001": ["应用题", "答", "单位"],
    "M-WORD-002": ["钱", "转移", "差倍"],
    "M-WORD-003": ["归一", "先求一份", "单一量"],
    "M-WORD-004": ["归总", "先求总数"],
    "M-WORD-005": ["行程", "速度", "时间", "路程", "每分钟"],
    "M-WORD-006": ["植树", "间隔", "棵数"],
    "M-WORD-007": ["鸡兔同笼", "假设法"],
    "M-WORD-008": ["盈亏"],
    
    # 英语
    "E-VOCAB-001": ["单词", "词汇", "写出中文", "读一读", "选出不同类", "汉译英", "英译汉",
                     "选出每组中不同类", "根据汉语", "看图写单词", "补全单词"],
    "E-VOCAB-002": ["复数", "可数", "名词", "单数", "复数形式", "变复数"],
    "E-VOCAB-003": ["时间", "时间表达", "What time", "o'clock", "几点"],
    "E-VOCAB-004": ["日期", "月份", "星期", "Monday", "January"],
    "E-VOCAB-005": ["天气", "weather", "sunny", "rainy", "cloudy"],
    "E-GRAM-001": ["三单", "第三人称", "likes", "goes", "does", "单数形式"],
    "E-GRAM-002": ["现在进行时", "ing", "正在", "is running", "are doing", "be doing"],
    "E-GRAM-003": ["be动词", "am", "is", "are", "用am/is/are", "用be动词"],
    "E-GRAM-004": ["代词", "物主", "主格", "宾格", "my", "your", "mine", "yours",
                   "人称代词", "物主代词", "him", "her", "me", "us"],
    "E-GRAM-005": ["冠词", "a/an", "the", "用a", "用an"],
    "E-GRAM-006": ["情态", "can", "may", "must", "should", "could"],
    "E-GRAM-007": ["比较级", "than", "more", "最高级", "比较"],
    "E-GRAM-008": ["介词", "in", "on", "at", "under", "beside", "behind",
                   "用适当的介词", "介词填空"],
    "E-GRAM-009": ["疑问词", "what", "who", "where", "when", "why", "how",
                   "特殊疑问词", "疑问句"],
    "E-SYNX-001": ["There be", "there is", "there are"],
    "E-SYNX-002": ["一般现在时", "一般现在", "do/does"],
    "E-SYNX-003": ["一般过去时", "was", "were", "过去式", "yesterday", "last", "ago"],
    "E-SYNX-004": ["一般将来时", "will", "be going to", "tomorrow", "next"],
    "E-SYNX-005": ["一般疑问句", "疑问句", "改为一般疑问", "改成一般疑问"],
    "E-SYNX-006": ["祈使句", "命令", "please", "don't", "let's"],
    "E-SYNX-007": ["连词", "and", "but", "or", "because", "so"],
    "E-READ-001": ["课堂句子", "记住的", "复述"],
    "E-READ-002": ["对话", "情景", "补全对话", "完成对话", "问答"],
    "E-READ-003": ["阅读理解", "阅读短文", "读短文", "阅读文章", "判断正误", "根据短文",
                   "阅读下面", "阅读并", "read and"],
    "E-WRIT-001": ["句子书写", "连词成句", "造句", "写句子", "完整句子"],
    "E-WRIT-002": ["写作", "书面表达", "短文", "小作文", "写一段", "描述"],
    
    # 语文
    "C-VOCAB-001": ["词语", "记住的词", "造句", "看拼音", "写汉字", "看拼音写",
                     "组词", "比一比", "组词语", "看拼音写词语"],
    "C-VOCAB-002": ["多音字", "多音", "选择正确读音", "给加点字选择"],
    "C-VOCAB-003": ["形近字", "形近", "辨字组词", "比一比再组词"],
    "C-VOCAB-004": ["近义词", "反义词", "写出近义词", "写出反义词"],
    "C-VOCAB-005": ["成语", "补充完整", "把词语补充", "四字词语"],
    "C-VOCAB-006": ["关联词", "因为所以", "虽然但是", "如果就", "不但而且",
                     "用关联词", "填关联词"],
    "C-VOCAB-007": ["比喻", "拟人", "排比", "修辞", "修辞手法"],
    "C-READ-001": ["概括", "段意", "段落", "主要内容", "用一句话"],
    "C-READ-002": ["中心思想", "主旨", "表达了什么", "告诉我们"],
    "C-READ-003": ["记叙文", "阅读短文", "阅读下面", "课内阅读", "课外阅读"],
    "C-READ-004": ["说明文"],
    "C-POEM-001": ["古诗", "默写", "背诵", "补充诗句", "将诗句补充", "填空诗句"],
    "C-POEM-002": ["小古文", "文言文", "古文"],
    "C-WRIT-001": ["看图写话", "看图", "写一段话"],
    "C-WRIT-002": ["日记", "写日记"],
    "C-WRIT-003": ["书信", "写信", "格式"],
    "C-WRIT-004": ["修改病句", "病句", "修改下列", "改病句"],
    "C-WRIT-005": ["标点", "逗号", "句号", "引号", "加标点", "标点符号"],
    
    # 新几何点
    "M-GEOM-008": ["直线", "射线", "线段", "线的认识"],
}


class ExamParser:
    """解析单份试卷"""
    
    def __init__(self):
        pass
    
    def parse_docx(self, filepath: Path) -> dict:
        """解析docx试卷，返回 {questions: [], answers: {}, meta: {}}"""
        doc = Document(str(filepath))
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return self._parse_lines(lines, filepath.name)
    
    def _parse_lines(self, lines: list, filename: str) -> dict:
        """从行列表解析试卷"""
        result = {
            "filename": filename,
            "title": "",
            "subject": self._guess_subject(filename),
            "year": self._guess_year(filename),
            "district": self._guess_district(filename),
            "type": self._guess_exam_type(filename),
            "grade": self._guess_grade(filename),
            "questions": [],
            "answers": {},
        }
        
        result["title"] = lines[0] if lines else ""
        
        # 分割原卷和答案
        answer_start = None
        for i, line in enumerate(lines):
            if "参考答案" in line or "答案" in line and i > len(lines) * 0.5:
                answer_start = i
                break
        
        question_lines = lines[:answer_start] if answer_start else lines
        answer_lines = lines[answer_start:] if answer_start else []
        
        # 解析题目
        questions = self._extract_questions(question_lines)
        
        # 解析答案
        if answer_lines:
            answers = self._extract_answers(answer_lines)
        else:
            answers = {}
        
        # 匹配题目和答案
        for q in questions:
            q_id = str(q.get("number", ""))
            # 尝试匹配答案
            for a_key, a_val in answers.items():
                if q_id in a_key or a_key in q_id:
                    q["answer"] = a_val
                    break
        
        result["questions"] = questions
        result["answers"] = answers
        
        return result
    
    def _extract_questions(self, lines: list) -> list:
        """从行中提取题目 — 改进版：清理答案/解析残留"""
        questions = []
        current_q = None
        q_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过答案标记行
            if re.match(r'^【答案】|^【解析】|^【分析】|^参考答案|^答案[：:]', line):
                continue
            
            # 检测题号模式
            num_match = re.match(r'^[\(（]?(\d+)[\)）]?[.、．)\s]', line)
            
            if num_match:
                if current_q:
                    questions.append(current_q)
                q_number += 1
                # 清理行内答案标记
                clean_line = self._strip_answers_from_prompt(line)
                current_q = {
                    "number": q_number,
                    "prompt": clean_line,
                    "answer": "",
                    "subject": "",
                }
            elif current_q:
                # 续行 — 但遇到答案标记就停
                if re.search(r'【答案】|【解析】|【分析】', line):
                    line = re.sub(r'【答案】.*|【解析】.*|【分析】.*', '', line).strip()
                    if not line:
                        continue
                current_q["prompt"] += " " + line
        
        if current_q:
            questions.append(current_q)
        
        return questions
    
    def _strip_answers_from_prompt(self, text: str) -> str:
        """清理题目中的答案和解析残留"""
        # 移除 【答案】... 及之后内容
        text = re.sub(r'【答案】.*', '', text)
        text = re.sub(r'【解析】.*', '', text)
        text = re.sub(r'【分析】.*', '', text)
        # 移除行末多余空格
        text = text.strip()
        # 确保长度合理
        return text[:500] if len(text) > 500 else text
    
    def _extract_answers(self, lines: list) -> dict:
        """从答案行中提取答案映射 — 改进版"""
        answers = {}
        full_text = "\n".join(lines)
        
        # 匹配选择题答案模式: 1. A  2. B  或 1-5: ABCDB
        # 上海试卷常见格式
        choice_blocks = re.findall(r'(\d+)[.、\s]+([A-D])', full_text)
        for num, ans in choice_blocks:
            answers[num] = ans
        
        # 匹配连续选择题答案: 1-5 ABCDA  或 1.A 2.B 3.C
        seq_match = re.findall(r'(\d+)[.、]\s*([A-D])', full_text)
        for num, ans in seq_match:
            if num not in answers:
                answers[num] = ans
        
        # 匹配数学答案: 题号＝答案 或 题号. 答案
        for line in lines:
            # 格式: 1.120  2.36  3.8000
            math_answers = re.findall(r'(\d+)[.、]\s*([\d.]+)', line)
            for num, ans in math_answers:
                if num not in answers and len(ans) > 0:
                    answers[num] = ans
            
            # 格式: (1) 828  (2) 160
            paren_answers = re.findall(r'[\(（](\d+)[\)）]\s*([\d.]+)', line)
            for num, ans in paren_answers:
                if num not in answers:
                    answers[num] = ans
        
        return answers
    
    def _guess_subject(self, filename: str) -> str:
        f = filename.lower()
        if "数学" in f:
            return "数学"
        if "英语" in f or "english" in f:
            return "英语"
        if "语文" in f:
            return "语文"
        return ""
    
    def _guess_year(self, filename: str) -> int:
        match = re.search(r'20(\d{2})-20(\d{2})', filename)
        if match:
            return int(f"20{match.group(1)}")
        match = re.search(r'20(\d{2})', filename)
        if match:
            return int(f"20{match.group(1)}")
        return 0
    
    def _guess_district(self, filename: str) -> str:
        districts = ["浦东", "黄浦", "徐汇", "长宁", "静安", "普陀", "虹口",
                     "杨浦", "闵行", "宝山", "嘉定", "金山", "松江", "青浦",
                     "奉贤", "崇明"]
        for d in districts:
            if d in filename:
                return d + "区"
        return ""
    
    def _guess_exam_type(self, filename: str) -> str:
        f = filename
        if "期末" in f:
            return "期末"
        if "期中" in f:
            return "期中"
        if "月考" in f:
            return "月考"
        return "练习"
    
    def _guess_grade(self, filename: str) -> str:
        if "四年级" in filename or "4年级" in filename:
            return "四年级"
        if "三年级" in filename:
            return "三年级"
        if "五年级" in filename:
            return "五年级"
        return ""


class BatchImporter:
    """批量导入试题到题库"""
    
    def __init__(self):
        import os
        engine_dir = str(Path(__file__).parent)
        if engine_dir not in sys.path:
            sys.path.insert(0, engine_dir)
        from knowledge_bank import KnowledgeBank
        self.bank = KnowledgeBank()
        self.parser = ExamParser()
        self.stats = {"parsed": 0, "questions": 0, "imported": 0, "errors": 0}
    
    def scan_directory(self, directory: Path) -> dict:
        """扫描目录统计试卷"""
        result = defaultdict(lambda: defaultdict(int))
        for f in directory.rglob("*.docx"):
            info = self.parser._guess_subject(f.name)
            year = self.parser._guess_year(f.name)
            result[info][year] += 1
        return result
    
    def parse_and_import(self, directory: Path, subject_filter: str = None, limit: int = 0):
        """解析目录下所有docx并导入题库"""
        files = list(directory.rglob("*.docx"))
        
        if subject_filter:
            files = [f for f in files 
                    if self.parser._guess_subject(f.name) == subject_filter]
        
        if limit:
            files = files[:limit]
        
        print(f"待处理: {len(files)} 份试卷")
        
        for i, filepath in enumerate(files):
            try:
                exam = self.parser.parse_docx(filepath)
                self.stats["parsed"] += 1
                
                imported = 0
                for q in exam["questions"]:
                    self.stats["questions"] += 1
                    
                    # 匹配知识点
                    kp_id = self._match_kp(q["prompt"], exam["subject"])
                    
                    if kp_id and q.get("answer"):
                        self.bank.add_question(
                            kp_id=kp_id,
                            subject=exam["subject"],
                            prompt=q["prompt"][:200],  # 限制长度
                            answer=q["answer"],
                            difficulty=self._guess_difficulty(q["prompt"]),
                            kind="exam",
                        )
                        imported += 1
                        self.stats["imported"] += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  进度: {i+1}/{len(files)} ({self.stats['imported']}题入库)")
                
            except Exception as e:
                self.stats["errors"] += 1
                if self.stats["errors"] <= 5:
                    print(f"  错误 ({filepath.name}): {e}")
        
        self.bank.save()
    
    def _quality_check(self, prompt: str, answer: str) -> bool:
        """质量检查：过滤掉解析残缺的题目"""
        if not answer or not prompt:
            return False
        # 答案太短（<1）或太长（>200）不正常
        if len(answer) < 1 or len(answer) > 200:
            return False
        # 题目太短或太长
        if len(prompt) < 10 or len(prompt) > 500:
            return False
        # 答案在题目里出现 → 说明题目和答案没分开
        if answer in prompt:
            return False
        # 答案包含"解析""分析"→ 混入了答案区域
        if "解析" in answer or "分析" in answer or "参考答案" in answer:
            return False
        # 英文答案超过20字符可能是句子混入
        if answer.isascii() and len(answer) > 50:
            return False
        return True

    def _match_kp(self, text: str, subject: str) -> Optional[str]:
        """自动匹配知识点"""
        # 先在已定义的关键词中匹配
        for kp_id, keywords in KP_KEYWORDS.items():
            kp = self.bank.get_knowledge_point(kp_id)
            if not kp:
                continue
            if kp["subject"] != subject:
                continue
            for kw in keywords:
                if kw.lower() in text.lower():
                    return kp_id
        
        # 数学题默认归到四则运算
        if subject == "数学":
            if any(op in text for op in ["+", "-", "×", "÷", "*", "/"]):
                if "÷" in text:
                    return "M-CALC-002"
                return "M-CALC-011"
            if "角" in text:
                return "M-GEOM-001"
            if "面积" in text or "周长" in text:
                return "M-GEOM-007" if "面积" in text else "M-GEOM-006"
        
        return None
    
    def _guess_difficulty(self, text: str) -> int:
        """猜测题目难度 1-3"""
        if "应用" in text or "解决" in text or "Boss" in text:
            return 3
        if "选择" in text or "判断" in text or "概念" in text:
            return 2
        return 1
    
    def print_stats(self):
        s = self.stats
        bank_s = self.bank.stats()
        print(f"\n{'='*50}")
        print(f"导入统计")
        print(f"{'='*50}")
        print(f"  解析试卷: {s['parsed']}")
        print(f"  提取题目: {s['questions']}")
        print(f"  成功入库: {s['imported']}")
        print(f"  出错: {s['errors']}")
        print(f"\n  题库总量: {bank_s['total_questions']}")
        print(f"  覆盖知识点: {bank_s['coverage']}")


def cli():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if cmd == "scan":
        # 扫描所有试卷
        importer = BatchImporter()
        
        print("=" * 60)
        print("真题试卷扫描报告")
        print("=" * 60)
        
        for grade_dir in sorted(RAW_DIR.iterdir()):
            if not grade_dir.is_dir():
                continue
            grade = grade_dir.name
            
            total = len(list(grade_dir.rglob("*.docx")))
            if total == 0:
                continue
            
            print(f"\n📚 {grade}: {total} 份试卷")
            
            # 按学科统计
            for subj in ["数学", "英语", "语文"]:
                count = len(list(grade_dir.rglob(f"*{subj}*/*.docx")))
                if count > 0:
                    print(f"    {subj}: {count}")
    
    elif cmd == "import-all":
        # 导入全部四年级试卷
        importer = BatchImporter()
        grade4_dir = RAW_DIR / "四年级"
        
        if not grade4_dir.exists():
            print("四年级目录不存在")
            return
        
        print("开始批量导入四年级真题...")
        print("=" * 60)
        
        for subj in ["数学", "英语", "语文"]:
            print(f"\n--- {subj} ---")
            importer.parse_and_import(grade4_dir, subject_filter=subj)
        
        importer.print_stats()
        importer.bank.save()
    
    elif cmd == "import-subject":
        subject = sys.argv[2] if len(sys.argv) > 2 else "数学"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        
        importer = BatchImporter()
        grade4_dir = RAW_DIR / "四年级"
        importer.parse_and_import(grade4_dir, subject_filter=subject, limit=limit)
        importer.print_stats()
    
    elif cmd == "stats":
        from knowledge_bank import KnowledgeBank
        bank = KnowledgeBank()
        s = bank.stats()
        print(json.dumps(s, ensure_ascii=False, indent=2))
    
    else:
        print("用法:")
        print("  python batch_import.py scan              — 扫描全部试卷概览")
        print("  python batch_import.py import-all        — 导入全部四年级试卷")
        print("  python batch_import.py import-subject 数学 — 导入数学")
        print("  python batch_import.py stats             — 题库统计")


if __name__ == "__main__":
    cli()
