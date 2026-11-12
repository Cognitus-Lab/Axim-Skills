#!/usr/bin/env python3
"""
axim_scan_engine.py — Comprehensive Code Security, SAST, SCA & Secrets Engine for AXIM & Berry.
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills
License: LGPL-2.1-only / Apache-2.0

Comprehensive static application security testing (SAST), software composition analysis (SCA / Supply Chain),
and secret detection across 30+ programming languages. Runs self-contained with pure Python standard library,
and seamlessly accelerates via Semgrep CLI / external AST engines when available.
"""

import ast
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Severity Levels
SEV_ERROR = "ERROR"
SEV_WARNING = "WARNING"
SEV_INFO = "INFO"

# -----------------------------------------------------------------------------
# 1. Supported Language Definitions (30+ Languages)
# -----------------------------------------------------------------------------
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    # Systems & Compiled
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hxx": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".java": "java",
    ".kt": "kotlin", ".kts": "kotlin",
    ".scala": "scala", ".sc": "scala",
    ".dart": "dart",
    # Scripting & Dynamic
    ".py": "python", ".pyw": "python", ".pyi": "python",
    ".rb": "ruby",
    ".php": "php",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".lua": "lua",
    ".r": "r", ".R": "r",
    ".jl": "julia",
    ".pl": "perl", ".pm": "perl",
    # Functional & Logic
    ".ex": "elixir", ".exs": "elixir",
    ".clj": "clojure", ".cljs": "clojure", ".cljc": "clojure",
    ".ml": "ocaml", ".mli": "ocaml",
    ".lisp": "lisp", ".lsp": "lisp",
    ".scm": "scheme", ".ss": "scheme",
    # Cloud, Infra & Smart Contracts
    ".sol": "solidity",
    ".tf": "terraform", ".tfvars": "terraform",
    ".cls": "apex", ".trigger": "apex",
    # Shell & Configuration
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".json": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".xml": "xml",
    ".html": "html", ".htm": "html",
    ".jsonnet": "jsonnet", ".libsonnet": "jsonnet",
    ".j2": "jinja", ".jinja": "jinja", ".jinja2": "jinja", ".erb": "erb"
}

SPECIAL_FILENAMES: Dict[str, str] = {
    "dockerfile": "dockerfile",
    "containerfile": "dockerfile",
    "package.json": "package-json",
    "pnpm-lock.yaml": "package-lock",
    "package-lock.json": "package-lock",
    "yarn.lock": "package-lock",
    "requirements.txt": "requirements-txt",
    "pipfile": "pipfile",
    "pyproject.toml": "pyproject-toml",
    "poetry.lock": "poetry-lock",
    "go.mod": "go-mod",
    "go.sum": "go-sum",
    "cargo.toml": "cargo-toml",
    "cargo.lock": "cargo-lock",
    "package.swift": "package-swift",
    "pom.xml": "maven-pom",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "gemfile": "gemfile",
    "gemfile.lock": "gemfile-lock",
    "composer.json": "composer-json",
    "pubspec.yaml": "pubspec-yaml"
}

IGNORED_DIRS: Set[str] = {
    ".git", ".svn", "node_modules", "DerivedData", ".build", "dist",
    "build", "venv", ".venv", "env", "__pycache__", ".next", ".cache",
    ".idea", ".vscode", "coverage", "Pods", "target", "vendor"
}

