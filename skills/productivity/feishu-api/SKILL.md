---
name: feishu-api
description: 读写飞书(Lark)文档、云盘文件、知识库——通过脚本调飞书开放平台 API 补足 Hermes 原生工具缺口（原生只有 feishu_doc_read + 评论工具）。当需要在飞书里建文档、填表格、上传下载云盘文件、同步知识库时使用。凭证在 ~/.hermes/.env。
category: productivity
tags: [feishu, lark, 飞书, document, drive, wiki, api]
---

# 飞书 API 工具包 (feishu-api)

用脚本调飞书开放平台 API，补足 Hermes 原生飞书工具的缺口。

## 什么时候用

- 在飞书里**新建文档 / 修改文档正文**（原生只能读）
- **上传/下载云盘文件**（原生没有）
- **知识库**读写（原生没有）
- 批量处理飞书文档、自动填表格、归档

Hermes 原生飞书工具只有 5 个：
`feishu_doc_read` + `feishu_drive_{list_comments,list_comment_replies,reply_comment,add_comment}`
（读文档 + 评论交互）。其余要靠本脚本。

## 前置条件

1. **飞书应用已建**（扫码即建：`hermes gateway setup` → Feishu）
2. **凭证在 ~/.hermes/.env**：
   ```
   FEISHU_APP_ID=cli_xxx
   FEISHU_APP_SECRET=xxx
   FEISHU_DOMAIN=feishu
   ```
3. **权限已开通**（关键！否则 API 返回 code=99991672）：
   - 云盘：`drive:drive` `drive:drive:readonly` `space:document:retrieve`
   - 文档：`docs:doc` `docs:doc:readonly`
   - 知识库：`wiki:wiki` `wiki:wiki:readonly` `wiki:space:retrieve`

### 权限报错时：拿一键申请链接

飞书 API 报权限不足时，error msg 里**自带一键申请 URL**：

```
https://open.feishu.cn/app/<APP_ID>/auth?q=drive:drive,drive:drive:readonly,space:document:retrieve,wiki:wiki,wiki:wiki:readonly&op_from=openapi&token_type=tenant
```
开通后**必须去"版本管理与发布"创建版本并发布**，权限才生效。

## 用法

```python
import sys
sys.path.insert(0, "~/.hermes/skills/productivity/feishu-api/scripts")
from feishu_api import FeishuClient
c = FeishuClient()          # 自动从 ~/.hermes/.env 读凭证

c.list_files()                          # 列云盘根目录
c.list_files(folder_token="fldcnXXX")   # 列指定文件夹
c.create_folder("归档", parent_token="") # 建文件夹
c.upload_file("/tmp/a.pdf", parent_token="")   # 上传
c.download_file("file_token", "/dst/a.pdf")    # 下载
c.read_doc("doxcnXXX")                  # 读文档正文（纯文本）
c.create_doc("我的文档")                 # 新建文档
c.write_doc_blocks(doc_id, "第一行\n第二行") # 追加段落
c.list_wiki_spaces()                    # 列知识库
c.get_wiki_node("wikcnXXX")             # 查知识库节点
```

命令行自测：
```bash
python3 scripts/feishu_api.py test
```

## 关键坑

1. **权限分两批，必须分别申请**
   - 云盘/知识库: `drive:drive,drive:drive:readonly,space:document:retrieve,wiki:wiki,wiki:wiki:readonly,wiki:space:retrieve`
   - 文档读写: `docx:document,docx:document:create`
   两批都要"创建版本→发布"才生效（个人版自己批）
2. **两个上传接口别混淆**（实测踩过）：
   - 传文件到**云盘文件夹** → `POST /drive/v1/files/upload_all`（parent_type=explorer）
   - 传素材到**文档内** → `POST /drive/v1/medias/upload_all`（parent_type=docx_image/docx_file）
   字段必须含 file_name / parent_type / parent_node / size / file，且 boundary 格式要正确
3. **doc_token** = 文档 URL `xxx.feishu.cn/docx/<TOKEN>` 里的 TOKEN
4. **接口前缀**：文档 `/open-apis/docx/v1/`，云盘 `/open-apis/drive/v1/`，知识库 `/open-apis/wiki/v2/`
5. **tenant_access_token 有效期 2 小时**——脚本已缓存自动刷新
6. **知识库节点≠文档**——要先 get_node 拿 obj_token 再读
7. **频控**：飞书 API 有 QPS 限制，批量操作间隔 0.5s+
8. **写文档正文**用 blocks children 接口：`POST /docx/v1/documents/{doc_id}/blocks/{doc_id}/children`
   block_type=2 是文本段落，elements 里放 text_run.content

## 实测结果（2026-10-12 全通过）

```
✅ 列云盘 / 建文件夹 / 上传文件 / 列文件夹 / 下载文件（闭环）
✅ 列知识库
✅ 建文档 / 写文档 / 读文档（闭环，内容一字不差）
```

上线时的应用: `cli_aa46edd75679dbe2`（名"用户283408的智能助手"）
测试产物: 云盘 `Hermes测试/` 文件夹 + `Hermes测试文档`

## 相关

- 消息平台接入（扫码建应用 / WebSocket 模式）见 `hermes-agent` 技能
- 本机已接入：飞书（websocket）、微信、Telegram
