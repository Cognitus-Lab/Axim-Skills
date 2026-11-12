---
name: axim-scan
description: Full-spectrum static application security testing (SAST), supply-chain SCA analysis, secret detection, and semantic bug pattern searching for AXIM & Berry across 30+ programming languages.
keywords:
  - security scan
  - scan code
  - audit code
  - vulnerability scan
  - supply chain
  - sca
  - sast
  - secrets
  - api keys
  - hardcoded secrets
  - bug detection
  - code review
  - owasp
  - cwe
  - semgrep
  - pattern search
  - semantic search
---

# AXIM Scan — Enterprise Code Security & Bug Detection Skill

The `axim-scan` skill provides static code analysis, supply-chain dependency auditing, credential leak detection, and semantic bug hunting across **30+ programming languages** for Berry and AXIM agents. It searches code, finds bugs, detects vulnerabilities, and provides AI-tailored remediation guidance directly in your workflow.

---

## Language & Ecosystem Support

### 1. Code Analysis (30+ Languages)
- **Systems & Compiled**: C, C++, C#, Go, Rust, Swift, Java, Kotlin, Scala, Dart
- **Scripting & Dynamic**: Python, JavaScript, TypeScript, JSX, TSX, Ruby, PHP, Lua, R, Julia, Perl
- **Functional**: Elixir, Clojure, OCaml, Lisp, Scheme
- **Cloud & Smart Contracts**: Solidity, Terraform, Apex, Dockerfile
- **Configuration & Templates**: JSON, YAML, XML, HTML, Jsonnet, Jinja, ERB

### 2. Supply Chain & Package Managers (12 Languages, 15 Package Managers)
- **JavaScript / TypeScript**: `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`
- **Python**: `requirements.txt`, `Pipfile`, `pyproject.toml`, `poetry.lock`
- **Go**: `go.mod`, `go.sum`
- **Rust**: `Cargo.toml`, `Cargo.lock`
- **Swift**: `Package.swift`, `Package.resolved`
- **Java / Kotlin**: `pom.xml` (Maven), `build.gradle`, `build.gradle.kts` (Gradle)
- **Ruby**: `Gemfile`, `Gemfile.lock`
- **PHP**: `composer.json`, `composer.lock`
- **Dart / Flutter**: `pubspec.yaml`, `pubspec.lock`
- **C# / .NET**: `*.csproj`, `packages.config` (NuGet)

---

## Agent Tool Reference

### 1. `axim_scan`
Full scan of a directory or repository across SAST, Supply Chain, and Secrets:
```json
{
  "name": "axim_scan",
  "arguments": {
    "target_path": ".",
    "severity": "WARNING",
    "output_format": "markdown"
  }
}
```

### 2. `axim_scan_code`
Instant snippet scan in memory (e.g. before applying an edit or during PR review):
```json
{
  "name": "axim_scan_code",
  "arguments": {
    "code": "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')",
    "language": "python",
    "output_format": "markdown"
  }
}
```

### 3. `axim_scan_pattern`
Search code using semantic code patterns with metavariables (`$X`, `$VAL`) and wildcards (`...`):
```json
{
  "name": "axim_scan_pattern",
  "arguments": {
    "pattern": "$X == $X",
    "target_path": "src/",
    "language": "python"
  }
}
```

### 4. `axim_scan_supply_chain`
Dedicated supply-chain dependency scan to check package manifests for unpinned dependencies, insecure HTTP registries, and known risks:
```json
{
  "name": "axim_scan_supply_chain",
  "arguments": {
    "target_path": "."
  }
}
```

### 5. `axim_scan_secrets`
Dedicated secret and credential auditor (AWS keys, GitHub tokens, OpenAI keys, JWTs, Stripe keys, private keys, database URIs):
```json
{
  "name": "axim_scan_secrets",
  "arguments": {
    "target_path": "."
  }
}
```

### 6. `axim_scan_rules_list`
List available security, quality, and supply-chain rules:
```json
{
  "name": "axim_scan_rules_list",
  "arguments": {
    "language": "swift"
  }
}
```

### 7. `axim_scan_explain`
Get AI Assistant remediation guidance, secure coding alternatives, and CWE/OWASP analysis:
```json
{
  "name": "axim_scan_explain",
  "arguments": {
    "rule_id": "axim.security.injection.sql-concat"
  }
}
```

### 8. `axim_scan_ensure_cli`
Checks engine status and reports active native or CLI accelerators:
```json
{
  "name": "axim_scan_ensure_cli",
  "arguments": {}
}
```
