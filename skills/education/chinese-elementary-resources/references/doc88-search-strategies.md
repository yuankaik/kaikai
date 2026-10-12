# Doc88 Chinese Education Resource Search Guide

## Platform Reality

doc88.com (道客巴巴) is a document-sharing platform. It can find teaching methodology but NOT student worksheets from branded sources. Full document access requires login + points; the viewer renders content as images/canvas — text extraction from document pages is impossible.

## What Works

| Search Type | Example | Returns |
|-------------|---------|---------|
| Generic grade exercises | "沪教版 语文 阅读理解 四年级" | Rich: real exam papers, exercises |
| Grammar/vocab topics | "上海小学 英语 语法 练习" | Rich: comprehensive grammar guides |
| Arithmetic drills | "小学 口算 速算 天天练" | Rich: daily drill sheets |
| Teacher profiles | "景洪春 语文 小学" | Teaching philosophy, lesson observations |
| Teacher methods | "吴正宪小学数学教学优秀案例" | Classroom transcripts, teaching cases |
| Shanghai teacher list | "上海 小学 特级教师 数学" | Complete teacher roster with subjects |

## Shanghai Primary School Special-Grade Teachers Found

| Name | Subject | School |
|------|:------:|--------|
| 景洪春 | 语文 | 徐汇区高安路第一小学 |
| 李祯忠 | 科技 | 徐汇区向阳小学 |
| 高一敏 | 幼教 | 徐汇区科技幼儿园 |

## National Primary School Master Teachers Found

| Name | Subject | Key Contribution |
|------|:------:|-----------------|
| 吴正宪 | 数学 | 情境教学法, 课堂实录案例 |
| 沈峰 | 英语 | PWP五环节, Free talk教学 |
| 王凌 | 数学 | 35条教学语录（经验性学习） |
| 于永正 | 语文 | 五重教学法 |
| 窦桂梅 | 语文 | 主题教学法 |
| 丁有宽 | 语文 | 读写结合法 |
| 贾志敏 | 语文 | 作文教学五字诀 |
| 乔亚梦 | 语文 | 六步教学法 |
| 武凤霞 | 语文 | 分年级专题体系 |
| 王立根 | 语文 | 22写作训练点 |
| 颜思笠 | 语文 | 思维导图分类法 |
| 于漪 | 语文 | 教文育人 |

## What Doesn't Work

| Attempt | Why It Fails |
|---------|-------------|
| "学而思 小学数学" | Brand name blocked (copyright) |
| "新东方 小学英语" | Brand name blocked |
| "精锐教育 小学练习" | Only brand intros, no exercises |
| "昂立教育 小学" | Only brand intros, zero exercises |
| Teacher name + "练习题" | Teachers publish pedagogy, not workbooks |

## Brand Name Workarounds

| Brand | Use Instead |
|-------|------------|
| 学而思 | "培优 小学数学" or "小学数学培优" |
| 新东方 | "泡泡英语 练习" or "青少版新概念" |
| 精锐教育 | "小升初 语文 模拟" (generic) |
| 昂立教育 | "少儿英语 进阶 练习" (generic) |

## Technical Limitations

- **Search result pages**: Text snippets ARE extractable via browser_snapshot. 10 results per page with truncated previews.
- **Document detail pages**: Content is canvas/image-rendered — NOT in DOM. `browser_console` extraction returns empty. Do not attempt.
- **Full downloads**: Require login + points. Not worth attempting.
- **URL param search**: Does NOT work (`?keyword=xxx`). Must use JS form submission via `browser_type` + `browser_click`.
- **Stealth warning**: doc88 triggers browserbase stealth warnings. Pages work but may be slower.

## Quark Cloud Drive Limitations

- **List API**: Works with cookies (lists files, directories)
- **Save-to-drive API**: Returns 401 even with fresh cookies. Browser-only operation.
- **Cookie lifetime**: ~24 hours
- **Recommendation**: Abandon Quark for programmatic access. Manual browser save or skip entirely.

## Recommended Strategy

When scraping fails after 2 attempts → pivot to self-generation. We already have:
- Knowledge point framework (120 math, 38 Chinese, 44 English)
- Teaching methods from real teachers (吴正宪情境法, 沈峰PWP, 景洪春探究法)
- Textbook references (53天天练, 一课一练)

**The scorched-earth strategy**: Generate everything upfront. Don't wait for platforms to improve — they only get worse. One session of generating 600 math problems + 150 Chinese + 150 English = independence from all platforms forever.
