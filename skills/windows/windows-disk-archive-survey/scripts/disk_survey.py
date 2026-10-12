#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""桌面/存档盘点 + 去重探针（windows-disk-archive-survey 技能配套）

用途：在合并/清理前，安全地摸清目录内容并找出真重复，避免误删。

用法：
  python3 disk_survey.py <目录1> [<目录2> ...]
  给两个目录时，自动比对其重复文件（先按相对路径同名，再按 MD5 内容）。
"""
import os
import sys
import hashlib
import collections


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk(root):
    """返回 {相对路径: (绝对路径, 字节数)}"""
    out = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            fp = os.path.join(r, f)
            try:
                out[os.path.relpath(fp, root)] = (fp, os.path.getsize(fp))
            except OSError:
                pass
    return out


def human(n):
    for u in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}T"


def survey(root):
    files = walk(root)
    total = sum(sz for _, sz in files.values())
    by_ext = collections.Counter()
    for rel, (_, sz) in files.items():
        ext = os.path.splitext(rel)[1].lower() or "(无扩展名)"
        by_ext[ext] += sz
    print(f"=== {root} ===")
    print(f"  文件数 {len(files)}  总大小 {human(total)}")
    print("  按类型 top10:")
    for ext, sz in by_ext.most_common(10):
        print(f"    {human(sz):>9}  {ext}")
    print("  顶层条目:")
    for e in sorted(os.listdir(root)):
        p = os.path.join(root, e)
        if os.path.isdir(p):
            print(f"    [DIR] {e}")
        else:
            print(f"    {human(os.path.getsize(p)):>9}  {e}")
    return files


def compare(a_root, b_root):
    a, b = walk(a_root), walk(b_root)
    same_path = set(a) & set(b)
    print("\n=== 重复检测 ===")
    print(f"A={a_root}  ({len(a)} 文件)")
    print(f"B={b_root}  ({len(b)} 文件)")
    print(f"\n同相对路径同名: {len(same_path)}")
    for s in sorted(same_path):
        print("   ", s)
    # 内容级：A 独有文件在 B 里能否按 MD5 找到
    b_by_hash = collections.defaultdict(list)
    for rel, (fp, _) in b.items():
        b_by_hash[md5(fp)].append(rel)
    print("\nA 独有文件的内容级比对:")
    for rel in sorted(set(a) - set(b)):
        fp, _ = a[rel]
        hits = b_by_hash.get(md5(fp), [])
        tag = "内容重复→" + ",".join(hits) if hits else "★内容独有，需保留"
        print(f"   {rel}: {tag}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    for r in args:
        survey(r)
    if len(args) >= 2:
        compare(args[0], args[1])
