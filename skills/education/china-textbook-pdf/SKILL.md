---
name: china-textbook-pdf
description: 从中小学官方教科书仓库 (TapXWorld/ChinaTextbook, 82K⭐) 按需下载全学科·全版本·全学段的官方教科书 PDF（人教/沪教/苏教/北师大等）。当用户要官方教材、课本原文、备课参考时使用。含按 git blob API 单文件下载与 markitdown 转 Markdown。
category: education
tags: [textbook, pdf, education, china, 教科书, tapxworld, markitdown]
---

# 官方教科书 PDF 下载 (ChinaTextbook)

## 触发条件

用户要：
- 小学/初中/高中/大学的**官方教科书 PDF**（课本原文）
- 特定版本教材（人教版、沪教版/上海版、苏教版、北师大版、冀教版…）
- 备课/命题/出练习时的课本依据

**与 chinese-ebook-download 的区别**：那个技能下载的是**文学类电子书**(EPUB/MOBI)；本技能下载的是**教育部审定的官方教科书 PDF**，两库互补。

## 数据源

**TapXWorld/ChinaTextbook** — 82K⭐，43.5GB 仓库（**绝不能 clone**，必须按需单文件下载）。

- 许可：无 license 声明（视作公共教育资料；仅供个人学习备课，勿商用传播）
- 顶层目录：`小学/` `初中/` `高中/` `大学/` `小学（五•四学制）/` `初中（五•四学制）/` `学数学最重要的刷习题在这里/`
- 结构：`<学段>/<科目>/<版本>/义务教育教科书·<科目><年级><册>.pdf`

## 一、列出目录（先看有什么）

```python
import urllib.request, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def gh(url):
    r = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/vnd.github+json"})
    return json.loads(urllib.request.urlopen(r, timeout=30, context=ctx).read().decode())

t = gh("https://api.github.com/repos/TapXWorld/ChinaTextbook/git/trees/HEAD?recursive=1")
paths = [x["path"] for x in t.get("tree", [])]
# 例：找沪教版四年级英语
for p in sorted(set(p for p in paths if p.startswith("小学/") and "沪教版" in p and "四年级" in p)):
    print(p)
```

**注意**：recursive 会截断（3112 条上限），大范围搜索时按学段分次查：先查顶层 → 进 `小学/` 逐科目 → 或直接用 API 查子目录：

```python
d = gh("https://api.github.com/repos/TapXWorld/ChinaTextbook/contents/" + urllib.parse.quote("小学/数学"))
```

**版本命名**：上海本地用 `沪教版`（数学另有`上海版`路径）、国家统编 `人教版`、江苏 `苏教版`、北京 `北师大版`、河北 `冀教版`、西南 `西南大学版`。

## 二、按需下载单个 PDF（关键：走 git blob API）

**不要用 `download_url`（raw.githubusercontent.com）— 连接会被重置。**

正确路径：contents API 拿 `sha` → blob API base64 解码落盘：

```python
import urllib.request, urllib.parse, json, ssl, base64, os
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def gh(url):
    r = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/vnd.github+json"})
    return json.loads(urllib.request.urlopen(r, timeout=60, context=ctx).read().decode())

path = "小学/英语/沪教版/义务教育教科书·英语（三年级起点）四年级上册.pdf"
meta = gh(f"https://api.github.com/repos/TapXWorld/ChinaTextbook/contents/{urllib.parse.quote(path)}")
blob = gh(f"https://api.github.com/repos/TapXWorld/ChinaTextbook/git/blobs/{meta['sha']}")
data = base64.b64decode(blob["content"])
out = os.path.expanduser("~/Desktop/") + os.path.basename(path)
open(out, "wb").write(data)
assert data[:4] == b"%PDF"      # 校验真 PDF
print("OK", out, round(len(data)/1024/1024,2), "MB")
```

**坑位**：
- 仓库用 Git LFS/分片时，部分大 PDF 会被拆成 `xxx.pdf_merge_folder/xxx.pdf.1` `.2` — 需下齐分片再合并（`cat 部分 > 完整.pdf`）
- 单文件 5–30MB 常见；GitHub contents API 对 >1MB 返回 base64 需走 blob 接口（>100MB 会拒绝）
- 国内网络下 codeload/raw 均不稳，blob API 实测最稳

## 三、PDF → Markdown（用于提取课本文字/命题）

用已安装的 markitdown：

```python
from markitdown import MarkItDown
md = MarkItDown()
print(md.convert("/path/to/课本.pdf").text_content[:2000])
```

markitdown 也可转 docx/xlsx/pptx → markdown（表格保留）。装齐依赖：

```bash
pip install --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple 'markitdown[all]'
```

扫描版 PDF 无文字层时 markitdown 只出图 — 需先 OCR（见 correction-ocr / ocr-tools 技能）。

## 四、上海（佳乐四年级）相关路径速查 — 实测（2026-10）

**重要：上海本地教材覆盖不全。** 实测结论：

| 科目 | 沪教/上海版是否存在 | 实际路径 |
|------|---------------------|----------|
| 英语 | ✅ 有 | `小学/英语/沪教版/义务教育教科书·英语（三年级起点）四年级上册.pdf` |
| 美术 | ✅ 有 | `小学/美术/沪教版/…四年级上册.pdf` |
| 书法 | ✅ 有（沪科教版） | `小学/语文·书法练习指导/沪科教版/…` |
| 数学 | ❌ **无沪教版** | 小学/数学 下只有：人教/冀教/北京/北师大/苏教/西南大学/西南师大/青岛版。上海数学需另找 |
| 语文 | ⚠️ 用统编版 | `小学/语文/统编版/`（全国统编，上海也用） |

**⚠️ 陷阱**：`小学（五•四学制）/` 是**山东五四制**（青岛版/鲁科版），**不是上海的**。别被"五四学制"误导。

其他版本命名：`人教版`(全国统编)、`苏教版`(江苏)、`北师大版`(北京)、`冀教版`(河北)、`青岛版`(山东)。

人教版数学四年级上册实际大小 21.68MB（已实测下载成功）。

## 陷阱

1. **绝不 clone**（43.5GB）— 只按需单文件下载
2. **不用 raw.githubusercontent** — 走 contents→blob API
3. **下完必验 PDF 头** `%PDF` — 防拿到 HTML 错误页
4. **分片文件** `.pdf.1/.2` 要合并
5. **版权**：官方教材有版权，仅限个人学习/备课参考，不传播不商用
6. 找不到某版本 → 先用 contents API 逐层列目录确认，别猜路径
