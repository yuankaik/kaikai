# WeChat (Weixin) — Full Doc Extract

Source: https://hermes-agent.nousresearch.com/docs (SPA, extracted 2026-06-14)

## Overview

Connect Hermes to WeChat (微信), Tencent's personal messaging platform. Uses Tencent's iLink Bot API — distinct from WeCom (Enterprise WeChat). Messages via long-polling, no public endpoint/webhook required.

## iLink Bot Identity Warning

QR login connects Hermes to an iLink bot identity (e.g. `a5ace6fd482e@im.bot`), NOT a fully scriptable ordinary personal WeChat account.

- iLink bot identity generally cannot be invited into ordinary WeChat groups
- iLink typically does not deliver ordinary WeChat group events (@-mentions of the personal QR-login account)
- @-mentioning the personal account != @-mentioning the iLink bot (separate identities)
- Group policy settings only take effect when iLink actually returns group events

Most deployments only get DMs working reliably.

## Setup Steps

1. `pip install aiohttp cryptography` (+ optionally `hermes-agent[messaging]` for QR display)
2. `hermes gateway setup` → select Weixin → scan QR → confirm on phone
3. Set `WEIXIN_ACCOUNT_ID=<id>` in `~/.hermes/.env`
4. Start/restart gateway: `hermes gateway`

## Configuration Options (config.yaml under platforms.weixin.extra)

| Key | Default | Description |
|-----|---------|-------------|
| account_id | — | iLink Bot account ID (required) |
| token | — | iLink Bot token (auto-saved from QR login) |
| base_url | https://ilinkai.weixin.qq.com | iLink API base URL |
| cdn_base_url | https://novac2c.cdn.weixin.qq.com/c2c | CDN base URL |
| dm_policy | open | DM access: open, allowlist, disabled, pairing |
| group_policy | disabled | Group access: open, allowlist, disabled |
| allow_from | [] | User IDs for DM allowlist |
| group_allow_from | [] | Group IDs for group allowlist |
| split_multiline_messages | false | Legacy multiline splitting |
| text_batch_delay_seconds | 3.0 | Debounce for batched text flush |
| text_batch_split_delay_seconds | 5.0 | Extended flush delay near split threshold |

## DM Policy Values

- **open**: Anyone can DM (default)
- **allowlist**: Only user IDs in `allow_from` / `WEIXIN_ALLOWED_USERS`
- **disabled**: All DMs ignored
- **pairing**: Initial setup mode

## Group Policy Values

- **open**: Respond in all groups (IF events delivered)
- **allowlist**: Only groups in `group_allow_from`
- **disabled**: All group messages ignored (default)

NOTE: `WEIXIN_GROUP_ALLOWED_USERS` expects GROUP CHAT IDs, not member user IDs (legacy naming).

## Features

- Long-poll transport (no public endpoint/webhook)
- QR code login via `hermes gateway setup`
- DM messaging with configurable access policies
- Media support: images, video, files, voice
- AES-128-ECB encrypted CDN (auto encrypt/decrypt)
- Context token persistence (disk-backed across restarts)
- Markdown formatting preserved (headers, tables, code blocks)
- Smart message chunking (single bubble under 4000 chars)
- Typing indicators
- SSRF protection on outbound media URLs
- Message deduplication (5-min sliding window)
- Automatic retry with backoff
- Token lock (only one gateway per token)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| WEIXIN_ACCOUNT_ID | ✅ | — | iLink Bot account ID |
| WEIXIN_TOKEN | ✅ | — | iLink Bot token |
| WEIXIN_BASE_URL | — | https://ilinkai.weixin.qq.com | API base URL |
| WEIXIN_CDN_BASE_URL | — | https://novac2c.cdn.weixin.qq.com/c2c | CDN base URL |
| WEIXIN_DM_POLICY | — | open | DM access policy |
| WEIXIN_GROUP_POLICY | — | disabled | Group access policy |
| WEIXIN_ALLOWED_USERS | — | (empty) | Comma-separated user IDs for DM allowlist |
| WEIXIN_GROUP_ALLOWED_USERS | — | (empty) | Comma-separated group chat IDs for group allowlist |
| WEIXIN_HOME_CHANNEL | — | — | Chat ID for cron/notification output |
| WEIXIN_HOME_CHANNEL_NAME | — | Home | Display name for home channel |
| WEIXIN_ALLOW_ALL_USERS | — | — | Gateway-level flag (setup wizard) |

## Access Control Flow

1. `WEIXIN_ALLOWED_USERS` is an INBOUND filter, not an invitation system
2. QR login connects ONE iLink bot identity
3. Other users must message the connected iLink bot/contact
4. Hermes processes DM only if sender's Weixin user ID is in `WEIXIN_ALLOWED_USERS`

Practical flow:
1. Pair Hermes once with `hermes gateway setup`
2. Have each allowed user send a DM to the bot/contact
3. Read sender/user ID from gateway logs
4. Add IDs to `WEIXIN_ALLOWED_USERS`, restart gateway

## CDN Encryption Details

- Inbound: Download encrypted media from CDN, decrypt with AES-128-ECB using per-file key
- Outbound: Encrypt locally with random AES-128-ECB key, upload to CDN
- AES key: 16 bytes (128-bit), base64 or hex-encoded
- Requires `cryptography` Python package

## Context Token

- Disk-backed store: `~/.hermes/weixin/accounts/<account_id>.context-tokens.json`
- Restored on startup, updated per inbound message
- Ensures reply continuity across gateway restarts

## Long-Poll Details

- Connect → validate credentials → start poll loop
- `getupdates` with 35s timeout
- Messages dispatched concurrently via `asyncio.create_task`
- Persistent sync cursor saved to disk

## Retry Behavior

| Condition | Behavior |
|-----------|----------|
| Transient error (1st-2nd) | Retry after 2s |
| Repeated errors (3+) | Back off 30s, reset counter |
| Session expired (errcode=-14) | Pause 10 min (re-login needed) |
| Timeout | Immediately re-poll |

## Troubleshooting Quick Reference

| Problem | Fix |
|---------|-----|
| aiohttp/cryptography required | `pip install aiohttp cryptography` |
| WEIXIN_TOKEN required | Run `hermes gateway setup` |
| WEIXIN_ACCOUNT_ID required | Set in .env or run setup wizard |
| Another gateway using same token | Stop other gateway first |
| Session expired (errcode=-14) | Re-run `hermes gateway setup` |
| QR expired during setup | Auto-refreshes up to 3 times |
| Bot doesn't respond to DMs | Check allowlist / dm_policy |
| Bot ignores group messages | Groups default disabled; iLink limitation |
| Media download/upload fails | Install cryptography; check CDN access |
| Blocked unsafe URL (SSRF) | Outbound URL must be public |
| Voice messages show as text | If WeChat provides transcription |
| Messages duplicated | Check for multiple gateway instances |
| Terminal QR doesn't render | `pip install hermes-agent[messaging]` |
