#!/usr/bin/env python3
"""
微信 iLink QR 登录 — 生成 QR 码图片并等待扫码确认。

绕过 hermes gateway setup 的 TUI 交互问题，直接调用 iLink Bot API。
适用于：
- TUI 在 PTY 模式下方向键不工作
- 需要在 WSL 中生成 QR 到 Windows 桌面
- 脚本化/自动化微信连接

依赖: aiohttp, qrcode, pillow (PIL)
"""
import asyncio
import sys
import os
import time
import json
import ssl

import aiohttp

ILINK_BASE_URL = "https://ilinkai.weixin.qq.com"
ILINK_APP_ID = "bot"
ILINK_APP_CLIENT_VERSION = (2 << 16) | (2 << 8) | 0  # 2.2.0

EP_GET_BOT_QR = "ilink/bot/get_bot_qrcode"
EP_GET_QR_STATUS = "ilink/bot/get_qrcode_status"

HERMES_HOME = os.path.expanduser("~/.hermes")


def make_ssl_connector():
    return aiohttp.TCPConnector(ssl=ssl.create_default_context())


async def api_get(session, endpoint, base_url=ILINK_BASE_URL, timeout_ms=35000):
    """Replicates gateway.platforms.weixin._api_get — requires iLink headers."""
    url = f"{base_url.rstrip('/')}/{endpoint}"
    headers = {
        "iLink-App-Id": ILINK_APP_ID,
        "iLink-App-ClientVersion": str(ILINK_APP_CLIENT_VERSION),
    }

    async def _do():
        async with session.get(url, headers=headers) as response:
            raw = await response.text()
            if not response.ok:
                raise RuntimeError(f"iLink GET {endpoint} HTTP {response.status}: {raw[:200]}")
            return json.loads(raw)

    return await asyncio.wait_for(_do(), timeout=timeout_ms / 1000)


def find_desktop_path():
    """Find Windows Desktop path from WSL."""
    desktop = "/mnt/c/Users/admin/Desktop"
    try:
        users = os.listdir("/mnt/c/Users/")
        for u in sorted(users):
            dp = f"/mnt/c/Users/{u}/Desktop"
            if os.path.isdir(dp) and u not in ("All Users", "Default", "Default User", "Public"):
                desktop = dp
                break
    except Exception:
        pass
    return desktop


