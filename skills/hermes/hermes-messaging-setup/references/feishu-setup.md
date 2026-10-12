# Feishu / Lark Setup — Full Reference (verified 2026-10)

Extracted from the Hermes docs SPA (`/docs/user-guide/messaging/feishu`) plus a live
end-to-end onboarding on WSL. Everything here was actually executed, not just read.

## Two independent capabilities, one credential

| Line | Capability | Needs |
|------|-----------|-------|
| ① Chat | DM the bot; group requires @mention | `FEISHU_*` env + running gateway |
| ② Docs/Drive | Read Feishu docs; auto-reply to doc comments that @mention the bot | `feishu_doc` + `feishu_drive` toolsets + extra scopes + `drive.notice.comment_add_v1` event |

A user asking "can you connect to Feishu?" may want either or both — confirm before
starting, because line ② needs a developer-console visit that line ① does not.

## Connection modes

| Mode | Public URL needed? | Env | Notes |
|------|-------------------|-----|-------|
| `websocket` (default, recommended) | **No** | `FEISHU_CONNECTION_MODE=websocket` | Outbound wss to `msg-frontier.feishu.cn`. Ideal for laptop/WSL/private host. |
| `webhook` | Yes, HTTPS | `FEISHU_CONNECTION_MODE=webhook` | Hermes serves `aiohttp` on `/feishu/webhook` (default 127.0.0.1:8765). Set `FEISHU_ENCRYPT_KEY` + `FEISHU_VERIFICATION_TOKEN` for signature verification. |

The earlier assumption that Feishu always needs a public callback is WRONG for
websocket mode. Do not tell the user they need a domain/HTTPS unless they explicitly
want webhook mode.

## Scan-to-create (device-code) flow

Feishu onboarding is a **device-code** flow, not a callback. Confirmed live:

1. `POST {accounts}/.../begin` → returns `device_code`, `verification_uri_complete`
   (the `qr_url`), `user_code`, `interval`, `expire_in` (600s).
2. User scans `qr_url` with the Feishu mobile app (or opens it on the phone).
3. `_poll_registration()` polls until scanned → returns
   `{app_id, app_secret, domain, open_id}`.
4. `probe_bot()` optionally verifies via `tenant_access_token` → `GET /open-apis/bot/v3/info`.

The app is created **with the correct chat permissions automatically** — no manual
developer-console app creation needed for line ①.

Implementation lives in `plugins/platforms/feishu/adapter.py` (Feishu was moved into a
bundled plugin; `hermes_cli/gateway.py` has the marker comments).

### Exact observed artifacts

```
user_code : UMNQ-G8J2
URL       : https://open.feishu.cn/page/launcher?user_code=UMNQ-G8J2&from=hermes&tp=hermes
result    : {app_id: "cli_aa46edd75679dbe2", app_secret: "...", domain: "feishu",
             open_id: "ou_46304000380c00b4be74e3fb5eedd13f"}
bot probe : {app_name: "用户283408的智能助手", activate_status: 2, open_id: "ou_ef1d5e299f941e32e498236307d6a846"}
```
Note the bot's `open_id` differs from the scanning user's `open_id` — the user's goes in
`FEISHU_ALLOWED_USERS`.

### Verified gateway log line
```
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?fpid=493&aid=552564&... [conn_id=...]
```
Grep it with: `journalctl --user -u hermes-gateway --since "1 minute ago" | grep -i lark`

## Environment variables (full)

| Var | Purpose |
|-----|---------|
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | Bot credentials |
| `FEISHU_DOMAIN` | `feishu` (China) or `lark` (international) |
| `FEISHU_CONNECTION_MODE` | `websocket` (default) or `webhook` |
| `FEISHU_ALLOWED_USERS` | Comma-separated open_ids. **Set it** — default group policy rejects unknowns. |
| `FEISHU_HOME_CHANNEL` | `oc_xxx` chat for cron results (or use `/set-home` in-chat) |
| `FEISHU_GROUP_POLICY` | `allowlist` (default) / `open` / `disabled` |
| `FEISHU_REQUIRE_MENTION` | `false` to read all group traffic |
| `FEISHU_ALLOW_BOTS` | `none` (default) / `mentions` / `all` — peer-bot messages |
| `FEISHU_BOT_OPEN_ID` / `FEISHU_BOT_NAME` | Only if auto-detection fails |
| `FEISHU_ENCRYPT_KEY` / `FEISHU_VERIFICATION_TOKEN` | Webhook-mode signature checks |
| `FEISHU_WEBHOOK_HOST/PORT/PATH` | Webhook server bind (default 127.0.0.1:8765/feishu/webhook) |

## Line ② permissions (NOT auto-granted)

Beyond chat scopes, add in the developer console → 权限管理:
- `docs:doc:readonly` — read document content
- `drive:drive:readonly` — read drive metadata/content

And in 事件订阅 → subscribe `drive.notice.comment_add_v1`.

Doc-comment replies are **explicit-grant only** (no implicit allow-all). Rules live in
`~/.hermes/feishu_comment_rules.json` (pairing grants in
`~/.hermes/feishu_comment_pairing.json`), hot-reloaded on mtime. CLI:
```
python -m gateway.platforms.feishu_comment_rules status
python -m gateway.platforms.feishu_comment_rules check <fileType:fileToken> <user_open_id>
python -m gateway.platforms.feishu_comment_rules pairing add <user_open_id>
```

## Media support (chat line)

Inbound: images `.jpg/.png/.gif/.webp/.bmp`, audio `.ogg/.mp3/.wav/.m4a/.opus`, video
`.mp4/.mov/.mkv`, files `.pdf/.docx/.xlsx/.pptx` — all downloaded & cached. Small text
files (.txt/.md) are auto-appended to the message so the agent reads them without tools.

## Pitfalls (all hit in practice)

1. **Poll must outlive execute_code's 300s cap.** Device code lives 600s. Run the poll in
   `terminal(timeout=600)` or background; keep the fast QR step in execute_code.
2. **Terminal ASCII QR is painful to scan.** Render a PNG to the Windows desktop AND
   print the raw URL.
3. **`lark-oapi` is required** for websocket mode and for `probe_bot` SDK path. It's not a
   default dep — `pip install lark-oapi`. Without it, websocket mode can't start.
4. **`pkg_resources` deprecation warning** from `lark_oapi` is harmless noise, not an error.
5. **`Installed gateway service definition is outdated`** after first restart — run
   `hermes gateway restart` once more; it rewrites the systemd unit.
6. **Config not in `.env` won't be seen** by the systemd gateway unless the drop-in
   `EnvironmentFile` exists — same as WeChat (see SKILL.md Post-Setup section).
7. **Scan-to-create does NOT grant doc/drive scopes.** Line ② always needs a console visit.
