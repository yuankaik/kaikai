"""Auto-grading engine for 王牌钓手 web practice.

Handles immediate answer checking for math, English, and Chinese questions.
Returns structured feedback with points, retry hints, and mastery state transitions.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


@dataclass
class GradeResult:
    question_id: str
    knowledge: str
    state: str          # "ok" | "review" | "bad"
    label: str
    points: int
    reason: str
    caution: str = ""
    next_action: str = ""
    expected: str = ""


@dataclass
class SessionReport:
    day: str
    total_questions: int
    ok_count: int = 0
    review_count: int = 0
    bad_count: int = 0
    total_points: int = 0
    items: list[dict[str, Any]] = field(default_factory=list)
    recovered_fish: list[str] = field(default_factory=list)
    escaped_fish: list[str] = field(default_factory=list)
    new_knowledge_fish: int = 0


def normalize(value: str) -> str:
    """Normalize answer for comparison: strip whitespace, punctuation, lowercase."""
    return re.sub(r'\s+', '', str(value or '')).replace('，', '').replace(',', '').replace('。', '').replace(';', ';').replace('；', '').lower()


def numbers_in(value: str) -> list[str]:
    """Extract all numeric tokens from an answer string."""
    return re.findall(r'\d+(?:\.\d+)?', str(value or ''))


def numbers_match(student: str, expected: str) -> bool:
    """True if all expected numbers appear in the student's answer."""
    exp_nums = numbers_in(expected)
    if not exp_nums:
        return False
    stu_nums = numbers_in(student)
    return all(n in stu_nums for n in exp_nums)


def _count_blanks(prompt: str) -> int:
    return len(re.findall(r'____+', prompt or ''))


def _has_judgement(answer: str, expected: str) -> bool:
    """Check if a judgement question (能/不能) was answered."""
    words = ['不能', '不可以', '可以', '能']
    return any(w in answer for w in words)


# ── Public API ──────────────────────────────────────────────────────


def grade_single(question: dict[str, Any], student_answer: str) -> GradeResult:
    """Grade one question and return structured result."""
    qid = str(question.get('id', '?'))
    knowledge = str(question.get('knowledge', ''))
    expected = str(question.get('answer', ''))
    prompt = str(question.get('prompt', ''))
    kind = str(question.get('kind', 'practice'))
    answer = str(student_answer or '').strip()

    # Empty answer
    if not answer:
        return GradeResult(
            question_id=qid, knowledge=knowledge, state='bad',
            label='未完成', points=0,
            reason='这题还没有下笔，先算作逃脱鱼。',
            caution='遇到 Boss 题，哪怕不会，也先写"我卡在……"这句话。',
            next_action=_variation(question), expected=expected,
        )

    # Open-ended questions
    if '开放题' in expected:
        ok = len(answer) >= 4
        return GradeResult(
            question_id=qid, knowledge=knowledge,
            state='review' if ok else 'bad',
            label='已完成，待大副精批' if ok else '表达太短',
            points=12 if ok else 4,
            reason='开放题先看完成度。' if ok else '开放题需要写出完整词句。',
            caution='语文英语开放题要尽量写成一句完整的话。',
            next_action='加分：完成课堂雷达。' if ok else _variation(question),
            expected=expected,
        )

    # Completeness check (multi-blank questions)
    blank_count = _count_blanks(prompt)
    stu_nums = len(numbers_in(answer))
    if blank_count >= 2 and stu_nums < blank_count:
        return GradeResult(
            question_id=qid, knowledge=knowledge, state='review',
            label='差一点，先补完整', points=8,
            reason=f'这题有 {blank_count} 个空，已看到 {stu_nums} 个数字。每个空都要填。',
            caution='一题里有两个空或两个问时，先逐个打勾：第一问、第二问、单位。',
            next_action=_variation(question), expected=expected,
        )

    # Judgement check (能不能/是不是 questions)
    if ('能不能' in prompt or '不能' in expected or '不可以' in expected) and not _has_judgement(answer, expected):
        return GradeResult(
            question_id=qid, knowledge=knowledge, state='review',
            label='数字对了，还要回答能/不能', points=8,
            reason='计算后还有一个判断题：别忘了回答"能/不能"。',
            caution='先写计算结果，再写"能"或"不能"。',
            next_action=_variation(question), expected=expected,
        )

    # Unit check
    unit_words = ['ml', '毫升', '瓶', '升', '个', '元', '米', 'cm', 'm', 'km']
    if any(w in expected for w in unit_words) and not any(w in answer for w in unit_words):
        if numbers_match(answer, expected):
            return GradeResult(
                question_id=qid, knowledge=knowledge, state='review',
                label='核心正确，单位要补齐', points=16,
                reason=f'关键数字对了，标准答案是：{expected}。',
                caution='以后最后一步要把单位和答句补完整。',
                next_action=f'奖励：解锁"{knowledge}"。', expected=expected,
            )

    # Exact match or number match
    if normalize(answer) == normalize(expected) or numbers_match(answer, expected):
        # Check if it was only number match (slightly imperfect)
        if numbers_match(answer, expected) and normalize(answer) != normalize(expected):
            return GradeResult(
                question_id=qid, knowledge=knowledge, state='review',
                label='核心正确，格式再对齐', points=16,
                reason=f'关键数字对了，标准答案是：{expected}。',
                caution='下次把格式写得更整齐。',
                next_action=f'奖励：解锁"{knowledge}"。', expected=expected,
            )
        return GradeResult(
            question_id=qid, knowledge=knowledge, state='ok',
            label='命中', points=20,
            reason='答案命中，说明这个知识点正在变稳。',
            caution='保持先看题意、再下笔的节奏。',
            next_action=f'奖励：获得"{question.get("unlock_reward", knowledge)}"。',
            expected=expected,
        )

    # Wrong answer
    return GradeResult(
        question_id=qid, knowledge=knowledge, state='bad',
        label='需要回炉', points=4,
        reason=f'船长答案：{answer}；正确方向：{expected}。',
        caution=_caution(question),
        next_action=_variation(question), expected=expected,
    )