async def main():
    desktop = find_desktop_path()
    print(f"桌面路径: {desktop}")

    async with aiohttp.ClientSession(trust_env=True, connector=make_ssl_connector()) as session:
        # Step 1: Get QR code from iLink API
        print("正在获取二维码...")
        try:
            qr_resp = await api_get(session, f"{EP_GET_BOT_QR}?bot_type=3")
        except Exception as e:
            print(f"获取二维码失败: {e}")
            return 1

        qrcode_value = str(qr_resp.get("qrcode") or "")
        qrcode_url = str(qr_resp.get("qrcode_img_content") or "")

        if not qrcode_value:
            print("二维码响应缺少 qrcode 字段")
            print(f"完整响应: {json.dumps(qr_resp, indent=2, ensure_ascii=False)}")
            return 1

        # qrcode_url is the scannable liteapp URL; qrcode_value is the raw hex token
        qr_scan_data = qrcode_url if qrcode_url else qrcode_value
        print(f"二维码 URL: {qr_scan_data[:100]}...")

        # Step 2: Generate QR image to desktop
        img_path = os.path.join(desktop, "wechat_qr.png")
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_scan_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(img_path)
            print(f"\n✅ QR 码已保存到: {img_path}")
            print("   请用微信扫描桌面上的 wechat_qr.png")
        except Exception as e:
            print(f"生成 QR 图片失败: {e}")
            print("请直接用微信扫描上面的二维码 URL")

        # Step 3: Poll for QR scan status
        print("\n等待扫码... (480秒超时, 按 Ctrl+C 退出)")
        deadline = time.monotonic() + 480
        current_base_url = ILINK_BASE_URL
        refresh_count = 0

        while time.monotonic() < deadline:
            try:
                status_resp = await api_get(
                    session,
                    f"{EP_GET_QR_STATUS}?qrcode={qrcode_value}",
                    base_url=current_base_url,
                )
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
                continue
            except Exception as exc:
                print(f"轮询错误: {exc}")
                await asyncio.sleep(1)
                continue

            status = str(status_resp.get("status") or "wait")

            if status == "wait":
                print(".", end="", flush=True)
            elif status == "scaned":
                print("\n📱 已扫码，请在微信里点击确认...")
            elif status == "scaned_but_redirect":
                redirect_host = str(status_resp.get("redirect_host") or "")
                if redirect_host:
                    current_base_url = f"https://{redirect_host}"
            elif status == "expired":
                refresh_count += 1
                if refresh_count > 3:
                    print("\n❌ 二维码多次过期，请重新执行。")
                    return 1
                print(f"\n🔄 二维码已过期，刷新中... ({refresh_count}/3)")
                try:
                    qr_resp = await api_get(session, f"{EP_GET_BOT_QR}?bot_type=3")
                    qrcode_value = str(qr_resp.get("qrcode") or "")
                    qrcode_url = str(qr_resp.get("qrcode_img_content") or "")
                    qr_scan_data = qrcode_url if qrcode_url else qrcode_value
                    qr2 = qrcode.QRCode(
                        version=None,
                        error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=10,
                        border=4,
                    )
                    qr2.add_data(qr_scan_data)
                    qr2.make(fit=True)
                    img2 = qr2.make_image(fill_color="black", back_color="white")
                    img2.save(img_path)
                    print(f"✅ 新 QR 码已更新: {img_path}")
                except Exception as exc:
                    print(f"刷新失败: {exc}")
                    return 1
            elif status == "confirmed":
                account_id = str(status_resp.get("ilink_bot_id") or "")
                token = str(status_resp.get("bot_token") or "")
                base_url = str(status_resp.get("baseurl") or ILINK_BASE_URL)

                if not account_id or not token:
                    print("❌ 确认成功但凭据不完整")
                    return 1

                print(f"\n\n✅ 微信连接成功！")
                print(f"  account_id: {account_id}")
                print(f"  token: {token[:30]}...")
                print(f"  base_url: {base_url}")

                # Save credentials
                accounts_dir = os.path.join(HERMES_HOME, "weixin", "accounts")
                os.makedirs(accounts_dir, exist_ok=True)
                creds = {"account_id": account_id, "token": token, "base_url": base_url}
                cred_file = os.path.join(accounts_dir, f"{account_id}.json")
                with open(cred_file, "w") as f:
                    json.dump(creds, f, indent=2)
                print(f"凭据已保存到: {cred_file}")

                # Update .env
                env_path = os.path.join(HERMES_HOME, ".env")
                update_env(env_path, account_id)
                print(f"环境变量已写入: {env_path}")
                print(f"\n接下来需要重启 gateway:")
                print(f"  hermes gateway restart")
                return 0

            await asyncio.sleep(2)

        print("\n⏰ 登录超时")
        return 1


def update_env(env_path, account_id):
    """Update ~/.hermes/.env with WEIXIN_* vars and GATEWAY_ALLOW_ALL_USERS."""
    env_lines = []
    weixin_done = {"ACCOUNT_ID": False, "DM_POLICY": False}
    gateway_done = False
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("WEIXIN_ACCOUNT_ID="):
                    weixin_done["ACCOUNT_ID"] = True
                    env_lines.append(f"WEIXIN_ACCOUNT_ID={account_id}\n")
                elif line.startswith("WEIXIN_DM_POLICY="):
                    weixin_done["DM_POLICY"] = True
                    env_lines.append(line)
                elif line.startswith("GATEWAY_ALLOW_ALL_USERS="):
                    gateway_done = True
                    env_lines.append(line)
                else:
                    env_lines.append(line)
    if not weixin_done["ACCOUNT_ID"]:
        env_lines.append(f"WEIXIN_ACCOUNT_ID={account_id}\n")
    if not weixin_done["DM_POLICY"]:
        env_lines.append("WEIXIN_DM_POLICY=open\n")
    if not gateway_done:
        env_lines.append("GATEWAY_ALLOW_ALL_USERS=true\n")
    with open(env_path, "w") as f:
        f.writelines(env_lines)


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n用户取消")
        sys.exit(1)
