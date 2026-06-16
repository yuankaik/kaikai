# WeChat iLink Bot Rate Limiting

## Symptom

User sends multiple questions through WeChat in quick succession → Hermes stops responding for ~15 minutes. No errors visible in user's WeChat; bot simply goes silent. Gateway logs may show `rate limited` warnings if verbose logging is on, but the primary symptom is a total message blackout for 10-20 minutes.

## Root Cause

iLink Bot (WeChat AI Platform) enforces **server-side frequency limits** on bot message delivery. When the gateway sends too many message chunks in a short window, the iLink API returns `errcode=-2` (defined as `RATE_LIMIT_ERRCODE` in the adapter). The server then imposes a cooldown — typically around 15 minutes — during which ALL messages from the bot are rejected.

This is NOT a Hermes bug or config issue. The rate limit is enforced on the WeChat/iLink server side and cannot be bypassed from the client.

## Adapter Internals

From the weixin adapter source (`gateway/platforms/weixin.py`):

```
RATE_LIMIT_ERRCODE = -2       # iLink frequency limit
MAX_CONSECUTIVE_FAILURES = 3   # consecutive failures before longer backoff
RETRY_DELAY_SECONDS = 2        # normal retry delay
BACKOFF_DELAY_SECONDS = 30     # backoff after consecutive failures >= threshold

_send_chunk_delay_seconds = 1.0         # WEIXIN_SEND_CHUNK_DELAY_SECONDS
_send_chunk_retries = 3                 # WEIXIN_SEND_CHUNK_RETRIES
_send_chunk_retry_delay_seconds = 1.0   # WEIXIN_SEND_CHUNK_RETRY_DELAY_SECONDS
```

When a rate limit (`errcode=-2`) is hit during chunk delivery:
- Wait `_send_chunk_retry_delay_seconds * 3` (3x backoff, ~3 seconds default)
- Retry up to `_send_chunk_retries` times
- If all retries exhausted with server still rate-limiting, the message is dropped

For poll failures (connection errors during message receive):
- After `MAX_CONSECUTIVE_FAILURES` (3) consecutive poll failures, use `BACKOFF_DELAY_SECONDS` (30s) backoff
- Before threshold, use `RETRY_DELAY_SECONDS` (2s) backoff

## Fix: Increase Message Chunk Intervals

Add to `~/.hermes/.env`:

```bash
# Delay between each message chunk sent (default: 1.0 second)
# Increasing this reduces throughput and avoids hitting the rate limit
WEIXIN_SEND_CHUNK_DELAY_SECONDS=2.5

# Retry delay when a chunk send fails (default: 1.0 second)
# Multiplied by 3 for rate-limit-specific backoff
WEIXIN_SEND_CHUNK_RETRY_DELAY_SECONDS=2.0
```

Then restart the gateway:

```bash
hermes gateway restart
```

## Additional Mitigations

1. **Control question frequency**: Wait for Hermes to finish replying before sending the next question. Long replies are split into multiple chunks — firing another question while chunks are still being delivered compounds the rate-limit risk.

2. **Keep replies concise**: Shorter replies = fewer chunks = lower risk. Agent system prompt can be adjusted, or `display.compact: true` in config.yaml.

3. **Note that the deepseek-v4-pro model itself has a 500 concurrency limit (account-level) — NOT the bottleneck here.** DeepSeek's rate limit is per-request concurrency, not per-message frequency, and is unlikely to be hit by a single WeChat user.

## Investigation Commands

```bash
# Check gateway rate limit logs
grep -i "rate.limit\|backoff\|errcode=-2" ~/.hermes/logs/gateway.log | tail -20

# Check current chunk delay config (defaults shown if not set)
grep "WEIXIN_SEND_CHUNK" ~/.hermes/.env

# Inspect adapter source for current defaults
grep -n "RATE_LIMIT\|BACKOFF\|send_chunk" /usr/local/lib/python3.*/dist-packages/gateway/platforms/weixin.py

# Verify env vars are picked up (restart first)
hermes gateway restart
sleep 5
grep "send_chunk" ~/.hermes/logs/gateway.log
```