def grade_session(day: str, questions: list[dict[str, Any]], answers: dict[str, str]) -> SessionReport:
    """Grade an entire practice session."""
    report = SessionReport(day=day, total_questions=len(questions))
    report.items = []

    for q in questions:
        qid = str(q.get('id', ''))
        student = answers.get(qid, '')
        result = grade_single(q, student)

        if result.state == 'ok':
            report.ok_count += 1
        elif result.state == 'review':
            report.review_count += 1
        else:
            report.bad_count += 1
            report.escaped_fish.append(result.knowledge)

        report.total_points += result.points
        report.items.append({
            'id': result.question_id,
            'knowledge': result.knowledge,
            'state': result.state,
            'label': result.label,
            'points': result.points,
            'student_answer': student,
            'expected': result.expected,
            'reason': result.reason,
            'caution': result.caution,
            'next': result.next_action,
        })

    # Reward: completed questions that were marked "ok" count as recovered fish
    report.recovered_fish = [
        item['knowledge'] for item in report.items if item['state'] == 'ok'
    ]
    # New knowledge fish unlocked today
    report.new_knowledge_fish = report.ok_count

    return report


def save_grading_log(root: Path, report: SessionReport) -> Path:
    """Append grading results to the grading log CSV."""
    path = root / 'records' / 'grading-log.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    today = date.today().isoformat()

    with path.open('a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(['item_id', 'source', 'subject', 'knowledge', 'prompt',
                             'student_answer', 'expected_answer', 'is_correct', 'status',
                             'note', 'date', 'day'])
        for item in report.items:
            writer.writerow([
                item['id'],
                'web-auto-grade',
                '',
                item['knowledge'],
                '',
                item.get('student_answer', ''),
                item.get('expected', ''),
                '1' if item['state'] == 'ok' else '0',
                item['state'],
                item.get('reason', ''),
                today,
                report.day,
            ])

    return path


# ── Helpers ──────────────────────────────────────────────────────────


def _variation(question: dict[str, Any]) -> str:
    """Generate a retry-variant prompt for a wrong question."""
    qid = str(question.get('id', ''))
    knowledge = str(question.get('knowledge', ''))
    if qid == 'D4-B2':
        return '变化题：360÷6 + 360÷4 = ____，能不能写成360÷10？'
    if '费曼' in knowledge:
        return '变化题：用一句话解释，300÷5 + 300÷10 为什么不能写成300÷15。'
    if '容量' in knowledge:
        return '变化题：3升600ml，每瓶300ml，可以装满几瓶？'
    if '退位' in knowledge:
        return '变化题：72 - 38 = ____。'
    return '变化题：把这题换一组数字，再试一次。'


def _caution(question: dict[str, Any]) -> str:
    """Get a caution message specific to the question type."""
    qid = str(question.get('id', ''))
    knowledge = str(question.get('knowledge', ''))
    if qid == 'D4-B2':
        return '先分别算两次除法，再相加；不能看到同一个被除数就把除数合并。'
    if '费曼' in knowledge:
        return '费曼题要讲"为什么"，固定口令：这是两次分，除数不能合并。'
    if '容量' in knowledge:
        return '容量题先统一单位，再做除法，最后补单位。'
    if '退位' in knowledge:
        return '退位减法先借位，再检查个位。'
    if '三单' in knowledge or 'he' in knowledge.lower():
        return '第三人称单数，动词要加 s 或 es。'
    return '先把题目关系说出来，再写算式。'


def entry_test_questions(mistake_knowledges: list[str]) -> list[dict[str, Any]]:
    """Generate 3 entry-test questions from recent mistake areas."""
    templates = {
        '除法陷阱': {'q': '480÷6+480÷8=____。能不能写成480÷14？', 'a': '140；不能'},
        '括号与混合运算': {'q': '[3600-(20+80×10)]÷20=____', 'a': '139'},
        '小数': {'q': '0.406+0.194=____', 'a': '0.6'},
        '容量': {'q': '4升200ml=____ml；每瓶300ml，可装____瓶。', 'a': '4200ml；14瓶'},
        '商和余数': {'q': 'a÷b商9余7，都乘10后，商____，余数____。', 'a': '9；70'},
        '三单': {'q': 'He ____ (like) fishing after school.', 'a': 'likes'},
        '进行时': {'q': 'Look! The boy is ____ (run).', 'a': 'running'},
    }
    questions = []
    for i, know in enumerate(mistake_knowledges[:3]):
        tmpl = templates.get(know, {'q': '复习：' + know, 'a': '待核查'})
        questions.append({
            'id': f'entry-{i+1}',
            'subject': '数学' if any(k in know for k in ['除法', '小数', '容量', '括号', '余数']) else '英语',
            'knowledge': know,
            'kind': 'entry_test',
            'prompt': tmpl['q'],
            'answer': tmpl['a'],
            'difficulty': 1,
        })
    return questions
