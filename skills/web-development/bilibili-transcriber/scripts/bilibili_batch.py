#!/usr/bin/env python3
"""
B站视频 → MD 批量转写脚本
用法: 修改 VIDEOS 和 OUTPUT_DIR，然后 python3 -u bilibili_batch.py

依赖: faster-whisper (base模型), ffmpeg
前提: 模型已缓存到 ~/.cache/huggingface/ (否则设置 HF_HUB_OFFLINE=0)
"""
import urllib.request, json, gzip, subprocess, os, time

# ========== 配置区 ==========
OUTPUT_DIR = '/mnt/c/Users/admin/Desktop/学习/XXX'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# 格式: (bvid, "安全文件名不含特殊字符")
VIDEOS = [
    # ("BVxxxxxxxxx", "视频标题简写"),
]
# ============================

def log(msg):
    print(msg, flush=True)

def bili_get(url, retries=3):
    headers = {
        'User-Agent': UA,
        'Referer': 'https://www.bilibili.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Origin': 'https://www.bilibili.com',
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=30)
            data = resp.read()
            if resp.headers.get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            return json.loads(data)
        except Exception as e:
            if attempt < retries - 1:
                log(f"  API重试{attempt+1}: {e}")
                time.sleep(5)
            else:
                raise

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载模型
from faster_whisper import WhisperModel
log("🔊 加载 Whisper base 模型(离线)...")
t0 = time.time()
model = WhisperModel("base", device="cpu", compute_type="int8", local_files_only=True)
log(f"✅ 加载完成 ({time.time()-t0:.1f}秒)")

total = len(VIDEOS)
for i, (bvid, title_safe) in enumerate(VIDEOS):
    md_path = os.path.join(OUTPUT_DIR, f"{title_safe}.md")
    if os.path.exists(md_path):
        log(f"[{i+1}/{total}] ⏭ {title_safe} (已存在)")
        continue

    log(f"[{i+1}/{total}] 📥 {title_safe}")

    try:
        # 获取视频信息
        info = bili_get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
        cid = info['data']['cid']
        title = info['data']['title']
        dur = info['data']['duration']
        if isinstance(dur, str) and ':' in dur:
            dur_min = int(dur.split(':')[0])
        else:
            dur_min = int(dur) // 60
        log(f"  {title[:60]} ({dur_min}分钟)")

        # 检查字幕
        player = bili_get(f'https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}')
        subtitles = player.get('data', {}).get('subtitle', {}).get('subtitles', [])
        if subtitles:
            log(f"  ✅ 有字幕! 直接提取")
            # TODO: 实现字幕直接提取（当前版本走语音转写）
            # subtitle_url = subtitles[0].get('subtitle_url')
            # 字幕URL是相对路径，需要补全 https: 前缀

        # 获取音频流
        playurl = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16&fnver=0&fourk=1'
        player = bili_get(playurl)
        audios = player['data']['dash']['audio']
        audio_url = max(audios, key=lambda a: a.get('bandwidth', 0)).get('base_url', '')
        if audio_url.startswith('//'):
            audio_url = 'https:' + audio_url

        # 下载音频
        audio_path = f'/tmp/bili_{bvid}.m4a'
        cmd = ['ffmpeg', '-y', '-headers', f'User-Agent: {UA}\r\nReferer: https://www.bilibili.com/',
               '-i', audio_url, '-c', 'copy', audio_path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        size_mb = os.path.getsize(audio_path) / 1024 / 1024
        log(f"  ✅ 下载 ({size_mb:.0f}MB)")

        # 语音转写
        log(f"  🎤 转写 (约{dur_min//5}分钟)...")
        t1 = time.time()
        segs, _ = model.transcribe(audio_path, language='zh', beam_size=5,
                                    vad_filter=True,
                                    vad_parameters=dict(min_silence_duration_ms=500))
        results = [{'text': s.text.strip()} for s in segs if s.text.strip()]
        log(f"  ✅ 转写 ({time.time()-t1:.0f}秒, {len(results)}段)")

        # 保存MD
        md = f"# {title}\n\n> 来源: https://www.bilibili.com/video/{bvid}\n> 时长: {dur_min}分钟\n> 转写: faster-whisper (base)\n\n---\n\n"
        for seg in results:
            md += f"{seg['text']}\n\n"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)
        log(f"  💾 {md_path} ({len(md)}字)")

        os.remove(audio_path)
    except Exception as e:
        log(f"  ❌ 失败: {e}")

    time.sleep(2)

log(f"\n✅ 完成！{OUTPUT_DIR}")
