# B站 API 速查

## 不需要登录/Cookie 的公开API

### 搜索UP主
```
GET https://api.bilibili.com/x/web-interface/search/type
  ?search_type=bili_user
  &keyword={urlencode(关键词)}
```
返回: `data.result[].mid` + `uname`

### 获取视频列表（通过搜索）
```
GET https://api.bilibili.com/x/web-interface/search/type
  ?search_type=video
  &keyword={urlencode(UP主名)}
  &page=1
```
筛选 `author == UP主名`。page 翻页。

### 视频信息 + cid
```
GET https://api.bilibili.com/x/web-interface/view?bvid={bvid}
```
返回: `data.cid`, `data.title`, `data.duration`

### 检查CC字幕
```
GET https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}
```
返回: `data.subtitle.subtitles[]` — 如果非空则有字幕
字幕JSON URL: `subtitle_url` 字段

### ★ 获取音频流（无需wbi签名！）
```
GET https://api.bilibili.com/x/player/playurl
  ?bvid={bvid}
  &cid={cid}
  &fnval=16      ← DASH格式（关键参数）
  &fnver=0
  &fourk=1
```
返回: `data.dash.audio[]` — 直接可下载的音频URL
- `base_url`: 音频流地址
- `bandwidth`: 码率（选最高的）
- `mimeType`: audio/mp4

**不需要 wbi 签名** — 这是关键发现。yt-dlp 会被 412 拦截，但这个 API 可以直接调。

### 请求头要求
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com/',
}
```
B站返回通常是 gzip 压缩，需要解压。

## 需要wbi签名的API（本技能不需要，仅供参考）

- `/x/space/wbi/arc/search` (UP主空间视频列表) — 需要wbi签名
- `/x/player/wbi/v2` — 需要wbi签名

如果要用这些，需要先调 `nav` 接口获取 `img_key` + `sub_key`，计算 MD5 签名。
