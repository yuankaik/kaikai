# sou.st 下载端点损坏记录 — 2026-07-21

## 错误

所有文件下载返回 HTTP 500，响应体为 HTML 错误页：

```
TypeError: App\Http\Controllers\FileController::download(): 
Argument #2 ($id) must be of type int, string given

called in /www/wwwroot/sou.st/vendor/laravel/framework/src/Illuminate/Routing/Controller.php
on line 54 in file /www/wwwroot/sou.st/app/...
```

## 测试过的 URL 格式

| URL 格式 | 结果 |
|----------|------|
| `/file/186720-epub/download` | HTTP 500 (传入了 "186720-epub" 字符串) |
| `/file/186720/download` | HTTP 500 (同上错误) |
| `/file/161187/download` | HTTP 500 |

## 测试过的下载方式

| 方式 | 结果 |
|------|------|
| curl + cookie jar | HTTP 500, 1.1MB HTML 错误页 |
| Python requests.Session | HTTP 500, 1.1MB HTML 错误页 |
| 浏览器点击 "Download Now" | 未测试（Browserbase 远程浏览器无法取回文件） |

## 文件页 URL 格式

文件详情页正常访问，URL 格式为 `/file/{ID}-epub`（例如 `/file/186720-epub`）。

搜索结果显示正常，文件 ID 提取也正常。

## 登录

登录功能正常 — 浏览器表单登录和 curl/Python 登录都成功（302 → dashboard）。

## 建议

1. 等 sou.st 修好下载端点再尝试
2. 或者用浏览器直接点击 "Download Now" 按钮下载（需要本地浏览器）
3. 换其他渠道下载这些书（Z-Library、Anna's Archive）
