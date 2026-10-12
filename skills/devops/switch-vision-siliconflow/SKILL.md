---
name: switch-vision-siliconflow
description: 切换 Hermes vision（图像识别）到硅基流动 SiliconFlow 的 Qwen3-VL 视觉模型，或切回 deepseek-flash。触发词：用户说「切」（约定单字，= 把 vision 切到硅基流动）、「切换硅基」「切硅基」「vision 换硅基流动」时触发。含 8/14 格式坑的规避方案。
---

# 切换硅基（Vision 模型切换）

把 Hermes 的 vision（看图/OCR/图像识别）在两个后端之间切换。

## 两个视觉后端现状

| 后端 | provider | 模型 | 状态 |
|------|----------|------|------|
| deepseek-flash | deepseek | deepseek-flash | ✅ 当前常驻，三科错题实测全准（须关 thinking） |
| 硅基流动 | openai | Qwen/Qwen3-VL-8B-Instruct | 备胎，8/14 有格式坑（见下） |

## 硅基流动关键信息

- base_url: `https://api.siliconflow.cn/v1`（OpenAI 兼容）
- API key: `sk-qxkbsqcpklxbacgblmenlvsuihcobonuevejxdrnckktlira`（8/14 用户提供，验证有效）
- 视觉模型（2026-08-14 实测）：
  - `Qwen/Qwen3-VL-8B-Instruct` ✅ 推荐（实测 40s 完整识别英语卷）
  - `Qwen/Qwen3-VL-30B-A3B-Instruct`（MoE 性价比款，未实测）
  - `Qwen/Qwen3-VL-32B-Instruct` ❌ 太大太慢，实测超时，不要用
  - `PaddlePaddle/PaddleOCR-VL-1.5`（专用 OCR，纯文字密集/表格场景）
  - `Qwen/Qwen3-VL-8B-Thinking` / `30B-A3B-Thinking`（带思考版，慢，识别场景不用）

## ⚠️ 8/14 的坑（关键）

8/14 首次切硅基流动，Hermes 内置 `vision_analyze` 实测报错：

```
unknown variant 'image_url', expected 'text'
```

**根因**：Hermes 的 vision 客户端（`resolve_vision_provider_client()`）对 `openai` provider 发图片的 content 格式，与硅基流动期望的 OpenAI 多模态格式不兼容。

**但 Python 直调硅基流动 API 是成功的**（8/14 用 urllib POST `/chat/completions`，8B 模型 40s 完整识别英语卷）。所以硅基流动本身没问题，是 Hermes 内置 vision 客户端的格式问题。

9/16 起 deepseek-flash 走 Hermes `vision_analyze` 成功（provider=deepseek 是内置，格式对）。硅基流动没有内置 provider，所以有格式坑。

## 两条切换路径

### 路径A：Hermes 内置 vision_analyze（需实测，可能仍撞格式坑）

```bash
hermes config set auxiliary.vision.provider openai
hermes config set auxiliary.vision.model "Qwen/Qwen3-VL-8B-Instruct"
hermes config set auxiliary.vision.base_url "https://api.siliconflow.cn/v1"
hermes config set auxiliary.vision.api_key "sk-qxkbsqcpklxbacgblmenlvsuihcobonuevejxdrnckktlira"
```

然后清掉 deepseek 的 `extra_body`（thinking disabled 不适用于 Qwen3-VL），再 `vision_analyze` 实测。

⚠️ 若仍报 `unknown variant 'image_url'` → 走路径B（直调），或切回 deepseek-flash。

### 路径B：Python 直调（8/14 已验证可行，绕开 vision_analyze 格式坑）

```python
import base64, json, urllib.request

def siliconflow_vision(img_path, prompt, model="Qwen/Qwen3-VL-8B-Instruct"):
    key = "sk-qxkbsqcpklxbacgblmenlvsuihcobonuevejxdrnckktlira"
    b64 = base64.b64encode(open(img_path, "rb").read()).decode()
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        "https://api.siliconflow.cn/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=120).read())["choices"][0]["message"]["content"]
```

## 切回 deepseek-flash

```bash
KEY=$(grep '^DEEPSEEK_API_KEY=' ~/.hermes/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs)
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.vision.model deepseek-flash
hermes config set auxiliary.vision.base_url "https://api.deepseek.com/"
hermes config set auxiliary.vision.api_key "$KEY"
# 恢复 extra_body thinking disabled（deepseek 必需，否则思考吃光 max_tokens）
```

## 验证方法

用桌面错题图实测：`/mnt/c/Users/admin/Desktop/day02.jpg`（或佳乐错题投递箱里的图），看能否读出题目 + 红笔打叉批改。

## 选型建议

- 佳乐订正本/错题/红笔 → deepseek-flash 已够用（三科全准），不必切
- 复杂表格/几何图形/统计图表 → 切硅基流动 Qwen3-VL 或 PaddleOCR-VL（强项）
- 切硅基流动遇到 vision_analyze 格式坑 → 用路径B直调，别硬怼
