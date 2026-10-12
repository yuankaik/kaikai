---
name: bilibili-transcriber
description: B站视频→文字批量转写工具。直接调B站API绕过反爬获取音频流，faster-whisper离线转写，保存为MD。不需下载视频、不需yt-dlp、不需cookie。
---

# B站视频转文字

## 适用场景
- 批量转写B站UP主的全部视频为文字素材库
- 单个视频转文字
- 教育类/知识类内容归档
- **作文范文批量采集** — 短分P朗读合集，纯中文，转录质量高，适合做晨读材料（见 `references/essay-collection-patterns.md`）
- **技能课→练习题** — 数学/语法等技能类课程转录后可提炼技巧→程序化命题（见 `references/speed-math-case-study.md`）

## 前提条件

```bash
pip install faster-whisper  # 语音转文字
# ffmpeg 必须已安装
```

## 三步流程

### 1. 搜索UP主获取视频列表

```python
# 搜索UP主
search_url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword={urllib.parse.quote(keyword)}'
# 获取 mid

# 搜视频（备用方案，不需要wbi签名）
search_url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={urllib.parse.quote(keyword)}&page={page}'
```

### 2. 检查字幕 + 获取音频流

```python
# 获取cid
info = bili_get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
cid = info['data']['cid']

# 检查字幕（player/v2 不需要wbi签名）
player = bili_get(f'https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}')
subtitles = player.get('data', {}).get('subtitle', {}).get('subtitles', [])
# 如果 subtitles 非空 → 直接用字幕URL，不需要语音转写

# 获取音频流（playurl + fnval=16 不需要wbi签名）
playurl = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16&fnver=0&fourk=1'
player = bili_get(playurl)
audios = player['data']['dash']['audio']
audio_url = max(audios, key=lambda a: a.get('bandwidth', 0)).get('base_url', '')
```

### 3. 下载音频 + 转写

```python
# ffmpeg下载
cmd = ['ffmpeg', '-y', '-headers', f'User-Agent: {UA}\r\nReferer: https://www.bilibili.com/',
       '-i', audio_url, '-c', 'copy', output_path]
subprocess.run(cmd, ...)

# faster-whisper转写（离线模式必须设置）
os.environ['HF_HUB_OFFLINE'] = '1'
model = WhisperModel("base", device="cpu", compute_type="int8", local_files_only=True)
segments, _ = model.transcribe(audio_path, language='zh', beam_size=5, 
                                vad_filter=True,
                                vad_parameters=dict(min_silence_duration_ms=500))
```

## 关键注意事项

### B站API无需wbi签名的端点
以下端点**不需要** wbi 签名，可直接调用：
- `x/web-interface/view?bvid=xxx` — 视频信息
- `x/player/v2?bvid=xxx&cid=xxx` — 字幕检查
- `x/player/playurl?bvid=xxx&cid=xxx&fnval=16` — 音频流URL ✅ **核心**
- `x/web-interface/search/type` — 搜索

### 反爬要点
- User-Agent 必须用 Chrome 131+ 版本
- Referer 必须设为 `https://www.bilibili.com/`
- **关键：部分端点（搜索API）会返回412，需要补全请求头：**
  ```python
  headers = {
      'User-Agent': UA,
      'Referer': 'https://www.bilibili.com/',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'zh-CN,zh;q=0.9',
      'Origin': 'https://www.bilibili.com',
  }
  ```
- 请求间隔至少1秒（搜索API建议 3s 以上，连续412时加到5s）
- 不要高频调用 playurl（每个视频只调一次拿音频流）
- 如果搜索API连续412，换搜索关键词重试（不要硬怼同一个词）
- **搜索API返回total=0或page信息缺失时，换更短的关键词重试**

### 搜索噪音过滤（重要！）
当搜索词有歧义时（如「胡迪」→ 玩具总动员 Woody），过滤策略：
```python
# 方法1：限定作者名
matched = [v for v in videos if v.get('author') in target_authors]

# 方法2：用标题关键词二次过滤
edu_keywords = ['语文', '阅读', '作文', '写作', '文言文', '古诗词']
matched = [v for v in videos if any(kw in v['title'] for kw in edu_keywords)]

# 方法3：用多个搜索词交叉验证
keywords = ['胡迪老师主讲', '胡迪 读写', '胡迪 阅读']
# → 「胡迪老师主讲」精确匹配到教育内容，过滤掉玩具胡迪
```

### 搜索API返回空时的策略
当视频搜索返回total=0或完全空结果时（常见于特定名词组合），依次尝试：
1. **换UP主搜索** — `search_type=bili_user` 搜作者名，找到mid后再通过空间获取视频
2. **换更短关键词** — 「白马老师 4736 作文」→「白马老师 作文」→「白马老师」
3. **拆词重试** — 把专有名词拆成独立关键词分别搜
4. **等3秒换词** — 连续412说明被限频，换完全不同的词等冷却

