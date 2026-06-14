# 微信 iLink QR 码生成技术

## 关键发现

`hermes gateway setup` 的 TUI 菜单不接受数字输入，只能方向键导航。PTY 模拟方向键也不可靠。

## 解决方案

直接调用 iLink Bot API 获取 QR 码，生成 PNG 图片到桌面。

### API 端点

```
GET https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3
Headers:
  iLink-App-Id: bot
  iLink-App-ClientVersion: 131584  (2<<16 | 2<<8 | 0 = 2.2.0)
```

### 成功流程

1. 调用 `get_bot_qrcode` → 获取 `qrcode_value` 和 `qrcode_url`
2. 用 Python `qrcode` 库生成 PNG → 保存到 Windows 桌面
3. 轮询 `get_qrcode_status?qrcode=<value>` → 检测状态
4. 状态变化：wait → scaned → confirmed
5. confirmed 时获取 `ilink_bot_id`、`bot_token`、`baseurl`
6. 保存凭据到 `~/.hermes/weixin/accounts/<id>.json`
7. 写入环境变量到 `~/.hermes/.env`

### 已知限制

- iLink bot 身份（`@im.bot`）通常无法加入普通微信群
- 私聊完全可用
- 第三方扫码者直接私聊 bot 即可，无需扫 Hermes QR

### 参考脚本

见 `scripts/wechat_qr_login.py`
