# 儿童爽文A4紧凑排版

用于10岁儿童阅读的爽文小说。关键词：紧凑省纸、字号大、插图嵌入、无空白页、连续排版。

## CSS

```css
@page { size: A4 portrait; margin: 1.8cm 1.6cm 1.6cm 1.6cm;
  @bottom-center { content: "— " counter(page) " —"; font-family: "Noto Serif CJK SC", serif; font-size: 7.5pt; color: #aaa; }
}
@page cover { margin: 0; @bottom-center { content: none; } }
body { font-family: "Noto Serif CJK SC", sans-serif; font-size: 11pt; line-height: 1.85; color: #1a1a1a; text-align: justify; }
.cover-page { page: cover; page-break-after: always; width:100%; height:100vh; overflow:hidden; }
.cover-page img { width:100%; height:100vh; object-fit:cover; }
.illustration { page-break-before: avoid; page-break-after: avoid; text-align: center; margin: 8pt 0 4pt 0; }
.illustration img { max-width: 100%; max-height: 78vh; object-fit: contain; }
.caption { font-size: 7.5pt; color: #aaa; text-align: center; margin: 2pt 0 0 0; text-indent: 0; font-style: italic; }
h1 { font-size: 24pt; text-align: center; font-weight: bold; letter-spacing: 4pt; margin-top: 100pt; }
h2 { font-size: 16pt; text-align: center; margin-top: 18pt; margin-bottom: 3pt; page-break-before: avoid; page-break-after: avoid; letter-spacing: 2pt; }
h3 { font-size: 13pt; text-align: center; color: #777; font-weight: normal; }
p { text-indent: 1.6em; margin: 0 0 0.1em 0; text-align: justify; }
h2 + p { text-indent: 0; }
hr { border: none; text-align: center; margin: 14pt 0; overflow: visible; }
hr::after { content: "✦   ✦   ✦"; font-size: 8pt; color: #bbb; letter-spacing: 3pt; }
blockquote { margin: 4pt 14pt; font-size: 9.5pt; color: #666; font-style: italic; }
```

## 插图占位替换

MD中用 `[插图: 场景描述]` 占位。regex替换为：
```html
<div class="illustration"><img src="PATH"/><p class="caption">场景描述</p></div>
```

## 图片匹配规则

按文件修改时间正序 = 章节顺序。**不要用字母排序**——用户通常按章节顺序上传。

## 封面

满版A4：`@page cover` 零边距 + `object-fit:cover`。