### 已知B站教育UP主
| UP主 | MID | 内容 | 特征 |
|------|-----|------|------|
| 北大_白马老师 | 97293459 | 小学作文写作法（4+7+26） | 北大特聘，高途名师，多为营销短片；完整课程付费 |
| 牛娃学习加油站 | — | 速算巧算技巧课(18讲) | 丁丁老师，38万播放，纯中文转录质量好 |
| 尖子生课代表 | — | 英语阅读训练100篇 | 付费PDF，微信分发(aa1312185)；中英混合不可转录 |
| 家庭教育知识库 | — | 小学作文有声朗读 | 第①期20篇+第②期21-40篇 |
| 考试宝典13 | — | 作文范文200篇(BV1xDtzeJEg1) | 纯中文短音频(2分/篇)，转录质量好，8类覆盖 |
| 雅熙五感法写作文 | — | 同步作文范文(Y5系列) | 短格式(~13秒/篇)，画面文字型 |
| 橙子资料学习库 | — | 沪教牛津版2026四年级英语 | 课本精讲+单元测试卷PDF，微信分发 |
| 小中高动画站 | — | 四年级英语阅读训练100篇 | 同尖子生课代表，中英混合不可转录 |

### ⚠️ 转录前：先检查本地资源
B站转录有whisper同音字误差（即使纯中文也有5-10%的同音字替换）。**在发起批量转录之前，先搜索本地是否已有对应材料**（`search_files` 搜索 `shanghai-exams/`、桌面 `学习/` 等目录）。本地已有的DOCX/MD通常质量更高（无转录误差、可能带批注/框架拆解）。本会话发现本地「五年级作文背诵范文60篇」远优于B站转录版。

### Whisper离线模式
- 首次使用需联网下载模型到 `~/.cache/huggingface/`
- 之后设置 `HF_HUB_OFFLINE=1` + `local_files_only=True` 避免超时
- base模型142MB，中文效果足够；medium(1.5GB)更准但慢

### 性能参考（CPU, base模型）
- 18分钟视频 → 约4.5分钟转写（4x实时速度）
- 42分钟视频 → 约6.5分钟转写（6x实时速度）
- 模型加载：5秒（离线模式）

## 完整脚本模板

批量脚本: `scripts/bilibili_batch.py` — 修改 VIDEOS 列表后直接运行
作文→Word脚本: `scripts/essays_to_docx.py` — 转录MD文件夹→格式化晨读Word（含同音字修正表）
单文件脚本参考: `/home/adminkaikai/bilibili_retry.py` — 带重试的单视频处理

## 参考文件

- `references/douxin-case-study.md` — 窦昕案例：超长合集无字幕时的策略切换
- `references/speed-math-case-study.md` — 速算巧算课案例：18讲批量转录→技巧提炼→40天练习题生成
- `references/essay-collection-patterns.md` — 作文范文批量采集模式：短分P朗读→晨读材料
- `references/transcription-to-cards.md` — 转录文字→每日学习卡片的降维转换技法（适合家长场景）
- `references/transcription-to-exercises.md` — 转录文字→每日练习题的生成技法（数学/语法等技能类）
- `references/english-content-patterns.md` — B站英语教学视频的格式分类与提取替代方案（微信PDF模式）

## 实测性能 (CPU, base模型, Ubuntu WSL)

| 视频时长 | 下载 | 转写耗时 | 段数 | 速度比 | 内容类型 |
|----------|------|----------|------|--------|----------|
| 9:36 | 6.2MB | 106秒 | 298 | 5.4x | 语文 |
| 16:42 | 9.1MB | 161秒 | 476 | 6.2x | 语文 |
| 18:13 | 11.4MB | 268秒 | 519 | 4.1x | 语文 |
| 23:27 | 13.5MB | 285秒 | 554 | 4.9x | 语文 |
| 28:22 | 16.2MB | 279秒 | 1089 | 6.1x | 语文 |
| 31:49 | 18.1MB | 298秒 | 1128 | 6.4x | 语文 |
| 42:24 | 23.2MB | 385秒 | 1214 | 6.6x | 语文 |
| **18集批量(数学)** | **~160MB总** | **~55分钟总** | **~9,400段** | **~5.3x均值** | **数学(纯中文)** |

> 批量处理参考：18集×均16分钟，后台terminal执行，55分钟完成全量转录。

## 输出格式

每个视频一个MD文件：
```markdown
# 视频标题

> 来源: https://www.bilibili.com/video/BVxxx
> 转写工具: faster-whisper (base)

---

转写文字内容...
```

## ⚠️ 多分P合集识别与处理（关键！）

**问题：** B站大量教育类视频是多分P合集（标题含「全XX集」）。如果只取 `info['data']['cid']`，只会拿到第1P！后续P的内容完全丢失。

