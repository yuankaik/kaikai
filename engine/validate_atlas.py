"""
王牌钓手 知识图谱反向验证脚本
============================
用真实真题的实际考点，反向校验我们的91知识点图谱。
- 发现漏掉的知识点 → 补充
- 发现多余的分类 → 合并
- 发现超纲考点 → 标记

用法：
  python validate_atlas.py analyze   — 分析已导入题库的实际知识点分布
  python validate_atlas.py gap       — 对比真题 vs 图谱，找盲区
  python validate_atlas.py suggest   — 建议图谱修改
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

BANK_DIR = Path(__file__).resolve().parent.parent / "data"


def load_atlas():
    with open(BANK_DIR / "knowledge_atlas.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_questions():
    with open(BANK_DIR / "question_bank.json", "r", encoding="utf-8") as f:
        return json.load(f).get("questions", [])


def analyze_exam_coverage():
    """分析真题中各知识点的实际出现频率"""
    atlas = load_atlas()
    questions = load_questions()
    
    # 统计每个知识点的题目数
    kp_counts = Counter(q.get("knowledge_id", "") for q in questions)
    
    # 统计每个学科/分类的覆盖
    by_category = defaultdict(lambda: {"total_kp": 0, "covered": 0, "total_q": 0})
    
    for kp in atlas["knowledge_points"]:
        cat_key = f"{kp['subject']}/{kp['category']}"
        by_category[cat_key]["total_kp"] += 1
        kp_id = kp["id"]
        count = kp_counts.get(kp_id, 0)
        if count > 0:
            by_category[cat_key]["covered"] += 1
            by_category[cat_key]["total_q"] += count
    
    return {
        "total_questions": len(questions),
        "total_kp": len(atlas["knowledge_points"]),
        "covered_kp": len([k for k in kp_counts if kp_counts[k] > 0]),
        "by_category": dict(by_category),
        "top_kp": [(k, v) for k, v in kp_counts.most_common(20) if v > 0],
        "empty_kp": [(k, 0) for k in atlas["knowledge_points"] 
                     if kp_counts.get(k["id"], 0) == 0],
    }


def find_knowledge_gaps():
    """
    反向验证：从真题中提取没有在图谱中的知识点关键词。
    扫描所有题目的prompt，找出重复出现的知识点关键词。
    """
    questions = load_questions()
    atlas = load_atlas()
    
    # 从图谱提取所有已知知识点名称和别名
    known_names = set()
    known_aliases = set()
    for kp in atlas["knowledge_points"]:
        known_names.add(kp["name"])
        if kp.get("alias"):
            known_aliases.add(kp["alias"])
    
    # 常见知识点关键词（从题目prompt中提取）
    # 这些是真题中可能出现的概念，检查是否在图谱中
    common_concepts = {
        "数学": [
            "乘法口诀", "除法口诀", "加法交换律", "减法性质", "差不变",
            "数的组成", "数的读写", "数的改写", "计数单位", "数位",
            "竖式计算", "脱式计算", "递等式", "综合算式",
            "单位换算", "进率", "复名数", "单名数",
            "直线", "射线", "线段", "锐角三角形", "直角三角形", "钝角三角形",
            "等腰三角形", "等边三角形", "不等边三角形",
            "正方体", "长方体", "体积", "容积",
            "真分数", "假分数", "带分数", "通分", "约分",
            "循环小数", "无限小数", "有限小数",
            "质数", "合数", "因数", "倍数", "公因数", "公倍数",
            "相遇问题", "追及问题", "流水问题", "工程问题",
            "利润", "折扣", "利息", "税率",
            "可能性", "概率", "确定事件", "不确定事件",
            "正比例", "反比例",
        ],
        "英语": [
            "元音", "辅音", "开音节", "闭音节",
            "人称", "数词", "序数词", "基数词",
            "感叹句", "选择疑问句", "反意疑问句",
            "不定式", "动名词",
            "同音词", "同义词", "反义词",
        ],
        "语文": [
            "偏旁", "部首", "笔画", "笔顺",
            "形声字", "会意字", "象形字",
            "主谓宾", "定状补", "把字句", "被字句",
            "扩句", "缩句", "句式转换",
            "拟人", "夸张", "对偶", "反问", "设问",
            "过渡句", "中心句", "总起句", "总结句",
            "童话", "寓言", "神话", "民间故事",
            "读后感", "观后感", "通知", "留言条",
        ],
    }
    
    gaps = defaultdict(list)
    for subject, concepts in common_concepts.items():
        for concept in concepts:
            # 检查是否在图谱中
            found = False
            for name in known_names:
                if concept in name or name in concept:
                    found = True
                    break
            for alias in known_aliases:
                if concept in alias or alias in concept:
                    found = True
                    break
            
            if not found:
                # 检查在题目中是否出现
                appeared = 0
                for q in questions:
                    if q.get("subject") == subject and concept in q.get("prompt", ""):
                        appeared += 1
                if appeared > 0:
                    gaps[subject].append({
                        "concept": concept,
                        "appearances": appeared,
                    })
    
    return dict(gaps)


def suggest_atlas_changes():
    """基于真题数据建议图谱修改"""
    atlas = load_atlas()
    questions = load_questions()
    gaps = find_knowledge_gaps()
    coverage = analyze_exam_coverage()
    
    suggestions = {
        "add": [],       # 需要新增的知识点
        "split": [],     # 需要拆分的过粗知识点
        "merge": [],     # 需要合并的过细知识点
        "reorder": [],   # 需要调整前置依赖的
        "out_of_scope": [],  # 超纲但真题出现的
    }
    
    # 1. 发现漏掉的知识点
    for subject, gap_list in gaps.items():
        for gap in gap_list:
            if gap["appearances"] >= 3:  # 出现3次以上才建议加
                suggestions["add"].append({
                    "subject": subject,
                    "concept": gap["concept"],
                    "evidence": f"真题出现{gap['appearances']}次",
                })
    
    # 2. 检查空知识点（在图谱但真题中没出现）
    empty = coverage.get("empty_kp", [])
    for kp in empty[:10]:
        suggestions["reorder"].append({
            "kp_id": kp["id"] if isinstance(kp, dict) else kp,
            "issue": "图谱有但真题未覆盖（可能是考纲外或需调整分类）",
        })
    
    return suggestions


def cli():
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    
    if cmd == "analyze":
        result = analyze_exam_coverage()
        print("=" * 60)
        print("知识图谱覆盖分析")
        print("=" * 60)
        print(f"\n题目总数: {result['total_questions']}")
        print(f"知识点总数: {result['total_kp']}")
        print(f"已覆盖: {result['covered_kp']} ({result['covered_kp']*100//result['total_kp']}%)")
        
        print(f"\n按学科/分类覆盖:")
        for cat, info in sorted(result["by_category"].items()):
            pct = info["covered"] * 100 // info["total_kp"] if info["total_kp"] else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"  {cat:30s} {bar} {info['covered']}/{info['total_kp']} ({info['total_q']}题)")
        
        print(f"\n题目最多的知识点 (Top 10):")
        for kp_id, count in result["top_kp"][:10]:
            print(f"  [{kp_id}] {count}题")
    
    elif cmd == "gap":
        gaps = find_knowledge_gaps()
        print("真题中出现的潜在遗漏知识点:")
        for subject, gap_list in gaps.items():
            if gap_list:
                print(f"\n【{subject}】")
                for g in sorted(gap_list, key=lambda x: -x["appearances"]):
                    print(f"  {g['concept']} — 出现{g['appearances']}次")
    
    elif cmd == "suggest":
        suggestions = suggest_atlas_changes()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    
    else:
        print("用法: python validate_atlas.py [analyze|gap|suggest]")


if __name__ == "__main__":
    cli()
