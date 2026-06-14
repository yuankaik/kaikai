# 深层资源库路线图

生成日期：2026-06-04

## 已补核心资源

- 袁佳乐学习画像：`learner-profile-yuanjiale.md`
- 上海小学 1-5 年级知识地图：`records/shanghai-primary-knowledge-map.csv`
- 上海课程与教材来源说明：`docs/shanghai-curriculum-sources.md`
- 四年级下期末冲刺地图：`records/g4b-final-sprint-map.csv`

## 还需要继续补的资源库

1. 学校同步资料库：`records/school-sync-log.csv`，记录老师复习范围、单元卷、默写范围、课堂重点、错题照片来源。
2. 题型模板库：`templates/problem-types/`，记录数学计算题、应用题、语文阅读题、英语句型题的可复用模板。
3. 游戏叙事模板库：`templates/game-narrative/`，记录海域名、鱼种名、Boss 名、徽章、积分奖励、失败后重试话术。
4. PDF 统一模板系统：`templates/pdf-layout/`，固定页眉、进度条、模块间距、题目样式、练字页、今日渔获页。
5. 批改规则库：`docs/grading-rubric.md`，统一照片识别、OCR 疑义、口算错误、抄错题、单位漏写等判定规则。
6. 复习间隔库：`records/review-schedule.csv`，规定 D1、D3、D7、D14 回炉和毕业规则。
7. 情绪与状态库：`records/energy-state-log.csv`，把绿色、黄色、红色状态和当天题量绑定。
8. 课内语文字词库：`records/chinese-textbook-words.csv`，按上海语文课本课次抽取生字词、古诗、重点词、练字候选字。
9. 英语课本句型库：`records/english-pattern-bank.csv`，整理牛津上海版各年级模块主题、核心句型、替换词、易错点。
10. 家长执行脚本库：`docs/parent-coach-scripts.md`，沉淀孩子抗拒、全错、全对、拖延、字迹潦草、讲不出来时的第一句话。

## 下一阶段建设顺序

1. 先补 `templates/pdf-layout/`，解决 Day2 版式反复修改和游戏元素丢失问题。
2. 再补 `records/g4b-final-sprint-map.csv` 的题型模板映射。
3. 晚上拿到 Day2 照片后，先批改入库，再生成 Day3，不提前批量生成。

## 生成原则

每日练习 = 袁佳乐画像约束 + 当天状态 + 上海知识地图 + 错题回炉 + 游戏叙事模板 + 统一版式模板。  
凡是不能被批改、不能进入掌握状态、不能影响次日练习的内容，都不应占用当天纸面空间。
