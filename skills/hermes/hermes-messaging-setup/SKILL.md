---
name: hermes-messaging-setup
description: Connect Hermes Agent to messaging platforms (WeChat, Telegram, Discord, etc.). Covers the general setup pattern, WeChat-specific configuration via iLink Bot API, and how to efficiently read Hermes docs (SPA site).
---

# Hermes Messaging Platform Setup

Connect Hermes to messaging platforms so users can interact with the agent from chat apps.

## Trigger Conditions

- User asks to connect/configure a messaging platform (WeChat, Telegram, Discord, DingTalk, WeCom, QQ, etc.)
- User says "连上微信", "连接 Telegram", "setup messaging", etc.

## General Setup Pattern

1. **Check prerequisites**: `pip list | grep -E "hermes|aiohttp|cryptography"` and `which hermes`
2. **Read docs**: Hermes docs at https://hermes-agent.nousresearch.com/docs are an SPA — curl returns 404. Navigate via browser, then extract with `browser_console(expression="document.querySelector('article').innerText")`.
3. **Run setup wizard**: `hermes gateway setup` — selects the platform, handles OAuth/QR login.
4. **Configure `.env`**: Set platform-specific env vars in `~/.hermes/.env`.
5. **Check gateway status**: Read `~/.hermes/gateway.pid`, check with `ps`.
6. **Restart gateway if needed**: `hermes gateway restart` or add the new platform in `config.yaml` under `platforms.<name>`.

## WeChat (Weixin) Specifics

Platform: Personal WeChat via iLink Bot API (not WeCom enterprise WeChat).

### Prerequisites
```bash
pip install aiohttp cryptography
# Optional: for terminal QR display
pip install hermes-agent[messaging]
```

### Setup
1. `hermes gateway setup` → select **Weixin**
2. Scan the terminal-displayed QR code with WeChat mobile app
3. Confirm login on phone
4. Wizard saves credentials to `~/.hermes/weixin/accounts/`

### Environment Variables (~/.hermes/.env)
```
WEIXIN_ACCOUNT_ID=<account_id from wizard>
WEIXIN_DM_POLICY=open
# Optional: restrict to specific users
# WEIXIN_DM_POLICY=allowlist
# WEIXIN_ALLOWED_USERS=user_id_1,user_id_2
```

### Key Limitations
- QR login creates an **iLink bot identity** (e.g., `xxx@im.bot`), NOT a scriptable personal account.
- iLink bots generally **cannot be invited into ordinary WeChat groups** — DMs are the primary working channel.
- Group policy defaults to **disabled** (unlike WeCom which defaults to open).
- The bot identity is separate from the personal account that scanned the QR code.

### Troubleshooting
| Problem | Fix |
|---------|-----|
| `aiohttp and cryptography are required` | `pip install aiohttp cryptography` |
| `WEIXIN_TOKEN is required` | Run `hermes gateway setup` to complete QR login |
| `errcode=-14` (session expired) | Re-run `hermes gateway setup` to scan new QR |
| Bot doesn't respond to DMs | Check `WEIXIN_DM_POLICY` — if `allowlist`, sender must be in `WEIXIN_ALLOWED_USERS` |
| `Another local Hermes gateway is already using this token` | Stop the other gateway instance first |

## Post-Setup: Add Platform to Config, Enable Gateway Access, Restart

After credentials are saved, three steps are needed before messaging works:

```bash
# 1. Add platform entry to config.yaml (use hermes config, not file tools)
hermes config set platforms.weixin '{"streaming": false}'

# 2. CRITICAL: Allow users through the gateway-level guard.
# Even when the platform's DM_POLICY is 'open', the gateway has its own
# allowlist check. Without this, all messages are denied with:
#   "No user allowlists configured. All unauthorized users will be denied."
echo 'GATEWAY_ALLOW_ALL_USERS=true' >> ~/.hermes/.env

# 3. Restart gateway to pick up both changes
hermes gateway restart

# Verify
hermes gateway status
cat ~/.hermes/logs/gateway.log | grep -E "weixin|Connected|platform|Channel directory"
```

A successful restart should show `Channel directory built: N target(s)` (N >= 1). If it shows `0 target(s)`, `GATEWAY_ALLOW_ALL_USERS` is likely missing.

Do NOT edit `~/.hermes/config.yaml` directly — the agent's file tools are blocked from modifying it. Always use `hermes config set <key> '<json_value>'`. If the key is nested (e.g., `platforms.weixin`), the tool creates the intermediate path.

## Reference Files

