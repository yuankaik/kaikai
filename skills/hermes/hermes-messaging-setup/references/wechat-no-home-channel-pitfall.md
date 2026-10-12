# "No home channel set" — The Rate-Limit Masking Pitfall

## Symptom

`send_message` returns:
```
No home channel set for weixin to determine where to send the message.
Either specify a channel directly with 'weixin:CHANNEL_NAME',
or set a home channel via: hermes config set WEIXIN_HOME_CHANNEL <channel_id>
```

## The Trap

This error message is **misleading**. You check `WEIXIN_HOME_CHANNEL` — it's set. You check `platforms.weixin` — it's configured. You restart the gateway — same error. You keep changing the config — nothing works.

## Root Cause

iLink server rate limiting (`errcode=-2`, 15-minute cooldown) blocking the gateway's startup notification. Flow:

1. Gateway starts → connects to weixin platform → builds channel directory (1 target ✓)
2. Gateway tries to send "home-channel startup notification" → **iLink returns `errcode=-2: rate limited`**
3. Home channel registration is incomplete (notification never delivered)
4. `send_message` checks home channel → finds it unregistered → reports "No home channel set"

The WEIXIN_HOME_CHANNEL config is **correct** — the problem is entirely iLink's rate limiting.

## Diagnostic Commands

```bash
# 1. Verify config exists (not the problem — just confirm)
hermes config show | grep -i home_channel
grep HOME_CHANNEL ~/.hermes/config.yaml

# 2. Check gateway log for the real cause
grep -E "rate limit|Home-channel" ~/.hermes/logs/gateway.log | tail -10

# 3. If you see this, it's rate limiting:
#    ERROR: [Weixin] send failed to=o9cq80-5: iLink sendmessage rate limited: errcode=-2
#    WARNING: Home-channel startup notification failed: rate limited

# 4. Find when the cooldown started
grep "rate limit" ~/.hermes/logs/gateway.log | tail -3 | head -1
# Example output: 2026-06-22 12:36:06 ...
# → cooldown expires ~15 min later: 12:51:06
```

## Fix

1. **Wait** for the 15-minute iLink cooldown to expire (from the last `rate limited` timestamp in logs)
2. **Restart** the gateway: `hermes gateway restart`
3. This time, the startup notification will succeed → home channel registers → `send_message` works

**Pro tip:** Use a one-shot cron job to auto-restart after the window:
```
cronjob create schedule="YYYY-MM-DDTHH:MM:SS" (15 min after last rate limit + 1 min buffer)
prompt: "Restart hermes gateway and send test message to weixin"
```

## What NOT to Do

- ❌ Keep changing `WEIXIN_HOME_CHANNEL` — it's already correct
- ❌ Run `hermes gateway setup` again — not a credential issue
- ❌ Change `GATEWAY_ALLOW_ALL_USERS` — not an allowlist issue
- ❌ Blame `send_message` tool — it's reporting what the gateway tells it
- ❌ Keep restarting the gateway before cooldown expires — each restart triggers a startup notification that also gets rate-limited, resetting the cooldown clock

## Verification After Fix

```bash
# Gateway log should show startup notification success (no "rate limited" errors)
grep -E "Home-channel|startup" ~/.hermes/logs/gateway.log | tail -5

# send_message should work
# Expected: message delivered to WeChat, no "No home channel" error
```
