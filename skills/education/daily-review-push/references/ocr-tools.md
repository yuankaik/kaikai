# OCR 工具实测对比（完整版）

日期：2026-06-22，环境：WSL (Python 3.14) + Windows 11
最后更新：2026-06-22（新增 Tesseract 对比）

## 已测工具

### Pix2Text (3,160⭐) — ✅ 可用，优连续中文+公式
- **安装**: `pip install pix2text` (依赖 PyTorch，首次下载 ~2GB)
- **Python 3.14**: ✅ 兼容
- **中文准确率**: 打印体 80-90%，手写体 10-20%
- **数学公式**: 支持，输出 LaTeX (`\frac`, `\begin{matrix}` 等)
- **关键 API**:
  - `recognize_text(image)` — 纯文字 OCR，中文效果好
  - `recognize_formula(image)` — 公式检测（纯文字图会超时）
  - `recognize(image)` — 混合模式（易混淆文字和公式，不推荐）
- **速度**: 首次 ~30s（含模型下载 130MB），后续 ~5s/张 (CPU)
- **缺陷**: 无法区分红笔标记 vs 黑色字，手写识别差

### Tesseract 5.x + chi_sim — ✅ 可用，优数字/表格/结构化
- **安装**: `sudo apt install tesseract-ocr tesseract-ocr-chi-sim`
- **Python**: `pip install pytesseract`
- **中文准确率**: 打印体 80-85%，数字/金额 95%
- **强项**: 表格、价格、选择题选项（A/B/C/D）、单位换算
- **弱项**: 连续中文段落不如 Pix2Text 连贯
- **速度**: ~2s/张 (CPU)，无需 GPU，模型极小
- **缺陷**: 同 Pix2Text，红黑不分、手写差

### PaddleOCR (83,200⭐) — ❌ WSL 不兼容
- **安装**: 需要 Python 3.12 venv（paddlepaddle 不支持 3.14）
- **3.x 版**: ONEDNN `ConvertPirAttribute2RuntimeAttribute` 错误
- **2.x 版**: SIGILL 非法指令 (CPU 不兼容)
- **根因**: WSL 虚拟化层 CPU 指令集不完整，PaddlePaddle 二进制依赖 AVX2/AVX512
- **结论**: 当前环境无法使用

### Surya OCR (20,900⭐) — ❌ API 不兼容
- **问题**: 0.20.0 版本 API 完全重写，旧版导入路径失效
- **未深入**: 因时间投入 PaddleOCR，跳过探索

## 实测数据（3 张错题本照片，双引擎对比）

| 照片 | Tesseract | Pix2Text | 结论 |
|------|-----------|----------|------|
| 数学卷（计算+换算） | ✅ 数字/表格准 | ⚠️ 部分乱码 | Tesseract 优 |
| 语文阅读理解 | ⚠️ 顶部乱码 | ✅ 连续文本全 | Pix2Text 优 |
| 语文基础卷 | ✅ 结构清晰 | ⚠️ 文本多但杂 | 各有优劣 |

## 最终方案：三步流水线 (correction-ocr 技能)

```
拍照 → vision(minicpm-v) 看图定位红笔区域
     → Tesseract(数字/表格) + Pix2Text(中文/公式) 双引擎 OCR
     → 结构化入库 → 每日复习追踪.json
```

专用技能：`correction-ocr`（education/），完整实现了上述流水线。

- **Tesseract**: 用于数字、金额、表格、选择题
- **Pix2Text**: 用于连续中文段落、数学公式（LaTeX）
- **共同盲区**: 手写字（双引擎皆差）、红黑区分（靠 vision 补）

## 数据迁移记录

2026-06-22 从 `D:\Kaideepseek\worktrees\ace-angler-phase1-checkpoint-a` 迁移：
- 数学 107 条（来自 Day spec 错题 + P0 题型模板）
- 英语 215 条（来自 vocab-log.json + Day spec 英语章节）
- 语文 8 条（来自 Day spec 语文章节）
- 总计 330 条，写入 `/mnt/c/Users/admin/Desktop/shanghai-exams/每日复习追踪.json`