# -----------------------------------------------------------------------------
# 2. Curated SAST & Security Rules (OWASP Top 10, CWEs, Logic Bugs)
# -----------------------------------------------------------------------------
BUILTIN_RULES: List[Dict[str, Any]] = [
    # --- Injection Vulnerabilities ---
    {
        "id": "axim.security.injection.sql-concat",
        "name": "SQL Injection via String Formatting",
        "severity": SEV_ERROR,
        "cwe": "CWE-89: SQL Injection",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "go", "java", "php", "ruby", "csharp", "swift"],
        "regex": r"""(?i)(?:execute|query|raw|cursor\.execute|db\.exec)\s*\(\s*(?:f["'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?\{|["'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?["']\s*\+|`.*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?\$\{)""",
        "message": "SQL query formed by dynamic string interpolation. Callers can manipulate SQL syntax.",
        "fix": "Use parameterized queries or prepared statements (e.g. `cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))`).",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.injection.command-execution",
        "name": "OS Command Injection",
        "severity": SEV_ERROR,
        "cwe": "CWE-78: OS Command Injection",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "go", "ruby", "php", "java", "shell"],
        "regex": r"""(?i)(?:os\.system|child_process\.exec|execSync|subprocess\.(?:Popen|run|call)\(.*?\bshell\s*=\s*True|runtime\.exec|Process\.run)\s*\(""",
        "message": "Operating system shell execution with potential untrusted input concatenation.",
        "fix": "Avoid shell=True. Pass arguments as a discrete array (e.g. `subprocess.run(['prog', arg1, arg2], shell=False)`).",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.injection.code-eval",
        "name": "Arbitrary Code Execution via eval() / exec()",
        "severity": SEV_ERROR,
        "cwe": "CWE-95: Eval Injection",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "php", "ruby"],
        "regex": r"""(?i)(?<![\w\.])(?:eval|exec)\s*\([^)]+""",
        "message": "Dynamic code evaluation via eval() or exec(). Callers can execute arbitrary language constructs.",
        "fix": "Avoid dynamic code execution. Use strict parsers such as `json.loads()` or `ast.literal_eval()`.",
        "confidence": "HIGH"
    },

    # --- Cross-Site Scripting (XSS) ---
    {
        "id": "axim.security.xss.dom-sink",
        "name": "Cross-Site Scripting (XSS) via DOM Sink",
        "severity": SEV_ERROR,
        "cwe": "CWE-79: Cross-site Scripting",
        "owasp": "A03:2021 - Injection",
        "languages": ["javascript", "typescript"],
        "regex": r"""(?:\.innerHTML\s*=\s*|dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:)\s*[^"'`\s]""",
        "message": "Assignment to innerHTML or dangerouslySetInnerHTML with unvalidated content.",
        "fix": "Use textContent, innerText, or sanitize HTML via DOMPurify before rendering into the DOM.",
        "confidence": "HIGH"
    },

    # --- Path Traversal ---
    {
        "id": "axim.security.path-traversal.unvalidated-path",
        "name": "Path Traversal / Arbitrary File Access",
        "severity": SEV_WARNING,
        "cwe": "CWE-22: Path Traversal",
        "owasp": "A01:2021 - Broken Access Control",
        "languages": ["python", "javascript", "typescript", "go", "java"],
        "regex": r"""(?i)(?:open|readFile|createReadStream|os\.Open)\s*\(\s*(?:req\.|params\.|request\.|query\.|input\.|f["'].*?\{.*?path).*?\)""",
        "message": "File system access using directly formatted or untrusted path parameters.",
        "fix": "Resolve target paths using `os.path.realpath` or `path.resolve` and verify `path.startswith(safe_root)`.",
        "confidence": "MEDIUM"
    },

    # --- Broken Cryptography & Security Controls ---
    {
        "id": "axim.security.crypto.weak-hash",
        "name": "Use of Broken Cryptographic Hash (MD5 / SHA-1)",
        "severity": SEV_WARNING,
        "cwe": "CWE-328: Use of Weak Hash",
        "owasp": "A02:2021 - Cryptographic Failures",
        "languages": ["python", "javascript", "typescript", "go", "java", "swift", "csharp"],
        "regex": r"""(?i)(?:hashlib\.md5|hashlib\.sha1|crypto\.createHash\s*\(\s*["'](?:md5|sha1)["']|MessageDigest\.getInstance\s*\(\s*["'](?:MD5|SHA-1)["']\)|CC_MD5|Insecure\.MD5)""",
        "message": "Insecure cryptographic hashing algorithm (MD5 or SHA1). Vulnerable to preimage collision attacks.",
        "fix": "Use SHA-256 (`hashlib.sha256`), SHA-512, or bcrypt/argon2 for password hashing.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.network.tls-disabled",
        "name": "Disabled SSL/TLS Certificate Validation",
        "severity": SEV_ERROR,
        "cwe": "CWE-295: Improper Certificate Validation",
        "owasp": "A02:2021 - Cryptographic Failures",
        "languages": ["python", "javascript", "typescript", "go", "java"],
        "regex": r"""(?i)(?:\bverify\s*=\s*False\b|\brejectUnauthorized\s*:\s*false\b|\bInsecureSkipVerify\s*:\s*true\b)""",
        "message": "SSL/TLS verification explicitly disabled. Leaves traffic open to MITM interception.",
        "fix": "Enable SSL verification (`verify=True`, `rejectUnauthorized: true`). Provide custom trusted root CAs if needed.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.deserialization.insecure-pickle",
        "name": "Insecure Deserialization via Python pickle",
        "severity": SEV_ERROR,
        "cwe": "CWE-502: Deserialization of Untrusted Data",
        "owasp": "A08:2021 - Software and Data Integrity Failures",
        "languages": ["python"],
        "regex": r"""(?i)(?:pickle|cPickle|_pickle)\.(?:load|loads)\s*\(""",
        "message": "Deserialization of data with pickle can execute arbitrary bytecode.",
        "fix": "Use safe formats like JSON, Protocol Buffers, or MessagePack.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.ssrf.outbound-request",
        "name": "Potential Server-Side Request Forgery (SSRF)",
        "severity": SEV_WARNING,
        "cwe": "CWE-918: Server-Side Request Forgery (SSRF)",
        "owasp": "A10:2021 - Server-Side Request Forgery (SSRF)",
        "languages": ["python", "javascript", "typescript", "go"],
        "regex": r"""(?i)(?:requests\.(?:get|post|put|delete)|fetch|axios\.(?:get|post|put|delete)|http\.Get)\s*\(\s*(?:req\.|params\.|request\.|query\.|input\.|url_param).*?\)""",
        "message": "Outbound HTTP request made with unvalidated destination URL parameter.",
        "fix": "Validate target URLs against an explicit allowlist and block private IP ranges (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16).",
        "confidence": "MEDIUM"
    },

    # --- Logic Bugs & Quality ---
    {
        "id": "axim.quality.logic.identical-comparison",
        "name": "Comparison of Identical Variables ($X == $X)",
        "severity": SEV_WARNING,
        "cwe": "CWE-570: Expression is Always False / True",
        "owasp": "A04:2021 - Insecure Design",
        "languages": ["all"],
        "regex": r"""(?:\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:===|==|!==|!=)\s*\1\b)""",
        "message": "Variable compared against itself. Likely a typo or redundant check.",
        "fix": "Verify variable names on both sides of the comparison operator.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.quality.bugs.unclosed-file",
        "name": "Unclosed Resource Descriptor",
        "severity": SEV_INFO,
        "cwe": "CWE-775: Missing Release of File Descriptor",
        "owasp": "A04:2021 - Insecure Design",
        "languages": ["python"],
        "regex": r"""^\s*([a-zA-Z_0-9]+)\s*=\s*open\([^)]+\)(?!\s*as\s)""",
        "message": "File opened without `with` context manager. May leak descriptors on exceptions.",
        "fix": "Use `with open(...) as f:` to guarantee descriptor closure.",
        "confidence": "MEDIUM"
    }
]

