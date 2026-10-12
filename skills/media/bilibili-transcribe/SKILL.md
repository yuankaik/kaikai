---
name: bilibili-transcribe
description: B站视频语音转文字——搜索UP主、检查CC字幕、下载音频流、faster-whisper转写、输出MD。不需要yt-dlp，不需要登录/Cookie。
---

# B站视频 → 文字 转写

## 触发条件
- 用户要把B站视频/UP主内容转成文字
- "把XX的B站视频转成文字/字幕/笔记"
- "提取B站视频的文稿"

## 依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| `faster-whisper` | 语音→文字（本地，免费） | `pip install faster-whisper` |
| `ffmpeg` | 下载音频流 | `apt install ffmpeg` |

**不需要 yt-dlp** —— B站 playurl API 直接返回音频流 URL。

## 工作流

### 1. 搜索UP主 → 获取视频列表

```python
# 搜索UP主
GET https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword=xxx
→ 得到 mid

# 获取视频（搜索API，不需要wbi签名）
GET https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=xxx&page=N
→ 筛选 author == UP主名
```

### 2. 检查CC字幕

```python
GET https://api.bilibili.com/x/web-interface/view?bvid=xxx  → 得到 cid
GET https://api.bilibili.com/x/player/v2?bvid=xxx&cid=xxx
→ data.subtitle.subtitles: 如果有就下载字幕JSON，不需要转写
```

### 3. 获取音频流（关键：不需要wbi签名）

```python
# fnval=16 返回 DASH 格式，audio 字段直接有 URL
GET https://api.bilibili.com/x/player/playurl?bvid=xxx&cid=xxx&fnval=16&fnver=0&fourk=1
→ data.dash.audio[].base_url  # 选最高 bandwidth 的
```

**注意**: URL 可能以 `//` 开头，需要补 `https:`。

### 4. ffmpeg 下载音频

```bash
ffmpeg -y \
  -headers "User-Agent: Mozilla/5.0...\r\nReferer: https://www.bilibili.com/" \
  -i "$AUDIO_URL" -c copy output.m4a
```

### 5. faster-whisper 转写

```python
import os
os.environ['HF_HUB_OFFLINE'] = '1'     # 离线模式
os.environ['TRANSFORMERS_OFFLINE'] = '1'

from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8", local_files_only=True)

segments, info = model.transcribe(
    audio_path, language="zh", beam_size=5,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500)
)
```

### 6. 保存为 Markdown

加来源链接、时间戳。每段文字自然分段。

## 模型选择

| 模型 | 大小 | 中文效果 | CPU速度 | 建议场景 |
|------|------|----------|---------|----------|
| tiny | ~75MB | 勉强 | 最快 | 应急 |
| **base** | ~145MB | 可用 | ~4x实时 | **默认推荐** |
| small | ~480MB | 不错 | ~2x实时 | 高质量需求 |
| medium | ~1.5GB | 好 | ~1x实时 | GPU环境 |

## 性能参考

- base模型 + CPU(int8): 18分钟视频 → 4.5分钟处理（约4x实时）
- 首次加载模型需要下载CTranslate2格式（~145MB for base）
- 后续加载秒级（已缓存时~4秒）

## 常见问题

### 412 Precondition Failed
yt-dlp 或直接访问被B站wbi签名拦截 → 改用 playurl API (fnval=16)，不需要签名。

### faster-whisper 加载卡住
HuggingFace 不通 → 设置 `HF_HUB_OFFLINE=1` + `local_files_only=True`。

### 输出质量
base模型对中文有少量识别误差（如"非连续文本"→"非年续新文本"），但整体可读性良好。对知识素材库来说够用。

## 相关技能

## 脚本

- `scripts/bilibili_batch.py` — 批量转写脚本，修改 VIDEOS 列表即可用

## 参考

- `references/bilibili-api.md` — B站 API 详细文档（端点、参数、返回格式）

## Use-Case Variants

This skill covers the full B站→文字 pipeline. Two common framing variants:

### Variant A: 知识库构建 (Knowledge Base)
When the goal is building a searchable text knowledge base from educational UP主 content:
- Prioritize CC字幕 over transcription (zero cost, perfect accuracy)
- Organize output by UP主 → playlist → video
- Add metadata headers (来源链接, 转写工具, 时间戳)
- Known resource: 梓墨说语文 at `C:\Users\admin\Desktop\学习\梓墨说语文\` (14 videos transcribed)

### Variant B: 批量转写 (Batch Processing)
When transcribing an entire UP主 channel:
- Use `scripts/bilibili_batch.py` — edit the VIDEOS list and run
- Process videos serially with API rate limiting (≥1s between requests)
- Audio URLs expire quickly — download immediately after fetching
- Track progress by checking output directory, not stdout (background mode buffers output)

## Related Skills

- `youtube-content`: YouTube 转文字
- `mediacrawler`: B站视频信息+评论爬取（不能转语音）
