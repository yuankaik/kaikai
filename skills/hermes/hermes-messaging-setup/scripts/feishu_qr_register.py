#!/usr/bin/env python3
"""Feishu / Lark scan-to-create QR onboarding for Hermes.

Bypasses the `hermes gateway setup` TUI: drives the device-code QR flow directly,
renders the QR to a PNG on the Windows desktop (WSL-aware) plus terminal ASCII,
polls for the scan, then writes credentials to ~/.hermes/.env.

Verified 2026-10 against Hermes on WSL (plugins/platforms/feishu/adapter.py).

USAGE
    # Step 1 (fast, ~15s): generate QR, save PNG, print URL. Then show the user.
    python3 feishu_qr_register.py begin
    # Step 2 (long, up to 600s): poll until scanned. Run with a >=600s timeout,
    # or in the background with notify_on_complete.
    python3 feishu_qr_register.py poll

Why two steps: execute_code has a 300s cap and a foreground terminal call can time out
mid-poll. Splitting keeps the fast QR step cheap and lets the slow poll run long.
"""
import sys, os, json, time

DIST = "/usr/local/lib/python3.14/dist-packages"
if DIST not in sys.path:
    sys.path.insert(0, DIST)

from plugins.platforms.feishu import adapter as fad  # noqa: E402

BEGIN_CACHE = "/tmp/feishu_begin.json"
RESULT_CACHE = "/tmp/feishu_result.json"
DOMAIN = os.environ.get("FEISHU_DOMAIN", "feishu")  # feishu | lark


def _desktop_dir() -> str:
    """Best-effort Windows desktop path under WSL."""
    for user in os.listdir("/mnt/c/Users") if os.path.isdir("/mnt/c/Users") else []:
        if user.lower() in ("all users", "default", "default user", "public"):
            continue
        d = f"/mnt/c/Users/{user}/Desktop"
        if os.path.isdir(d):
            return d
    return os.path.expanduser("~")


def cmd_begin():
    fad._init_registration(DOMAIN)
    begin = fad._begin_registration(DOMAIN)
    with open(BEGIN_CACHE, "w") as f:
        json.dump(begin, f)

    url = begin["qr_url"]
    print(f"user_code : {begin['user_code']}")
    print(f"expires in: {begin['expire_in']}s   interval: {begin['interval']}s")
    print(f"URL       : {url}")

    try:
        import qrcode
        out = os.path.join(_desktop_dir(), "feishu-scan-me.png")
        qrcode.make(url).save(out)
        print(f"QR image  : {out}")
        # ASCII fallback for the terminal
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception as e:  # noqa: BLE001
        print(f"(QR render failed, use the URL above: {e})")
    print("\n>>> Scan with the Feishu mobile app, or open the URL on your phone.")


def cmd_poll():
    if not os.path.exists(BEGIN_CACHE):
        sys.exit("No begin cache — run `begin` first.")
    begin = json.load(open(BEGIN_CACHE))
    res = fad._poll_registration(
        device_code=begin["device_code"],
        interval=begin["interval"],
        expire_in=begin["expire_in"],
        domain=DOMAIN,
    )
    if not res:
        sys.exit("FAILED / TIMEOUT — no scan received before the device code expired.")

    with open(RESULT_CACHE, "w") as f:
        json.dump(res, f)
    print(f"SUCCESS app_id={res['app_id']}")
    print(f"open_id (use as FEISHU_ALLOWED_USERS)={res.get('open_id')}")
    print(f"\nNext: append to ~/.hermes/.env\n"
          f"FEISHU_APP_ID={res['app_id']}\n"
          f"FEISHU_APP_SECRET={res['app_secret']}\n"
          f"FEISHU_DOMAIN={res.get('domain', DOMAIN)}\n"
          f"FEISHU_CONNECTION_MODE=websocket\n"
          f"FEISHU_ALLOWED_USERS={res.get('open_id','')}")


def cmd_probe():
    """Verify credentials and print bot name — no gateway needed."""
    res = json.load(open(RESULT_CACHE))
    app_id, app_secret = res["app_id"], res["app_secret"]
    info = fad.probe_bot(app_id, app_secret, res.get("domain", DOMAIN))
    print(json.dumps(info, indent=2, ensure_ascii=False) if info else "probe failed")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "begin"
    {"begin": cmd_begin, "poll": cmd_poll, "probe": cmd_probe}[cmd]()
