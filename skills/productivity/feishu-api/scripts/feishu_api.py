#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu (Lark) API toolkit for Hermes.
读写飞书文档、云盘文件、知识库。

凭证来源: ~/.hermes/.env 的 FEISHU_APP_ID / FEISHU_APP_SECRET

用法:
    from feishu_api import FeishuClient
    c = FeishuClient()
    c.list_files()                       # 列云盘文件
    c.read_doc("doxcnXXXX")              # 读文档正文
    c.create_doc("标题")                  # 新建文档
    c.write_doc(doc_id, "内容")           # 覆盖写文档
    c.upload_file("/path/to/f.pdf")      # 上传文件到云盘
    c.download_file("file_token", "/dst")# 下载云盘文件
    c.list_wiki_spaces()                 # 列知识库
    c.get_wiki_node(space_id, node_token) # 读知识库节点
"""
import os, json, re, urllib.request, urllib.error, time

BASE = "https://open.feishu.cn/open-apis"


def _load_creds():
    env = os.path.expanduser("~/.hermes/.env")
    cid = csec = None
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            line = line.strip()
            if line.startswith("FEISHU_APP_ID="):
                cid = line.split("=", 1)[1].strip()
            elif line.startswith("FEISHU_APP_SECRET="):
                csec = line.split("=", 1)[1].strip()
    cid = cid or os.getenv("FEISHU_APP_ID")
    csec = csec or os.getenv("FEISHU_APP_SECRET")
    if not cid or not csec:
        raise RuntimeError("FEISHU_APP_ID / FEISHU_APP_SECRET not found in ~/.hermes/.env")
    return cid, csec


class FeishuError(Exception):
    pass


class FeishuClient:
    def __init__(self, app_id=None, app_secret=None):
        self.app_id, self.app_secret = (app_id, app_secret) if app_id else _load_creds()
        self._token = None
        self._token_exp = 0

    # ---- auth ----
    def token(self):
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        body = json.dumps({"app_id": self.app_id, "app_secret": self.app_secret}).encode()
        req = urllib.request.Request(f"{BASE}/auth/v3/tenant_access_token/internal",
                                     data=body, headers={"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if r.get("code") != 0:
            raise FeishuError(f"token failed: {r}")
        self._token = r["tenant_access_token"]
        self._token_exp = time.time() + r.get("expire", 7200)
        return self._token

    def _req(self, method, path, params=None, data=None, raw=False):
        url = BASE + path
        if params:
            url += "?" + "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        headers = {"Authorization": f"Bearer {self.token()}"}
        body = None
        if data is not None:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            return resp.read() if raw else json.loads(resp.read())
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "replace")
            raise FeishuError(f"HTTP {e.code} {method} {path}: {payload[:500]}")

    # ---- drive (云盘) ----
    def list_files(self, folder_token=""):
        """列云盘目录文件。folder_token 为空 = 根目录"""
        return self._req("GET", "/drive/v1/files",
                         params={"folder_token": folder_token, "page_size": 200})

    def create_folder(self, name, parent_token=""):
        return self._req("POST", "/drive/v1/files/create_folder",
                         data={"name": name, "folder_token": parent_token})

    def upload_file(self, local_path, parent_token="", name=None):
        """上传文件到云盘（multipart，需 drive:drive 写权限）"""
        import mimetypes, uuid
        name = name or os.path.basename(local_path)
        size = os.path.getsize(local_path)
        boundary = uuid.uuid4().hex
        with open(local_path, "rb") as f:
            content = f.read()
        parts = []
        def field(n, v):
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n".encode())
        field("file_name", name)
        field("parent_type", "explorer")
        field("parent_node", parent_token or self._root_token())
        field("size", str(size))
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: {mimetypes.guess_type(name)[0] or 'application/octet-stream'}\r\n\r\n".encode()
            + content + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        req = urllib.request.Request(f"{BASE}/drive/v1/medias/upload_all", data=body,
            headers={"Authorization": f"Bearer {self.token()}",
                     "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
        return json.loads(urllib.request.urlopen(req, timeout=120).read())

    def _root_token(self):
        r = self.list_files()
        return r.get("data", {}).get("files", [{}])[0].get("parent_token", "") if False else ""

    def download_file(self, file_token, dest_path):
        """下载云盘文件（二进制）"""
        data = self._req("GET", f"/drive/v1/files/{file_token}/download", raw=True)
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(data)
        return dest_path

    # ---- docx (文档) ----
    def read_doc(self, doc_token):
        """读文档纯文本正文"""
        r = self._req("GET", f"/docx/v1/documents/{doc_token}/raw_content")
        if r.get("code") != 0:
            raise FeishuError(f"read_doc failed: {r}")
        return r.get("data", {}).get("content", "")

    def create_doc(self, title, folder_token=""):
        """新建文档，返回 document_id"""
        r = self._req("POST", "/docx/v1/documents",
                      data={"title": title, "folder_token": folder_token})
        if r.get("code") != 0:
            raise FeishuError(f"create_doc failed: {r}")
        return r.get("data", {}).get("document", {}).get("document_id")

    def write_doc_blocks(self, doc_id, text):
        """用子块 API 追加文本段落（简化版，逐段插入）"""
        blocks = []
        for para in text.split("\n"):
            blocks.append({"block_type": 2, "text": {
                "elements": [{"text_run": {"content": para}}], "style": {}}})
        r = self._req("POST", f"/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
                      data={"children": blocks, "index": 0})
        return r

    # ---- wiki (知识库) ----
    def list_wiki_spaces(self):
        return self._req("GET", "/wiki/v2/spaces", params={"page_size": 50})

    def get_wiki_node(self, token):
        return self._req("GET", "/wiki/v2/spaces/get_node", params={"token": token})


if __name__ == "__main__":
    import sys
    c = FeishuClient()
    print("token OK:", c.token()[:12], "...")
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for label, fn in [("云盘列表", lambda: c.list_files()),
                          ("知识库", lambda: c.list_wiki_spaces())]:
            try:
                r = fn()
                print(f"[{label}] code={r.get('code')} {r.get('msg')}")
            except Exception as e:
                print(f"[{label}] ERR: {str(e)[:200]}")