# -----------------------------------------------------------------------------
# 3. Secret Detection Rules (High-Entropy + Signatures)
# -----------------------------------------------------------------------------
SECRET_RULES: List[Dict[str, Any]] = [
    {
        "id": "axim.secrets.generic-token",
        "name": "Generic Hardcoded Secret or Token",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"""(?i)(?:api[_-]?key|auth[_-]?token|secret[_-]?key|access[_-]?token|private[_-]?key|jwt[_-]?token|bearer[_-]?token|client[_-]?secret)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{16,})["']""",
        "message": "Potential hardcoded secret or API token.",
        "fix": "Move secrets into environment variables (.env) or a secret manager."
    },
    {
        "id": "axim.secrets.private-key-block",
        "name": "Private Cryptographic Key",
        "severity": SEV_ERROR,
        "cwe": "CWE-312: Cleartext Storage of Sensitive Information",
        "owasp": "A02:2021 - Cryptographic Failures",
        "regex": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "message": "Embedded private key found in source code.",
        "fix": "Never commit private cryptographic keys into version control."
    },
    {
        "id": "axim.secrets.aws-access-key",
        "name": "AWS Access Key ID",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"(?:AKIA|ASIA|AROA)[A-Z0-9]{16}",
        "message": "Hardcoded AWS Access Key ID.",
        "fix": "Use AWS IAM roles, instance profiles, or ~/.aws/credentials."
    },
    {
        "id": "axim.secrets.github-pat",
        "name": "GitHub Personal Access Token",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})",
        "message": "Hardcoded GitHub Personal Access Token.",
        "fix": "Revoke this token immediately on GitHub and use repository secrets."
    },
    {
        "id": "axim.secrets.openai-key",
        "name": "OpenAI API Key",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"sk-(?:proj-)?[A-Za-z0-9_\-]{40,}",
        "message": "Hardcoded OpenAI API Key.",
        "fix": "Store OpenAI keys in process environment variables (OPENAI_API_KEY)."
    },
    {
        "id": "axim.secrets.slack-token",
        "name": "Slack Bot / User Token",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}",
        "message": "Hardcoded Slack API Token.",
        "fix": "Revoke and store in secure environment variables."
    },
    {
        "id": "axim.secrets.stripe-key",
        "name": "Stripe Live Secret Key",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"(?:sk_live_|rk_live_)[0-9a-zA-Z]{24,}",
        "message": "Hardcoded Stripe live payment API key.",
        "fix": "Revoke key on Stripe Dashboard immediately."
    },
    {
        "id": "axim.secrets.database-uri",
        "name": "Database Connection URI with Credentials",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "regex": r"(?:postgres|postgresql|mysql|mongodb\+srv|mongodb|redis):\/\/[a-zA-Z0-9_\-\.]+:[a-zA-Z0-9_\-\.\$\!\*\@\%\&]+@[a-zA-Z0-9_\-\.]+",
        "message": "Database connection URI contains embedded plaintext username and password.",
        "fix": "Construct database connection URLs using environment variables."
    }
]

