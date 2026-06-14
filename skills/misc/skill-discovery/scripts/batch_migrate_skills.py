#!/usr/bin/env python3
"""Batch migrate skills from multiple source directories into ~/.hermes/skills/"""
import os
import shutil
from pathlib import Path

HERMES_SKILLS = Path.home() / ".hermes" / "skills"

# Configure sources: (directory, prefix_for_unique_names)
SOURCES = [
    (Path.home() / ".local" / "skills", ""),
    (Path.home() / ".local" / "optional-skills", "opt-"),
    # Add more sources as needed:
    # (Path("/mnt/c/Users/admin/.agents/skills"), "agents-"),
    # (Path("/mnt/c/Users/admin/superpowers/skills"), "super-"),
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

        if len(parts) == 1:
            category = "misc"
            skill_name = f"{prefix}{parts[0]}"
        else:
            category = parts[0]
            skill_name = f"{prefix}{'-'.join(parts)}"

        skill_name = skill_name.lower().replace(" ", "-").replace("_", "-")
        dest_dir = HERMES_SKILLS / category / skill_name
        dest_md = dest_dir / "SKILL.md"

        if dest_md.exists():
            stats["skipped"] += 1
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_md, dest_md)

            for sub in ["references", "templates", "scripts", "assets"]:
                src_sub = skill_dir / sub
                if src_sub.is_dir() and not (dest_dir / sub).exists():
                    shutil.copytree(src_sub, dest_dir / sub)

            stats["migrated"] += 1
            if stats["migrated"] % 50 == 0:
                print(f"  Migrated {stats['migrated']}...")

        except Exception as e:
            stats["errors"] += 1
            print(f"  ERROR: {skill_name}: {e}")

print(f"\nMigrated: {stats['migrated']}")
print(f"Skipped: {stats['skipped']}")
print(f"Errors: {stats['errors']}")
