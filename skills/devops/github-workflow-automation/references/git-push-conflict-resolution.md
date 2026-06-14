# Git Push Conflict Resolution

Patterns for resolving push conflicts when a local repo and GitHub remote have diverged.

## Scenario: Remote has auto-generated content, local has new content

Happens when:
- GitHub auto-creates README, .gitignore, LICENSE on repo creation
- User initializes locally with their own versions
- First push gets: `! [rejected] main -> main (fetch first)`

### Wrong Approaches

❌ `git push --force` — destructive, may lose remote commits the user cares about
❌ `git rebase --abort; git push --force` — same risk

### Correct Approach

```bash
# 1. Pull with --allow-unrelated-histories (repos have independent root commits)
#    Use --no-rebase to merge rather than rebase (rebase can cause conflicts on every file)
git pull origin main --allow-unrelated-histories --no-rebase

# 2. If auto-merge succeeds for most files but conflicts on some:
#    - Check which files conflict: git status
#    - Resolve by editing to keep the superset of both versions
#    - For .gitignore: merge entries from both sides, deduplicate

# 3. Stage and commit the merge
git add <resolved-files>
git commit -m "Merge: combine local and remote content"

# 4. Push
git push origin main
```

## Merge Conflict Resolution Strategy

When conflicting on config-style files (.gitignore, .env.example, etc.):
- Keep ALL entries from both sides
- Deduplicate identical entries
- Group similar entries together (e.g., Python, Node, IDE, OS sections)
- Preserve project-specific entries from the remote (they were there for a reason)

## Pitfalls

- `git rebase` on unrelated histories applies each local commit individually, causing N conflicts for N commits. Prefer `git merge` with `--allow-unrelated-histories`.
- The user may deny `--force` pushes (rightly so). Always default to merge-based resolution.
- Check `git status` after pulls — the repo can enter a conflicted state that persists across commands. Always resolve before continuing.
