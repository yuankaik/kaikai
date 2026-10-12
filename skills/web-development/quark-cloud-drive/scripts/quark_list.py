"""Quark cloud drive file listing — zero-auth approach.

USAGE:
    python3 quark_list.py <pwd_id> [pwd_id ...]

Each pwd_id is extracted from a pan.quark.cn/s/<pwd_id> URL.
Prints a tree of all files/folders found in each share link.

Requires: Python 3 stdlib only (no pip install needed).
Authentication: None needed for listing.
"""

import urllib.request, json, urllib.parse, sys, time

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://pan.quark.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_token(pwd_id):
    url = f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc&pwd_id={pwd_id}"
    req = urllib.request.Request(url,
        data=json.dumps({"pwd_id": pwd_id, "passcode": ""}).encode(),
        headers=HEADERS, method='POST')
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    if data.get("status") != 200:
        raise RuntimeError(f"Token error: {data}")
    return data["data"]["stoken"], data["data"].get("title", "未知")

def list_dir(pwd_id, stoken, pdir_fid="0"):
    url = (f"https://drive-pc.quark.cn/1/clouddrive/share/sharepage/detail?"
           f"pr=ucpro&fr=pc&pwd_id={pwd_id}&stoken={urllib.parse.quote(stoken)}"
           f"&pdir_fid={pdir_fid}&_page=1&_size=100"
           f"&_sort=file_type:asc,updated_at:desc")
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())["data"]["list"]

def walk(pwd_id, stoken, fid="0", prefix="", max_depth=3):
    """Recursively walk folder tree, printing files."""
    if max_depth <= 0:
        print(f"{prefix}... (max depth)")
        return
    try:
        items = list_dir(pwd_id, stoken, fid)
    except Exception as e:
        print(f"{prefix}⚠️ Error: {e}")
        return
    for item in items:
        name = item.get("file_name", "?")
        if item.get("dir"):
            n = item.get("include_items", "?")
            print(f"{prefix}📁 {name}/ ({n} files)")
            walk(pwd_id, stoken, item["fid"], prefix + "  ", max_depth - 1)
        else:
            size_kb = item.get("size", 0) // 1024
            print(f"{prefix}📄 {name} ({size_kb}KB)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quark_list.py <pwd_id> [pwd_id ...]")
        print("  pwd_id from pan.quark.cn/s/<pwd_id>")
        sys.exit(1)

    for pwd_id in sys.argv[1:]:
        try:
            stoken, title = get_token(pwd_id)
            print(f"\n{'='*60}")
            print(f"📦 {title}")
            print(f"🔗 pan.quark.cn/s/{pwd_id}")
            print(f"{'='*60}")
            walk(pwd_id, stoken)
        except Exception as e:
            print(f"\n❌ {pwd_id}: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