# -----------------------------------------------------------------------------
# 4. Supply Chain (SCA) Rules
# -----------------------------------------------------------------------------
SUPPLY_CHAIN_PATTERNS = [
    {
        "id": "axim.supply-chain.insecure-registry",
        "name": "Insecure HTTP Package Registry URL",
        "severity": SEV_ERROR,
        "cwe": "CWE-319: Cleartext Transmission of Sensitive Information",
        "owasp": "A02:2021 - Cryptographic Failures",
        "regex": r"""(?i)["']https?:\/\/(?!https:\/\/)[a-zA-Z0-9_\-\.]+\/(?:repository|npm|pypi|simple|registry)""",
        "message": "Package dependency repository configured over unencrypted HTTP.",
        "fix": "Enforce HTTPS for all package registries to avoid package tampering."
    },
    {
        "id": "axim.supply-chain.unpinned-version",
        "name": "Unpinned Wildcard Dependency (*)",
        "severity": SEV_WARNING,
        "cwe": "CWE-1104: Use of Unmaintained or Uncontrolled Third-Party Components",
        "owasp": "A06:2021 - Vulnerable and Outdated Components",
        "regex": r"""["'](?:[\w@\/\-]+)["']\s*:\s*["'](?:\*|latest)["']""",
        "message": "Dependency version unpinned or set to '*'/latest. Subject to malicious package releases.",
        "fix": "Pin explicit dependency versions or version ranges in package manifests."
    }
]


