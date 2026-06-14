#!/usr/bin/env python3
"""文玩图片仙图检测 —— 检查灯光/滤镜/色彩异常"""
import sys
import json
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print(json.dumps({"error": "需要 pip install Pillow numpy"}))
    sys.exit(1)

def analyze_image(path):
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    result = {"file": str(path), "size": f"{w}x{h}"}
    warnings = []
    
    # 1. 红色通道检测（暖光/滤镜）
    r_mean = float(arr[:,:,0].mean())
    g_mean = float(arr[:,:,1].mean())
    b_mean = float(arr[:,:,2].mean())
    result["rgb_means"] = {"R": round(r_mean,1), "G": round(g_mean,1), "B": round(b_mean,1)}
    
    if r_mean > 170 and r_mean - b_mean > 30:
        warnings.append("🔴 红色通道偏高，疑似暖光或滤镜")
    elif r_mean > 150:
        warnings.append("🟡 色调偏暖，建议自然光拍摄")
    
    # 2. 饱和度检测
    max_val = arr.max(axis=2)
    min_val = arr.min(axis=2)
    sat = (max_val - min_val) / (max_val + 1)
    sat_mean = float(sat.mean())
    result["saturation_mean"] = round(sat_mean, 3)
    
    if sat_mean > 0.55:
        warnings.append("🔴 饱和度异常高，疑似滤镜处理")
    elif sat_mean > 0.4:
        warnings.append("🟡 饱和度偏高")
    
    # 3. 高光检测
    bright_mask = arr.mean(axis=2) > 220
    bright_ratio = float(bright_mask.mean())
    result["overexposure_ratio"] = round(bright_ratio, 3)
    
    if bright_ratio > 0.2:
        warnings.append("🔴 过度曝光区域过多（{}%），掩盖细节".format(round(bright_ratio*100)))
    elif bright_ratio > 0.1:
        warnings.append("🟡 高光区域偏多")
    
    # 4. 暗部细节
    dark_mask = arr.mean(axis=2) < 30
    dark_ratio = float(dark_mask.mean())
    result["underexposure_ratio"] = round(dark_ratio, 3)
    
    if dark_ratio > 0.3:
        warnings.append("🟡 暗部细节丢失，疑似压暗背景")
    
    # 综合评级
    if any("🔴" in w for w in warnings):
        result["risk"] = "🔴 高风险：图片经过明显处理"
    elif warnings:
        result["risk"] = "🟡 中风险：建议自然光复拍"
    else:
        result["risk"] = "🟢 低风险：图片色彩自然"
    
    result["warnings"] = warnings
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 image_check.py <图片路径>")
        sys.exit(1)
    result = analyze_image(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
