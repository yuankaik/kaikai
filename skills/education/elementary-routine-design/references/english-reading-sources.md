# English Reading Sources — Real 题库 vs AI-Generated

## Rule: Never AI-generate English reading passages

The user's quality standard is real, professionally-edited materials. AI-generated passages are grammatically correct but noticeably weaker:
- Questions tend to be vague ("What is the main idea?")
- Passages lack the tight editing of published materials
- The user WILL notice and reject them

## Verified Real Sources (Shanghai Grade 4-5)

### 1. 道客巴巴 Reading Passages
- **File**: `shanghai-exams/五年级特级教师资源-英语/03-英语阅读练习10篇.md`
- **Contents**: 10 passages at Grade 5 level with core vocab, comprehension questions, answers, and Chinese translations
- **Topics**: The Lazy Grasshopper (寓言), The Great Wall of China (文化), A Trip to the Moon (科幻), Save the Pandas (环保), A Special Birthday Gift (暖心), The Invention of Paper (历史), Sports Day (校园), A Visit from a Firefighter (职业), The Magic Paintbrush (传说), My Mother's Hands (抒情)
- **Format**: Bilingual with `### 核心词汇`, `### 阅读理解`, `### 参考答案`, `### 中文译文` sections
- **Quality**: Professional, well-structured, curriculum-aligned

### 2. 道客巴巴 English Essays (usable as reading)
- **File**: `shanghai-exams/五年级特级教师资源-英语/02-英语范文10篇-道客巴巴提取.md`
- **Contents**: 10 model essays at Grade 5 level with vocab boosters, structure analysis, and imitation tips
- **Topics**: My Desk-mate, My Favorite Season, My Day, My Hometown, My Dream, An Unforgettable Trip, My Favorite Animal, My Weekend Plan, A Letter to My Pen Pal, If I Were a Teacher
- **Usage as reading**: Extract the essay body, add 3 simple comprehension questions (topic, vocabulary, personal connection)

### 3. 昂立教育/绿光少儿教育 Test Papers
- **Directory**: `shanghai-exams/其他教育品牌/`
- **Files**: 
  - `昂立教育_三年级英语_期中测试.md`
  - `昂立教育_四年级英语_期末测试.md`
  - `昂立教育_五年级英语_冲刺测试.md`
  - `绿光少儿教育_三年级英语_阶段测试.md`
  - `绿光少儿教育_五年级英语_综合能力测试.md`
- **Extraction**: Each file has a `阅读理解` section with a short passage (80-120 words) + 5 multiple-choice questions
- **Regex**: `re.search(r'阅读理解[^#]*?(?=## Part|\Z)', text, re.DOTALL)`

### 4. 牛津英语词汇总表
- **File**: `shanghai-exams/牛津英语1-5年级词汇总表.md`
- **Usage**: Source for daily vocabulary exercises (10 words/day, topic-organized)

## Passage Count Planning

For a 40-day plan:
- **Ideal**: 40 unique passages
- **Acceptable**: 20-25 passages with 1.5-2x repetition (D-level students benefit from re-reading)
- **Unacceptable**: AI-generated filler passages

When real passages are insufficient, tell the user honestly and ask them to upload more materials. Never silently fill gaps with generated content.

## File Naming After Extraction

Clean names after removing AI duplicates:
```
阅读01.docx ~ 阅读20.docx  (student files)
阅读01-答案.docx ~ 阅读20-答案.docx  (parent answer keys)
```

Store in `英语新内容/03-阅读/` and `英语新内容/03-阅读/家长答案/`.