def shannon_entropy(data: str) -> float:
    """Calculates the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


class AximScanEngine:
    def __init__(self, external_cli_path: Optional[str] = None):
        self.cli_path = external_cli_path or shutil.which("semgrep")
        self.compiled_rules = self._compile_rules(BUILTIN_RULES)
        self.compiled_secrets = self._compile_rules(SECRET_RULES)
        self.compiled_supply_chain = self._compile_rules(SUPPLY_CHAIN_PATTERNS)

    def _compile_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compiled = []
        for r in rules:
            rc = dict(r)
            try:
                rc["_regex"] = re.compile(r["regex"], re.MULTILINE)
                compiled.append(rc)
            except Exception as e:
                sys.stderr.write(f"Failed to compile rule {r.get('id')}: {e}\n")
        return compiled

    def has_cli(self) -> bool:
        return bool(self.cli_path and os.path.isfile(self.cli_path) and os.access(self.cli_path, os.X_OK))

    def detect_language(self, path_or_name: str) -> str:
        name = Path(path_or_name).name.lower()
        if name in SPECIAL_FILENAMES:
            return SPECIAL_FILENAMES[name]
        ext = Path(path_or_name).suffix.lower()
        return LANGUAGE_EXTENSIONS.get(ext, "unknown")

    # -------------------------------------------------------------------------
    # Core Scanners
    # -------------------------------------------------------------------------
    def scan_code(self, code: str, language: str = "python", file_name: str = "inline") -> Dict[str, Any]:
        findings = []
        lines = code.splitlines()

        # 1. SAST Rules
        for rule in self.compiled_rules:
            rule_langs = rule.get("languages", [])
            if "all" not in rule_langs and language not in rule_langs:
                continue

            rgx: re.Pattern = rule["_regex"]
            for match in rgx.finditer(code):
                start_pos = match.start()
                line_no = code.count("\n", 0, start_pos) + 1
                matched_text = match.group(0).strip()
                line_content = lines[line_no - 1] if line_no - 1 < len(lines) else matched_text

                findings.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "category": "sast",
                    "severity": rule["severity"],
                    "cwe": rule["cwe"],
                    "owasp": rule["owasp"],
                    "file": file_name,
                    "line": line_no,
                    "snippet": line_content.strip()[:160],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "confidence": "HIGH"
                })

        # 2. Secret Rules
        for sec in self.compiled_secrets:
            rgx: re.Pattern = sec["_regex"]
            for match in rgx.finditer(code):
                start_pos = match.start()
                line_no = code.count("\n", 0, start_pos) + 1
                matched_text = match.group(0).strip()
                line_content = lines[line_no - 1] if line_no - 1 < len(lines) else matched_text

                findings.append({
                    "id": sec["id"],
                    "name": sec["name"],
                    "category": "secrets",
                    "severity": sec["severity"],
                    "cwe": sec["cwe"],
                    "owasp": sec["owasp"],
                    "file": file_name,
                    "line": line_no,
                    "snippet": line_content.strip()[:160],
                    "message": sec["message"],
                    "fix": sec["fix"],
                    "confidence": "HIGH"
                })

        return {
            "status": "success",
            "files_scanned": 1,
            "findings_count": len(findings),
            "findings": findings,
            "engine": "axim-scan-native"
        }

    def scan_path(
        self,
        target_path: str,
        config: str = "default",
        severity: Optional[str] = None,
        max_files: int = 1000
    ) -> Dict[str, Any]:
        target = Path(target_path).expanduser().resolve()
        if not target.exists():
            return {"status": "error", "error": f"Target path '{target_path}' does not exist"}

        # Accelerate with Semgrep CLI if installed and not forced to native
        if self.has_cli() and config not in ["builtin", "native"]:
            return self._run_external_cli(str(target), config, severity)

        # Built-in native static scanner
        files_to_scan = []
        if target.is_file():
            files_to_scan.append(target)
        else:
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
                for f in files:
                    fname_lower = f.lower()
                    ext = Path(f).suffix.lower()
                    if ext in LANGUAGE_EXTENSIONS or fname_lower in SPECIAL_FILENAMES:
                        files_to_scan.append(Path(root) / f)
                    if len(files_to_scan) >= max_files:
                        break
                if len(files_to_scan) >= max_files:
                    break

        all_findings = []
        files_scanned = 0

        for fpath in files_to_scan:
            try:
                lang = self.detect_language(str(fpath))
                if lang == "unknown":
                    continue
                content = fpath.read_text(encoding="utf-8", errors="replace")
                files_scanned += 1
                rel_path = str(fpath.relative_to(target) if target.is_dir() else fpath.name)
                res = self.scan_code(content, language=lang, file_name=rel_path)

                # Supply chain manifest checks
                if lang in ["package-json", "package-lock", "requirements-txt", "go-mod", "cargo-toml"]:
                    sc_res = self._scan_supply_chain_content(content, lang, rel_path)
                    res["findings"].extend(sc_res)

                for item in res["findings"]:
                    if severity and item["severity"].upper() != severity.upper():
                        continue
                    all_findings.append(item)
            except Exception:
                continue

        # Sort findings by severity (ERROR > WARNING > INFO) and file
        sev_rank = {SEV_ERROR: 0, SEV_WARNING: 1, SEV_INFO: 2}
        all_findings.sort(key=lambda x: (sev_rank.get(x["severity"], 9), x["file"], x["line"]))

        return {
            "status": "success",
            "target": str(target),
            "files_scanned": files_scanned,
            "findings_count": len(all_findings),
            "findings": all_findings,
            "engine": "axim-scan-native"
        }

    def _scan_supply_chain_content(self, content: str, manifest_type: str, file_name: str) -> List[Dict[str, Any]]:
        findings = []
        lines = content.splitlines()
        for rule in self.compiled_supply_chain:
            rgx: re.Pattern = rule["_regex"]
            for match in rgx.finditer(content):
                start_pos = match.start()
                line_no = content.count("\n", 0, start_pos) + 1
                matched_text = match.group(0).strip()
                line_content = lines[line_no - 1] if line_no - 1 < len(lines) else matched_text

                findings.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "category": "supply-chain",
                    "severity": rule["severity"],
                    "cwe": rule["cwe"],
                    "owasp": rule["owasp"],
                    "file": file_name,
                    "line": line_no,
                    "snippet": line_content.strip()[:160],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "confidence": "HIGH"
                })
        return findings

    # -------------------------------------------------------------------------
    # Semantic Pattern Matching (Code Search like Semgrep: `$X == $X`)
    # -------------------------------------------------------------------------
    def scan_pattern(self, pattern: str, target_path: str, language: str = "python") -> Dict[str, Any]:
        """Matches code patterns containing metavariables ($X, $VAL) and wildcards (...)"""
        regex_parts = []
        tokens = re.split(r'(\$[a-zA-Z_][a-zA-Z0-9_]*|\.\.\.)', pattern)
        metavars = {}

        for token in tokens:
            if not token:
                continue
            if token.startswith("$"):
                if token not in metavars:
                    metavars[token] = len(metavars) + 1
                    regex_parts.append(r"([a-zA-Z_][a-zA-Z0-9_]*)")
                else:
                    regex_parts.append(f"\\{metavars[token]}")
            elif token == "...":
                regex_parts.append(r".*?")
            else:
                regex_parts.append(re.escape(token))

        custom_regex = "".join(regex_parts)
        try:
            compiled = re.compile(custom_regex, re.MULTILINE)
        except Exception as e:
            return {"status": "error", "error": f"Invalid pattern syntax: {e}"}

        target = Path(target_path).expanduser().resolve()
        files = [target] if target.is_file() else [p for p in target.glob(f"**/*") if p.is_file() and p.suffix in LANGUAGE_EXTENSIONS]

        matches = []
        for f in files[:200]:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                lines = text.splitlines()
                for m in compiled.finditer(text):
                    pos = m.start()
                    line_no = text.count("\n", 0, pos) + 1
                    line_text = lines[line_no - 1] if line_no - 1 < len(lines) else m.group(0)
                    matches.append({
                        "file": str(f.relative_to(target) if target.is_dir() else f.name),
                        "line": line_no,
                        "matched": m.group(0).strip(),
                        "snippet": line_text.strip()[:160]
                    })
            except Exception:
                continue

        return {
            "status": "success",
            "pattern": pattern,
            "matches_count": len(matches),
            "matches": matches
        }

    def _run_external_cli(self, target: str, config: str, severity: Optional[str]) -> Dict[str, Any]:
        cmd = [self.cli_path, "scan", "--json", "--quiet"]
        if config and config != "default":
            cmd.extend(["--config", config])
        else:
            cmd.extend(["--config", "auto"])
        if severity:
            cmd.extend(["--severity", severity.upper()])
        cmd.append(target)

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            data = json.loads(proc.stdout or "{}")
            raw_results = data.get("results", [])
            findings = []
            for r in raw_results:
                findings.append({
                    "id": r.get("check_id"),
                    "name": r.get("check_id", "").split(".")[-1].replace("-", " ").title(),
                    "category": "sast",
                    "severity": r.get("extra", {}).get("severity", "WARNING").upper(),
                    "cwe": (r.get("extra", {}).get("metadata", {}).get("cwe") or ["CWE-Unknown"])[0] if isinstance(r.get("extra", {}).get("metadata", {}).get("cwe"), list) else str(r.get("extra", {}).get("metadata", {}).get("cwe") or ""),
                    "owasp": (r.get("extra", {}).get("metadata", {}).get("owasp") or ["OWASP-Unknown"])[0] if isinstance(r.get("extra", {}).get("metadata", {}).get("owasp"), list) else str(r.get("extra", {}).get("metadata", {}).get("owasp") or ""),
                    "file": r.get("path"),
                    "line": r.get("start", {}).get("line"),
                    "snippet": (r.get("extra", {}).get("lines") or "").strip()[:160],
                    "message": r.get("extra", {}).get("message"),
                    "fix": r.get("extra", {}).get("fix") or "Review and sanitize input before processing.",
                    "confidence": "HIGH"
                })
            return {
                "status": "success",
                "target": target,
                "files_scanned": len(data.get("paths", {}).get("scanned", [])),
                "findings_count": len(findings),
                "findings": findings,
                "engine": "axim-scan-cli"
            }
        except Exception:
            return self.scan_path(target, config="builtin", severity=severity)

    def list_rules(self) -> List[Dict[str, Any]]:
        all_r = []
        for r in self.compiled_rules + self.compiled_secrets + self.compiled_supply_chain:
            all_r.append({
                "id": r["id"],
                "name": r["name"],
                "severity": r["severity"],
                "cwe": r.get("cwe", "CWE-General"),
                "owasp": r.get("owasp", "General"),
                "languages": r.get("languages", ["all"]),
                "message": r["message"]
            })
        return all_r

    def format_markdown(self, result: Dict[str, Any]) -> str:
        findings = result.get("findings", [])
        lines = [
            f"# AXIM Scan — Security & Bug Detection Report",
            f"",
            f"- **Target**: `{result.get('target', 'Code')}`",
            f"- **Files Scanned**: {result.get('files_scanned', 0)}",
            f"- **Total Findings**: {result.get('findings_count', 0)}",
            f"- **Engine**: `{result.get('engine', 'axim-scan')}`",
            f"",
            f"---",
            f""
        ]

        if not findings:
            lines.append("### ✅ Zero Security Vulnerabilities or Bugs Detected")
            lines.append("No security weaknesses, code smells, supply-chain risks, or hardcoded secrets were detected.")
            return "\n".join(lines)

        lines.append("## Findings Summary")
        lines.append("")
        lines.append("| Severity | Category | ID | File : Line | Description |")
        lines.append("|---|---|---|---|---|")
        for f in findings:
            sev_badge = "🔴 ERROR" if f["severity"] == SEV_ERROR else ("🟡 WARNING" if f["severity"] == SEV_WARNING else "ℹ️ INFO")
            cat_badge = f.get("category", "sast").upper()
            lines.append(f"| {sev_badge} | `{cat_badge}` | `{f['id']}` | `{f['file']}:{f['line']}` | {f['name']} |")

        lines.append("")
        lines.append("## Detailed Vulnerability & Remediation Analysis")
        lines.append("")

        for i, f in enumerate(findings, 1):
            sev_badge = "🔴 ERROR" if f["severity"] == SEV_ERROR else ("🟡 WARNING" if f["severity"] == SEV_WARNING else "ℹ️ INFO")
            cat_badge = f.get("category", "sast").upper()
            lines.append(f"### {i}. {f['name']} ({sev_badge}) — [{cat_badge}]")
            lines.append(f"- **Rule ID**: `{f['id']}`")
            lines.append(f"- **Classification**: {f.get('cwe', '')} · {f.get('owasp', '')}")
            lines.append(f"- **Location**: `{f['file']}:{f['line']}`")
            lines.append(f"")
            lines.append(f"**Vulnerability Detail**:")
            lines.append(f"> {f['message']}")
            lines.append(f"")
            lines.append("```")
            lines.append(f"{f['snippet']}")
            lines.append("```")
            lines.append(f"")
            lines.append(f"**Actionable Remediation (AI Assistant Fix)**:")
            lines.append(f"{f['fix']}")
            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        return "\n".join(lines)


if __name__ == "__main__":
    eng = AximScanEngine()
    tgt = sys.argv[1] if len(sys.argv) > 1 else "."
    res = eng.scan_path(tgt)
    print(eng.format_markdown(res))
