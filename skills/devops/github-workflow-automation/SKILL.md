---
name: github-workflow-automation
description: GitHub 工作流自动化模式——PR 审查、Issue 分类、CI/CD 集成、Git 操作、仓库配置，支持 AI 辅助
category: devops
source: imported from kai哥's .agents/skills (2026-02-27)
---

# 🔧 GitHub Workflow Automation

> Patterns for automating GitHub workflows with AI assistance, inspired by Gemini CLI and modern DevOps practices.

## When to Use

- Automating PR reviews with AI
- Setting up issue triage automation
- Creating GitHub Actions workflows
- Integrating AI into CI/CD pipelines
- Automating Git operations (rebases, cherry-picks)
- Configuring repository settings (CODEOWNERS, branch protection)

---

## 1. Automated PR Review

### 1.1 PR Review Action

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get changed files
        id: changed
        run: |
          files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          echo "files<<EOF" >> $GITHUB_OUTPUT
          echo "$files" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Get diff
        id: diff
        run: |
          diff=$(git diff origin/${{ github.base_ref }}...HEAD)
          echo "diff<<EOF" >> $GITHUB_OUTPUT
          echo "$diff" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: AI Review
        uses: actions/github-script@v7
        with:
          script: |
            // Call AI API to review PR
            const response = await callAI(`Review this PR:
            Changed files: ${process.env.CHANGED_FILES}
            Diff: ${process.env.DIFF}
            
            Provide: Summary, Issues, Suggestions, Security concerns.
            Format as GitHub markdown.`);

            await github.rest.pulls.createReview({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.issue.number,
              body: response,
              event: 'COMMENT'
            });
        env:
          CHANGED_FILES: ${{ steps.changed.outputs.files }}
          DIFF: ${{ steps.diff.outputs.diff }}
```

### 1.2 Review Comment Template

```markdown
## 📋 Summary
Brief description of what this PR does.

## ✅ What Looks Good
- Well-structured code
- Good test coverage

## ⚠️ Potential Issues
1. **Line X**: Issue description + suggested fix

## 💡 Suggestions
- Improvement ideas

## 🔒 Security Notes
- Security observations
```

### 1.3 Focused Reviews

```yaml
# Review only specific file types
- name: Filter code files
  run: |
    files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | \
            grep -E '\.(ts|py|go|rs|js)$' || true)
```

---

## 2. Issue Triage Automation

### 2.1 Auto-label Issues

```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Analyze and label
        uses: actions/github-script@v7
        with:
          script: |
            const issue = context.payload.issue;
            const analysis = await analyzeIssue(issue.title, issue.body);

            const labels = [];
            if (analysis.type === 'bug') labels.push('bug');
            if (analysis.type === 'feature') labels.push('enhancement');
            if (analysis.area) labels.push(`area: ${analysis.area}`);

            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issue.number,
              labels: labels
            });
```

### 2.2 Issue Analysis Prompt

```json
{
  "type": "bug | feature | question | docs | other",
  "severity": "low | medium | high | critical",
  "area": "frontend | backend | api | docs | ci | other",
  "summary": "one-line summary",
  "hasReproSteps": true/false,
  "suggestedLabels": ["label1", "label2"]
}
```

### 2.3 Stale Issue Management

```yaml
# .github/workflows/stale.yml
name: Manage Stale Issues
on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          stale-issue-message: "Marked as stale. Will close in 14 days if no activity."
          stale-pr-message: "Marked as stale. Please update or will close in 14 days."
          days-before-stale: 60
          days-before-close: 14
          stale-issue-label: "stale"
          stale-pr-label: "stale"
          exempt-issue-labels: "pinned,security,in-progress"
```

---

## 3. CI/CD Integration

### 3.1 Smart Test Selection

```yaml
# .github/workflows/smart-tests.yml
# Only runs tests relevant to changed files
name: Smart Test Selection
on:
  pull_request:

jobs:
  analyze:
    runs-on: ubuntu-latest
    outputs:
      test_suites: ${{ steps.analyze.outputs.suites }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Analyze changes
        id: analyze
        run: |
          changed=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          suites="[]"
          if echo "$changed" | grep -q "^src/api/"; then
            suites=$(echo $suites | jq '. + ["api"]')
          fi
          if echo "$changed" | grep -q "^src/frontend/"; then
            suites=$(echo $suites | jq '. + ["frontend"]')
          fi
          [ "$suites" = "[]" ] && suites='["all"]'
          echo "suites=$suites" >> $GITHUB_OUTPUT

  test:
    needs: analyze
    runs-on: ubuntu-latest
    strategy:
      matrix:
        suite: ${{ fromJson(needs.analyze.outputs.test_suites) }}
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          if [ "${{ matrix.suite }}" = "all" ]; then
            npm test
          else
            npm test -- --suite ${{ matrix.suite }}
          fi
```

### 3.2 AI Deployment Risk Assessment

```yaml
# .github/workflows/deploy.yml
# Validates deployment safety with AI analysis
name: Deploy with AI Validation
on:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AI Risk Assessment
        run: |
          # Analyze commits for deployment risk
          # Risk levels: low, medium, high
          # High = manual approval required
```

### 3.3 Automated Rollback

```yaml
# .github/workflows/rollback.yml
name: Automated Rollback
on:
  workflow_dispatch:
    inputs:
      reason:
        description: "Reason for rollback"
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Find last stable version
        run: |
          stable=$(git tag -l 'v*' --sort=-version:refname | head -1)
          echo "Rolling back to $stable"
          git checkout $stable
```

---

## 4. Git Operations

### 4.1 Auto Rebase on Command

```yaml
# .github/workflows/auto-rebase.yml
# Triggered by commenting /rebase on a PR
name: Auto Rebase
on:
  issue_comment:
    types: [created]

jobs:
  rebase:
    if: github.event.issue.pull_request && contains(github.event.comment.body, '/rebase')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: Rebase PR
        run: |
          gh pr checkout ${{ github.event.issue.number }}
          git fetch origin main
          git rebase origin/main
          git push --force-with-lease
```

### 4.2 Branch Cleanup (Weekly)

```yaml
# .github/workflows/branch-cleanup.yml
name: Branch Cleanup
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Find stale branches
        run: |
          git for-each-ref --sort=-committerdate refs/remotes/origin \
            --format='%(refname:short) %(committerdate:relative)' | \
            grep -E '[3-9][0-9]+ days|[0-9]+ months' | \
            grep -v 'origin/main\|origin/develop'
```

---

## 5. On-Demand Commands

| Command           | Description              |
| :---------------- | :----------------------- |
| `@ai-helper explain` | Explain code in PR    |
| `@ai-helper review`  | Request AI code review   |
| `@ai-helper fix`     | Suggest fixes            |
| `@ai-helper test`    | Generate test cases      |
| `@ai-helper docs`    | Generate documentation   |
| `/rebase`            | Rebase PR onto main      |
| `/label bug`         | Add label                |

---

## 6. Repository Configuration

### 6.1 CODEOWNERS

```
# .github/CODEOWNERS
* @org/core-team
/src/frontend/ @org/frontend-team
/src/api/ @org/backend-team
/.github/ @org/devops-team
```

### 6.2 Branch Protection

```yaml
# Via GitHub API
required_status_checks:
  strict: true
  contexts: ['test', 'lint']
enforce_admins: true
required_pull_request_reviews:
  required_approving_review_count: 1
  require_code_owner_reviews: true
required_linear_history: true
allow_force_pushes: false
allow_deletions: false
```

---

## Best Practices

### Security
- Store API keys in GitHub Secrets
- Use minimal workflow permissions
- Validate all inputs
- Don't expose sensitive data in logs

### Performance
- Cache dependencies between runs
- Use matrix builds for parallel testing
- Skip unnecessary jobs with path filters

### Reliability
- Add timeouts to all jobs
- Handle rate limits gracefully
- Implement retry logic
- Have rollback procedures ready

---

## Reference Files
- `references/git-push-conflict-resolution.md` — Resolving push conflicts when local and remote have unrelated histories (e.g., auto-generated repo content vs. local init). Covers `--allow-unrelated-histories`, merge vs. rebase, and .gitignore conflict merging.

## Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub REST API](https://docs.github.com/en/rest)
- [GitHub CLI (gh)](https://cli.github.com/)