- `references/wechat-docs.md` — Full extracted WeChat (Weixin) documentation from hermes-agent.nousresearch.com, including all env vars, config options, CDN encryption details, and troubleshooting table.
- `references/network-proxy-workarounds.md` — Network proxy configuration and workarounds for this environment: pip Tsinghua mirror, git proxy, aiohttp Python 3.14 compatibility fix, browser-as-fallback for curl failures.
- `scripts/wechat_qr_login.py` — Standalone script to bypass the TUI wizard: fetches QR from iLink API, generates PNG to desktop, polls for scan, saves credentials and updates .env.
- `scripts/batch_migrate.py` — Batch migrate skills from multiple agent directories (.local/skills, .agents/skills, superpowers, codex) into ~/.hermes/skills/. Handles category detection, name prefixing, and supporting file copy.

## TUI Workaround: Direct Script Approach

The `hermes gateway setup` wizard uses a Textual TUI with a select widget. Attempting to drive it via PTY has two failure modes:

1. **Number input doesn't work**: Typing a number (e.g., `12` for Weixin) and pressing Enter is silently ignored — the widget only responds to arrow-key navigation + Enter/Space.
2. **Arrow-key escape sequences unreliable**: Sending `\x1b[A` (UP) via `process write` may not be processed correctly, causing the selection to land on the wrong item (e.g., WeCom Callback instead of Weixin because of an off-by-one in the arrow count).

**When either failure occurs**, do NOT retry the TUI — bypass the wizard entirely by writing a script that calls the platform's API directly. The general pattern:

1. Read the adapter source at `/usr/local/lib/python3.14/dist-packages/gateway/platforms/<platform>.py` to understand the API flow (endpoints, headers, credential format).
2. Write a standalone Python script replicating the minimal setup flow (QR fetch, poll, credential save, .env update). Set `sys.path` to include the dist-packages path for shared utilities.
3. Run it in background with `notify_on_complete=true` so the user gets notified when QR is scanned.
4. If the script fails with import errors (e.g., old aiohttp), diagnose dependency conflicts before modifying the script — see the aiohttp pitfall below.

For WeChat, see `scripts/wechat_qr_login.py` — a drop-in script that:
- Fetches QR from iLink Bot API with correct headers
- Generates a QR PNG to Windows Desktop (WSL-aware path detection)
- Polls for scan/confirm status
- Saves credentials and updates `~/.hermes/.env` (including `WEIXIN_ACCOUNT_ID`, `WEIXIN_DM_POLICY=open`, and `GATEWAY_ALLOW_ALL_USERS=true`)

This pattern applies to any platform whose setup wizard has TUI issues (WeCom, DingTalk, Feishu, QQ Bot all have similar QR-based flows).

## QR to Desktop (WSL)

When running in WSL and the user wants a QR image on their Windows desktop:
- Find Windows username: `ls /mnt/c/Users/` (skip system accounts: All Users, Default, Default User, Public)
- Desktop path: `/mnt/c/Users/<username>/Desktop/`
- Generate QR via the `qrcode` library: `qrcode.QRCode()` + `img.save(path)`

## Pitfalls

- **Docs are SPA**: The docs site at hermes-agent.nousresearch.com uses client-side rendering. `curl` returns a 404 GitHub Pages page. Always use browser tools to navigate, then extract content with `browser_console(expression="document.querySelector('article').innerText")`.
- **Only one gateway per token**: Weixin enforces a token lock — only one gateway instance can use a given token at a time.
- **Gateway-level allowlist blocks all users**: Even with per-platform `DM_POLICY=open`, the gateway enforces its own allowlist check. If the log shows "No user allowlists configured. All unauthorized users will be denied.", add `GATEWAY_ALLOW_ALL_USERS=true` to `~/.hermes/.env` and restart. Verify by checking `Channel directory built: N target(s)` — N=0 means the guard is still active.
- **Group messages unlikely to work**: The iLink bot identity limitation means group chat typically won't work. Set expectations with the user upfront.
- **aiohttp 3.7.x breaks on Python 3.14+**: Python 3.14 removed the `cgi` module. User-local aiohttp <=3.7.x fails with `ModuleNotFoundError: No module named 'cgi'`. Fix: `rm -rf ~/.local/lib/python3.14/site-packages/aiohttp*` so Python uses the system aiohttp (3.13+ at `/usr/lib/python3/dist-packages`).
- **iLink API requires specific headers**: The WeChat iLink Bot API rejects requests without `iLink-App-Id: bot` and `iLink-App-ClientVersion: <encoded_version>` headers. The adapter reads responses as text first, then parses JSON — standard aiohttp `response.json()` may fail on `application/octet-stream` content types.
- **Cannot edit config.yaml directly**: The agent's file tools (write_file, patch) are blocked from modifying `~/.hermes/config.yaml`. Use `hermes config set <key> '<json_value>'` instead. For nested keys like `platforms.weixin`, the tool auto-creates the path.
