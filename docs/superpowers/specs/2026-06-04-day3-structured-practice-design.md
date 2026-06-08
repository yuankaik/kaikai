# Day3 Structured Practice Design

生成日期：2026-06-04

## 背景

Day2 已完成并上传作业照片。批改结果显示：已批改 16 题，13 题正确，3 题需要回炉。第 2 页 Boss 战、家校雷达、费曼教学和第 3 页收杆练字未看到完整提交。因此 Day3 不应直接推进新难点，而应生成“回炉 + Boss 补验 + 轻量练字”的练习。

## 目标

建立 Day3 的结构化生成链路：

`Day2 批改结果 -> Day3 practice spec -> A4 PDF renderer -> PDF QA`

Day3 生成物必须同时满足教学目标和打印可读性：

- 只抓 1 条主知识鱼：除法陷阱。
- 回炉 3 个 Day2 真实问题：除法计算与运算顺序、容量单位换算和有余数除法、两位数退位减法。
- 补做 Boss 判断：解释为什么除数不能合并。
- 主体题目字号不低于 10.5pt。
- 辅助说明字号不低于 8.5pt。
- 数字和单位不可断行，例如 `255ml`、`6升641ml`。
- 练字页不空置，加入家长观察与“最稳一格”反馈。

## 架构

新增三个小边界，避免继续在 PDF 脚本里手写散题：

- `tutor_core/day3_spec.py`：读取 Day2 批改结果，生成结构化练习 spec。
- `rendering/typography.py`：负责按真实宽度换行，并保护单位 token。
- `rendering/day_pdf.py`：把 spec 渲染为 A4 PDF。

脚本入口为 `scripts/make_day3_from_day2.py`。它不覆盖 Day2，只输出：

- `practice/specs/Day3-海王龙的逆向追踪.json`
- `Day3-海王龙的逆向追踪.pdf`

## 验收标准

1. 从 `submissions/2026-06-04-Day2/grading-result.csv` 生成 Day3 spec。
2. spec 中包含 Boss 补验、3 条回炉题、费曼讲题、家校雷达、收杆练字。
3. PDF 为 A4，主体题目字号不低于 10.5pt。
4. PDF 文本抽取中不出现 `m` 与 `l` 被拆成相邻两行的情况。
5. 运行 `python -m unittest discover -s tests -v` 通过。

## 不做的事

- 不重新批改 Day2。
- 不覆盖 Day2 PDF。
- 不提前生成 Day4 及以后材料。
- 不引入 Web 应用或数据库。
