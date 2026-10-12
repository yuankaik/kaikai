# WeChat Image Fix: Enable Vision via Local Ollama

## Problem
DeepSeek API doesn't support `vision`/multimodal. When users send images via WeChat, the gateway agent fails with:
```
RuntimeError: No LLM provider configured for task=vision provider=auto. Run: hermes setup
```

Users see English error messages they can't understand ("The user sent an image but I couldn't quite see it this time (>_<)").

## Solution
Point Hermes vision to a local Ollama vision model. No API key needed, fully offline.

### Prerequisites
- Ollama installed on Windows (at `C:\Users\admin\AppData\Local\Programs\Ollama\ollama.exe`)
- A vision model pulled: `minicpm-v:8b` (Chinese-friendly, free)
- Ollama running with `OLLAMA_HOST=http://0.0.0.0:11434` (default)

### Start Ollama from WSL
```bash
cmd.exe /c "start /B C:\Users\admin\AppData\Local\Programs\Ollama\ollama.exe serve"
```

### Get Windows IP from WSL
```bash
ip route show default | awk '{print $3}'
# Example: 172.24.208.1
```

### Pull a Vision Model
```bash
curl -s http://172.24.208.1:11434/api/pull -d '{"name":"minicpm-v:8b","stream":false}'
```

### Configure Hermes Vision Provider
```bash
# Hermes reads vision config from auxiliary.vision (not top-level vision)
# CRITICAL (2026-06-17 verified): base_url MUST end with /v1 for Ollama.
# Without /v1: hermes vision_analyze returns "404 page not found".
# With /v1: works correctly. The OpenAI client in Hermes does NOT auto-append /v1.
hermes config set auxiliary.vision.provider openai
hermes config set auxiliary.vision.model minicpm-v:8b
hermes config set auxiliary.vision.base_url "http://172.24.208.1:11434/v1"
hermes config set auxiliary.vision.api_key ollama
```

### Restart Gateway
```bash
hermes gateway restart
```

## ⚠️ Critical Pitfalls

### 1. Ollama MUST be running BEFORE gateway restart
If Ollama is not running when the gateway receives an image, `vision_analyze` may get a 400 error that LOOKS like model incompatibility but is actually just Ollama being unreachable or in a bad state. The gateway log shows:

```
ERROR tools.vision_tools: Error analyzing image: Error code: 400 - 
{'error': {'message': 'Failed to deserialize the JSON body into the target type: 
messages[0]: unknown variant `image_url`, expected `text'...
```

**Fix**: Always start Ollama first, verify it's reachable, THEN restart gateway:
```bash
# 1. Start Ollama
cmd.exe /c "start /B C:\Users\admin\AppData\Local\Programs\Ollama\ollama.exe serve"
sleep 3
# 2. Verify
curl -s http://172.24.208.1:11434/api/tags | python3 -c "import sys,json; print(json.load(sys.stdin))"
# 3. Then restart gateway
hermes gateway restart
```

### 2. Ollama `/v1` endpoint (verified 2026-06-17)
Ollama 0.30.8+ with `minicpm-v:8b`: base_url **MUST** end with `/v1` for hermes vision_analyze to work. Without `/v1`, vision returns "404 page not found". The `/v1` path IS required — hermes's OpenAI client does not auto-append it.

CPU performance: ~30-90s for small images, may timeout (>120s) for large screenshots. DevTools cookie screenshots have very small text that minicpm-v:8b struggles to OCR accurately. For cookie value extraction, copy-paste from browser is more reliable than OCR.

## Alternative Vision Models
| Model | Size | Notes |
|-------|------|-------|
| `minicpm-v:8b` | ~5GB | Chinese-friendly, good for this use case |
| `llava:13b` | ~8GB | Better visual understanding |
| `llama3.2-vision:11b` | ~8GB | Meta's vision model |

## Speed Note
Vision models on Windows CPU are **slow** (84+ seconds per image). For production use, recommend a GPU or a cloud vision API.
