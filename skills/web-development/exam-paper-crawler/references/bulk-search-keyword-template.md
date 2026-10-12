# 知识点×全网资源批量搜索 - 关键词模板

> 使用方法：将已有知识点清单按此模板分组，生成搜索关键词。
> 核心原则：贴吧用 pan.quark.cn + 通用词，道客巴巴用沪教版+通用词（不要品牌名！），B站不限。

---

## 贴吧搜索关键词模板（搜夸克网盘链接）

⚠️ **只能搜1-2次！首搜用最关键的关键词！**

```
pan.quark.cn 小学 数学
pan.quark.cn 小学 语文
pan.quark.cn 小学 英语 语法
pan.quark.cn 小学 口算
pan.quark.cn 小学 教辅 全套
```

❌ 不要搜这些（触发安全验证）：
```
pan.quark.cn 学而思      → 触发验证
pan.quark.cn 新东方      → 触发验证
pan.quark.cn 四年级      → 触发验证（通用词但含数字）
pan.quark.cn 沪教版      → 触发验证
```

---

## 道客巴巴搜索关键词模板（搜文档）

✅ 可以搜：
```
沪教版 四年级 数学 知识点
沪教版 四年级 下册 语文 阅读理解
上海小学 英语 语法 练习
小学 口算 天天练
泡泡英语 小学            ← 代替"新东方泡泡英语"
小学 奥数 培优 讲义     ← 代替"学而思培优"
```

❌ 不要搜品牌词（被过滤）：
```
新东方 泡泡英语 小学     → 无结果
学而思 培优 小学数学     → 结果极少且不精准
精锐教育 小学            → 无结果
```

---

## B站搜索关键词模板（搜视频）

✅ 品牌词不限，都可以搜：
```
学而思 小学数学 全套
新东方 小学英语
沪教版 数学 四年级
上海小学 语文 阅读理解
精锐教育 小学            ← B站品牌词不限
```

JS提取脚本：
```javascript
// 从搜索结果页提取视频信息
Array.from(document.querySelectorAll('.bili-video-card')).map(el => ({
  title: el.querySelector('.bili-video-card__info--tit')?.textContent?.trim(),
  url: 'https:' + (el.querySelector('a')?.getAttribute('href') || ''),
  plays: el.querySelector('.bili-video-card__stats--play')?.textContent?.trim(),
  up: el.querySelector('.bili-video-card__info--author')?.textContent?.trim()
}))
```

---

## 三平台并行 delegate_task 模板

```python
delegate_task(tasks=[
  {
    "goal": "B站搜索上海小学教学视频...",
    "toolsets": ["browser"],
    "context": "搜索关键词：学而思小学数学、沪教版数学四年级、新东方小学英语、阅读理解。用browser_console提取结果。输出中文。"
  },
  {
    "goal": "道客巴巴搜索沪教版语文英语资源...",
    "toolsets": ["browser"],
    "context": "搜索关键词：泡泡英语小学、小学奥数培优、沪教版语文阅读理解四年级、上海小学英语语法练习。注意：不要用品牌词(学而思/新东方)。用browser_snapshot提取结果。输出中文。"
  },
  {
    "goal": "贴吧搜夸克网盘资源...",
    "toolsets": ["browser"],
    "context": "搜索关键词：pan.quark.cn 小学 数学（只搜1-2次，首次必须用最有价值的关键词）。如果触发百度安全验证空白页，记录失败。输出所有发现的pan.quark.cn链接。"
  }
])
```

---

## 知识点编号规范（用于匹配报告）

| 科目 | 前缀 | 范围 | 示例 |
|:---|:---|:---|:---|
| 数学 | M | M1-1 ~ M5-10 (170点) | M4-1 大数的认识 |
| 语文 | C | C-P1 ~ C-WR7 + C-P1古诗 (70点) | C-R3 概括内容 |
| 英语 | E | E-L1 ~ E-P4 (94点) | E-G11 人称代词 |
