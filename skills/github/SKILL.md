---
name: github
description: Inspect GitHub repositories, search code and issues, clone repos, manage pull requests, and execute GitHub operations directly.
keywords:
  - github
  - github repo
  - github pr
  - github issue
  - gh cli
  - clone github
  - github search
  - pull request
  - inspect repository
  - github skill
---

# GitHub Skill Tools

You are helping the user interact directly with GitHub repositories, issues, pull requests, and search using native AXIM tools.

## Available Direct Tools

### 1. `github_repo_view`
Inspect repository details (stars, forks, description, default branch, visibility, topics).
```json
{"name": "github_repo_view", "arguments": {"repo": "owner/repo"}}
```

### 2. `github_search`
Search across GitHub repositories, code, or issues.
```json
{"name": "github_search", "arguments": {"query": "axim-skills", "search_type": "repositories", "limit": 5}}
```

### 3. `github_issue_list`
List issues or bug reports from a GitHub repository.
```json
{"name": "github_issue_list", "arguments": {"repo": "owner/repo", "state": "open", "limit": 10}}
```

### 4. `github_pr_view`
Inspect a pull request, review comments, diff summary, and mergeable state.
```json
{"name": "github_pr_view", "arguments": {"repo": "owner/repo", "pr_number": 42}}
```

### 5. `github_pr_create`
Create a pull request from a branch to base.
```json
{"name": "github_pr_create", "arguments": {"repo": "owner/repo", "title": "Feat: Add new tool", "head": "feature-branch", "base": "main", "body": "Summary of changes"}}
```

### 6. `github_clone`
Clone a public or private GitHub repository into the local workspace.
```json
{"name": "github_clone", "arguments": {"repo": "owner/repo", "destination": "local/path"}}
```

### 7. `github_cli`
Execute native `gh` commands for advanced workflows.
```json
{"name": "github_cli", "arguments": {"command": "release list -R owner/repo"}}
```

## Best Practices
- Normalize repository names: accepts `owner/repo`, `https://github.com/owner/repo`, or `git@github.com:owner/repo.git`.
- If unauthenticated, public repository operations still work via public endpoints. For private operations, ensure `gh auth login` or `GITHUB_TOKEN` environment variable is present.
- Always prefer calling structured tools (`github_repo_view`, `github_issue_list`, etc.) before falling back to generic shell commands.
