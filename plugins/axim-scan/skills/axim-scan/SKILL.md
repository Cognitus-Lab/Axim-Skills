---
name: axim-scan
description: Static application security testing (SAST), code vulnerability auditing, and bug detection engine for AXIM & Berry. Scan repositories, workspaces, and code snippets for OWASP Top 10 vulnerabilities, CWE security flaws, and hardcoded secrets with automated fixes.
keywords:
  - security scan
  - scan code
  - audit code
  - vulnerability scan
  - check security
  - find bugs
  - security risk
  - sast
  - owasp
  - cwe
  - sql injection
  - command injection
  - xss
  - hardcoded secrets
  - api keys
  - code review
---

# AXIM Scan — Security & Bug Detection Skill

The `axim-scan` skill provides static application security testing (SAST), vulnerability analysis, and automated bug detection for Berry and AXIM agents. It inspects workspaces, single source files, PR diffs, or code snippets to identify critical security flaws, OWASP Top 10 vulnerabilities, CWE weaknesses, and secret leaks before code is deployed.

---

## Capabilities

1. **Security Vulnerability Scanning**:
   - Detects SQL Injection (`CWE-89`), Command Injection (`CWE-78`), Arbitrary Code Execution (`CWE-95`).
   - Detects Cross-Site Scripting (`CWE-79`) and insecure DOM sinks (`innerHTML`, `dangerouslySetInnerHTML`).
   - Detects Path Traversal and arbitrary file read/writes (`CWE-22`).
   - Detects Insecure Deserialization (`CWE-502`) and Server-Side Request Forgery (`CWE-918`).
   - Identifies Broken Cryptography (`CWE-328`: MD5/SHA1 for sensitive tokens) and disabled SSL/TLS certificate verification (`CWE-295`).

2. **Hardcoded Secrets & Credential Detection**:
   - Detects embedded API keys, JWT tokens, AWS IAM credentials, private RSA/EC keys, and bearer tokens (`CWE-798`).

3. **Code Quality & Bug Auditing**:
   - Identifies unclosed file handles and resource leaks (`CWE-775`).
   - Proposes concrete remediation patches and secure code alternatives.

---

## Agent Tool Reference

### 1. `axim_scan`
Scans a target directory, repository, or single file:
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
Scans an in-memory code snippet without saving to disk:
```json
{
  "name": "axim_scan_code",
  "arguments": {
    "code": "def query(user_id):\n    return db.execute(f'SELECT * FROM users WHERE id = {user_id}')",
    "language": "python",
    "output_format": "markdown"
  }
}
```

### 3. `axim_scan_rules_list`
Lists all active vulnerability and bug rules:
```json
{
  "name": "axim_scan_rules_list",
  "arguments": {
    "language": "typescript"
  }
}
```

### 4. `axim_scan_explain`
Provides deep remediation guidance and secure coding patterns for a finding:
```json
{
  "name": "axim_scan_explain",
  "arguments": {
    "rule_id": "axim.security.injection.sql-string-concat"
  }
}
```

### 5. `axim_scan_ensure_cli`
Checks scanning engine status:
```json
{
  "name": "axim_scan_ensure_cli",
  "arguments": {}
}
```

---

## Supported Languages

- Python (`.py`)
- JavaScript & TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`)
- Go (`.go`)
- Swift (`.swift`)
- Java (`.java`)
- Rust (`.rs`)
- C & C++ (`.c`, `.cpp`, `.h`)
- Ruby (`.rb`)
- PHP (`.php`)
- Shell scripts (`.sh`, `.bash`)
- Configuration & Secrets (`.json`, `.yaml`, `.yml`, `.env`)
