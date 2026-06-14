#!/usr/bin/env python3
"""通过 Ollama 本地视觉模型分析文玩图片（免费、离线、本地）"""
import sys, json, base64
from pathlib import Path
import urllib.request

OLLAMA_URL = "http://172.24.208.1:11434"
MODEL = "minicpm-v:8b"

def analyze_image(image_path, question=None):
    """用 Ollama 视觉模型分析图片"""
    if question is None:
        question = """请仔细分析这张文玩图片。从以下方面回答：
1. 这是什么品类（核桃/手串/玉石/其他）？
2. 图片是否有灯光滤镜处理痕迹（颜色是否自然、高光是否异常）？
3. 能否看到材质特征（纹理、气孔、光泽等）？
4. 给出一个红黄绿风险评级（🟢可信 🟡存疑 🔴高风险）。
请用中文简要回答，控制在200字以内。"""
    
    # 读取图片并转 base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": question,
            "images": [img_b64]
        }],
        "stream": False
    }
    
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    
    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read())
    return result["message"]["content"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python3 ollama_vision.py <图片路径> [问题]"}))
        sys.exit(1)
    
    path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        answer = analyze_image(path, question)
        print(json.dumps({"status": "ok", "answer": answer}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
