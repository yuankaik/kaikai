#!/usr/bin/env python3
"""Batch migrate skills from multiple sources into ~/.hermes/skills/
Usage: python3 batch_migrate_skills.py
"""
import os
import shutil
from pathlib import Path

HERMES_SKILLS = Path.home() / ".hermes" / "skills"

# Define sources as (path, name_prefix)
# prefix avoids name clashes when skills from different sources share names
SOURCES = [
    (Path.home() / ".local" / "skills", ""),
    (Path.home() / ".local" / "optional-skills", "opt-"),
    (Path("/mnt/c/Users/admin/.agents/skills"), "agents-"),
    (Path("/mnt/c/Users/admin/superpowers/skills"), "super-"),
    (Path("/mnt/c/Users/admin/.codex/skills/.system"), "codex-"),
    (Path.home() / ".agents" / "skills", "vercel-"),
]

stats = {"migrated": 0, "skipped": 0, "errors": 0}

for source_base, prefix in SOURCES:
    if not source_base.exists():
        print(f"SKIP: {source_base} (not found)")
        continue

    for skill_md in source_base.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        rel = skill_dir.relative_to(source_base)
        parts = rel.parts

        # Determine category and sanitized name
        category = parts[0] if len(parts) > 1 else "misc"
        skill_name = (prefix + "-".join(parts)).lower().replace(" ", "-").replace("_", "-")

        dest_dir = HERMES_SKILLS / category / skill_name
        dest_md = dest_dir / "SKILL.md"

        if dest_md.exists():
            stats["skipped"] += 1
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_md, dest_md)

            # Copy supporting directories
            for sub in ["references", "templates", "scripts", "assets"]:
                src_sub = skill_dir / sub
                if src_sub.is_dir():
                    dst_sub = dest_dir / sub
                    if not dst_sub.exists():
                        shutil.copytree(src_sub, dst_sub)

            stats["migrated"] += 1
            if stats["migrated"] % 20 == 0:
                print(f"  Migrated {stats['migrated']}...")

        except Exception as e:
            stats["errors"] += 1
            print(f"  ERROR: {skill_name}: {e}")

print(f"\nMigrated: {stats['migrated']}")
print(f"Skipped (already exist): {stats['skipped']}")
print(f"Errors: {stats['errors']}")
