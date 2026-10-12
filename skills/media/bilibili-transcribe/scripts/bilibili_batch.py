#!/usr/bin/env python3
"""B站视频→文字 批量转写工具 (flush版, 不需要yt-dlp)
用法: 修改 VIDEOS 列表后 python3 -u bilibili_batch.py
"""
import urllib.request, json, gzip, subprocess, os, sys, time

OUTPUT_DIR = '/mnt/c/Users/admin/Desktop/学习/梓墨说语文'  # 修改输出目录
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# 视频列表: (bvid, 安全文件名)
VIDEOS = [
    ("BV1t5j16EE4P", "视频标题1"),
    ("BV1m7ji6sEQc", "视频标题2"),
]

def log(msg):
    print(msg, flush=True)

def bili_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = resp.read()
    if resp.headers.get('Content-Encoding') == 'gzip':
        data = gzip.decompress(data)
    return json.loads(data)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载模型（一次性）
from faster_whisper import WhisperModel
log(f"Loading Whisper base model (offline)...")
t0 = time.time()
model = WhisperModel("base", device="cpu", compute_type="int8", local_files_only=True)
log(f"Loaded in {time.time()-t0:.1f}s")

total = len(VIDEOS)
for i, (bvid, title_safe) in enumerate(VIDEOS):
    md_path = os.path.join(OUTPUT_DIR, f"{title_safe}.md")
    if os.path.exists(md_path):
        log(f"[{i+1}/{total}] SKIP {title_safe} (exists)")
        continue

    log(f"[{i+1}/{total}] DOWNLOAD {title_safe}")

    try:
        # API: 获取cid + 音频URL (不需要wbi签名)
        info = bili_get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
        cid = info['data']['cid']
        title = info['data']['title']
        playurl = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16&fnver=0&fourk=1'
        player = bili_get(playurl)
        audios = player['data']['dash']['audio']
        audio_url = max(audios, key=lambda a: a.get('bandwidth', 0)).get('base_url', '')
        if audio_url.startswith('//'):
            audio_url = 'https:' + audio_url
    except Exception as e:
        log(f"  FAIL API: {e}")
        continue

    # ffmpeg 下载
    audio_path = f'/tmp/bili_{bvid}.m4a'
    cmd = ['ffmpeg', '-y', '-headers', f'User-Agent: {UA}\r\nReferer: https://www.bilibili.com/',
           '-i', audio_url, '-c', 'copy', audio_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        log(f"  FAIL download")
        continue
    log(f"  OK download ({os.path.getsize(audio_path)/1024/1024:.1f}MB)")

    # 转写
    log(f"  TRANSCRIBE...")
    t1 = time.time()
    segs, _ = model.transcribe(audio_path, language='zh', beam_size=5, vad_filter=True,
                                vad_parameters=dict(min_silence_duration_ms=500))
    results = [{'start': s.start, 'end': s.end, 'text': s.text.strip()} for s in segs if s.text.strip()]
    log(f"  OK transcribe ({time.time()-t1:.0f}s, {len(results)} segments)")

    # 保存MD
    md = f"# {title}\n\n> 来源: https://www.bilibili.com/video/{bvid}\n> 转写工具: faster-whisper (base)\n\n---\n\n"
    for seg in results:
        md += f"{seg['text']}\n\n"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    log(f"  SAVED {md_path} ({len(md)} chars)")

    os.remove(audio_path)
    time.sleep(1)

log(f"\nDONE! {OUTPUT_DIR}")
