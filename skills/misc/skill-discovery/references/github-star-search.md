# GitHub API Star Search — Quick Reference

One-liner to fetch and display repository rankings:

```bash
curl -s "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=10&page=1" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for i, repo in enumerate(data.get('items', []), 1):
    desc = (repo.get('description') or 'N/A')[:120]
    stars = repo['stargazers_count']
    name = repo['full_name']
    lang = repo.get('language', '') or ''
    print(f'{i:2}. \u2b50 {stars:>6,}  {name}')
    print(f'    [{lang}] {desc}')
    print()
"
```

## Parameters

| Param | Value | Description |
|-------|-------|-------------|
| `q` | `stars:>1` | Minimum stars filter |
| `sort` | `stars` | Sort by star count |
| `order` | `desc` | Descending order |
| `per_page` | `10` | Results per page (max 100) |
| `page` | `1..N` | Page number (max 1000 results total) |

## Rate Limits

- Anonymous: ~10 requests/minute
- With token: ~30 requests/minute for search API

No token needed for casual browsing — just don't hammer the API.

## Advanced Filters

```bash
# By language
q=stars:>1+language:python

# By topic
q=stars:>1+topic:agent

# By date range
q=stars:>1+created:>2025-01-01

# Exclude archived
q=stars:>1+archived:false
```