**检测方法：**
```python
info = bili_get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
pages = info['data'].get('pages', [])
if len(pages) > 1:
    # 这是多分P合集！逐P处理
    for p in pages:
        cid = p['cid']       # 每P独立cid
        page_num = p['page']  # 页码
        part_name = p['part'] # 分P标题
        duration = p['duration']  # 可能是秒数或"MM:SS"字符串
```

**时长格式兼容：**
```python
# duration 可能是 int(秒数) 或 str("223:40" 或 "3:45")
def parse_duration(dur):
    if isinstance(dur, str) and ':' in dur:
        parts = dur.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0]) * 60 + int(parts[1])  # "HHH:MM"
    return int(dur)
```

**音频完整性校验：**
```python
# 正常音频 ≈ 0.5MB/分钟。如果远小于预期，下载不完整
expected_mb = dur_min * 0.5
actual_mb = os.path.getsize(audio_path) / 1024 / 1024
if actual_mb < expected_mb * 0.3:
    print(f"⚠️ 音频异常小({actual_mb:.1f}MB vs 预期{expected_mb:.0f}MB)")
    # 原因：可能URL过期、或只下载了开头片段
```

**分P合集决策（修正版）：**
- 总分P ≤ 5 → ✅ 全部处理
- 总分P 6-15 → ⚠️ 筛选最对口的分P
- 总分P > 15 → 先处理前5P，其余按需
- 单P时长 < 10分钟 → 可能是预览/简介，检查内容后再决定

**窦昕案例修正：**
合集确实多分P！万能作文课8P(每P 33-43分钟)、阅读理解16P(每P 5-27分钟)。之前的"21个500小时合集无法处理"结论过时——应当**逐P挑选**最对口小学的，而非全量转写。

## ⚠️ 混合语言内容：英语教学视频不可转录

**问题：** B站大量英语教学视频是「中文讲解 + 英文内容朗读」混合音频。faster-whisper 的 `language` 参数只能指定一种语言：
- `language='zh'` → 英文段落被当成中文谐音转写，面目全非
- `language='en'` → 中文讲解被强行当英文，输出垃圾

**实测：** 四年级英语阅读训练100篇(BV129L8zQEKf)，P1转录结果几乎不可读。18讲数学课(纯中文)转录完美。

**替代方案：**
1. **找有CC字幕的** — player/v2 检查 subtitles，有字幕直接下载不需转写
2. **画面截图OCR（已走通，推荐）** — 英语阅读视频画面显示课文文字，比音频可靠。方案：`playurl`（fnval=16）返回的 dash 里除 `audio` 外还有 `video` 字段（视频流 base_url）→ ffmpeg 直接抽帧 `ffmpeg -y -headers "User-Agent: <UA>\r\nReferer: https://www.bilibili.com/" -i <video_url> -vf "fps=1/5" frame_%03d.jpg` → 逐帧 `vision_analyze`（deepseek-flash 原生多模态，三科实测准）批量识别画面文字。不用浏览器截图（老方案"反自动化超时"已弃用），也不用下载完整视频，直接从 dash 视频流抽帧，抽帧间隔按视频画面切换速度调（课件类 1/5~1/3 秒）
3. **UP主微信获取PDF** — 大量教育UP主的商业模式是「视频引流→加微信→发PDF」。标题含「配套讲义PDF+音频」的，视频本身只是广告，文字材料在微信分发

详细分析见 `references/english-content-patterns.md`。

## 常见问题

| 问题 | 解决 |
|------|------|
| HTTP 412 | 补全 Accept/Accept-Language/Origin 请求头；换搜索关键词 |
| 模型加载超时 | 设 `HF_HUB_OFFLINE=1` + `local_files_only=True` |
| API 超时 (TimeoutError) | 重试3次，间隔3秒；timeout设60s；terminal里跑比execute_code更稳定 |
| 音频流URL过期 | URL约2小时有效，超时需重新获取 |
| 后台进程无输出 | 用 `python3 -u` 禁用缓冲，print加 `flush=True`；即使看不见输出，文件仍在生成 |
| **中英混杂音频** | ⚠️ whisper对中英混杂语音识别极差。纯中文→`language='zh'`质量好；纯英文→`language='en'`可用；中英混合→两者都烂。英语阅读类视频（老师中文讲解+英文范文）不适合whisper转写，应改用画面OCR或其他方案 |
| **长音频超时** | execute_code有300s硬限制。45分钟以上音频（~9分钟转写）会超时。长视频用terminal+后台模式，不要用execute_code |
| **付费课内容** | B站很多教育UP主（白马老师等）视频只是营销片段，完整课程需加微信购买。判断标准：分P名含"购课+WX""获全集"等字样 |
| 英语教学视频转录 | ❌ 不可行。走画面OCR或找PDF源（见上节） |
