#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审计 Hermes 技能库中的 frontmatter name 冲突。

两个 SKILL.md 的 `name:` 相同 → Hermes 拒绝按名加载（Ambiguous / Unknown），
并会让 kanban/dispatcher 的 worker 加载技能时崩溃。

用法:
    python3 audit_skill_name_collisions.py            # 扫描默认技能库
    python3 audit_skill_name_collisions.py --root DIR # 指定根目录
退出码: 0 = 无冲突, 1 = 有冲突（可用于 CI / 定时检查）
"""
import argparse, collections, os, re, sys

DEFAULT_ROOT = os.path.expanduser("~/.hermes/skills")


def scan(root):
    names = collections.defaultdict(list)
    for dirpath, _, files in os.walk(root):
        if "SKILL.md" not in files:
            continue
        p = os.path.join(dirpath, "SKILL.md")
        try:
            c = open(p, encoding="utf-8").read()
        except Exception:
            continue
        m = re.search(r"^name:\s*(.+?)\s*$", c, re.M)
        if m:
            names[m.group(1)].append(os.path.relpath(p, root))
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    args = ap.parse_args()

    names = scan(args.root)
    dups = {k: v for k, v in names.items() if len(v) > 1}

    print(f"技能总数: {len(names)}")
    print(f"冲突数:   {len(dups)}")

    if not dups:
        print("\n✅ 无冲突")
        return 0

    print()
    for name, paths in sorted(dups.items()):
        print(f"「{name}」")
        for p in paths:
            print(f"    {p}")
    print("\n修复: 给重复项加来源前缀（super- / gstack-legacy- / agents- / opt-），"
          "只改 frontmatter 的 name，不动目录名。改前先备份。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
