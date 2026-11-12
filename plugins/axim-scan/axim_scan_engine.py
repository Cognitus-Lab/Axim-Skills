#!/usr/bin/env python3
"""
axim_scan_engine.py — Core Security & Bug Detection Engine for AXIM & Berry.
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills

Provides multi-language static application security testing (SAST), code quality auditing,
and secret detection. Runs self-contained with pure Python standard library rules, and
automatically integrates with external AST engines (such as Semgrep) when available.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Severity levels
SEV_ERROR = "ERROR"
SEV_WARNING = "WARNING"
SEV_INFO = "INFO"

# Built-in curated security rule definitions
BUILTIN_RULES: List[Dict[str, Any]] = [
    # 1. Hardcoded Secrets & Credentials
    {
        "id": "axim.security.secrets.hardcoded-token",
        "name": "Hardcoded Secret / Token",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Use of Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "languages": ["python", "javascript", "typescript", "go", "java", "ruby", "php", "swift", "rust", "json", "yaml"],
        "regex": r"""(?i)(?:api[_-]?key|auth[_-]?token|secret[_-]?key|access[_-]?token|private[_-]?key|jwt[_-]?token|bearer[_-]?token|client[_-]?secret)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{16,})["']""",
        "message": "Potential hardcoded secret or API credential detected in source code.",
        "fix": "Move secret credentials out of source code into environment variables or a secret vault.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.secrets.private-key",
        "name": "Hardcoded Private Key Block",
        "severity": SEV_ERROR,
        "cwe": "CWE-312: Cleartext Storage of Sensitive Information",
        "owasp": "A02:2021 - Cryptographic Failures",
        "languages": ["all"],
        "regex": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "message": "Embedded private key found in source file.",
        "fix": "Never commit private cryptographic keys into version control. Store keys in secure key management services (KMS).",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.secrets.aws-access-key",
        "name": "Hardcoded AWS Access Key",
        "severity": SEV_ERROR,
        "cwe": "CWE-798: Use of Hard-coded Credentials",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "languages": ["all"],
        "regex": r"(?:AKIA|ASIA|AROA)[A-Z0-9]{16}",
        "message": "Hardcoded AWS IAM Access Key ID detected.",
        "fix": "Use AWS IAM roles, instance profiles, or ~/.aws/credentials instead of committing access keys.",
        "confidence": "HIGH"
    },

    # 2. Injection Vulnerabilities (SQL, Command, Code)
    {
        "id": "axim.security.injection.sql-string-concat",
        "name": "SQL Injection via String Formatting",
        "severity": SEV_ERROR,
        "cwe": "CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "go", "java", "php", "ruby"],
        "regex": r"""(?i)(?:execute|query|raw|cursor\.execute)\s*\(\s*(?:f["'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?\{|["'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?["']\s*\+|`.*?(?:SELECT|INSERT|UPDATE|DELETE|DROP).*?\$\{)""",
        "message": "SQL query formed by dynamic string concatenation or interpolation. Vulnerable to SQL Injection.",
        "fix": "Use parameterized queries, prepared statements, or ORM parameter binding (e.g., `execute('SELECT * FROM users WHERE id = %s', (user_id,))`).",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.injection.command-injection",
        "name": "Command Injection via Shell Execution",
        "severity": SEV_ERROR,
        "cwe": "CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "go", "ruby", "php"],
        "regex": r"""(?i)(?:os\.system|child_process\.exec|execSync|subprocess\.(?:Popen|run|call)\(.*?\bshell\s*=\s*True|runtime\.exec)\s*\(""",
        "message": "Direct OS shell execution with potential untrusted input concatenation.",
        "fix": "Avoid shell=True. Pass arguments as a discrete list: `subprocess.run(['command', arg1, arg2], shell=False)`.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.injection.code-eval",
        "name": "Arbitrary Code Execution via eval()",
        "severity": SEV_ERROR,
        "cwe": "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')",
        "owasp": "A03:2021 - Injection",
        "languages": ["python", "javascript", "typescript", "php", "ruby"],
        "regex": r"""(?i)(?<![\w\.])(?:eval|exec)\s*\([^)]+""",
        "message": "Dynamic code evaluation via eval() or exec(). Callers can execute arbitrary instructions.",
        "fix": "Avoid eval() entirely. Use strict parsers (e.g., `json.loads()` or `ast.literal_eval()` in Python).",
        "confidence": "HIGH"
    },

    # 3. Cross-Site Scripting (XSS)
    {
        "id": "axim.security.xss.inner-html",
        "name": "Cross-Site Scripting (XSS) via innerHTML / unescaped HTML sink",
        "severity": SEV_ERROR,
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "owasp": "A03:2021 - Injection",
        "languages": ["javascript", "typescript"],
        "regex": r"""(?:\.innerHTML\s*=\s*|dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:)\s*[^"'`\s]""",
        "message": "Direct assignment to innerHTML or dangerouslySetInnerHTML with unvalidated content.",
        "fix": "Use textContent, innerText, or sanitize HTML via DOMPurify before rendering.",
        "confidence": "HIGH"
    },

    # 4. Path Traversal & Insecure File Access
    {
        "id": "axim.security.path-traversal.arbitrary-file",
        "name": "Path Traversal / Arbitrary File Access",
        "severity": SEV_WARNING,
        "cwe": "CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
        "owasp": "A01:2021 - Broken Access Control",
        "languages": ["python", "javascript", "typescript", "go"],
        "regex": r"""(?i)(?:open|readFile|createReadStream)\s*\(\s*(?:req\.|params\.|request\.|query\.|input\.|f["'].*?\{.*?path).*?\)""",
        "message": "File system access using directly formatted or untrusted path parameters.",
        "fix": "Validate and resolve target paths within an authorized base directory using `os.path.realpath` or `path.resolve` and verify `path.startswith(base_dir)`.",
        "confidence": "MEDIUM"
    },

    # 5. Broken Cryptography & Insecure Communication
    {
        "id": "axim.security.crypto.insecure-hash",
        "name": "Weak / Broken Hash Algorithm (MD5 / SHA1)",
        "severity": SEV_WARNING,
        "cwe": "CWE-328: Use of Weak Hash",
        "owasp": "A02:2021 - Cryptographic Failures",
        "languages": ["python", "javascript", "typescript", "go", "java"],
        "regex": r"""(?i)(?:hashlib\.md5|hashlib\.sha1|crypto\.createHash\s*\(\s*["'](?:md5|sha1)["']|MessageDigest\.getInstance\s*\(\s*["'](?:MD5|SHA-1)["']\))""",
        "message": "Insecure cryptographic hashing algorithm (MD5 or SHA1). Vulnerable to collision attacks.",
        "fix": "Use SHA-256 (`hashlib.sha256`), SHA-512, or bcrypt/argon2 for password hashing.",
        "confidence": "HIGH"
    },
    {
        "id": "axim.security.network.disabled-tls-verify",
        "name": "Disabled SSL/TLS Certificate Verification",
        "severity": SEV_ERROR,
        "cwe": "CWE-295: Improper Certificate Validation",
        "owasp": "A02:2021 - Cryptographic Failures",
        "languages": ["python", "javascript", "typescript", "go"],
        "regex": r"""(?i)(?:\bverify\s*=\s*False\b|\brejectUnauthorized\s*:\s*false\b|\bInsecureSkipVerify\s*:\s*true\b)""",
        "message": "SSL/TLS certificate verification explicitly disabled. Allows Man-In-The-Middle (MITM) attacks.",
        "fix": "Enable SSL verification (`verify=True`, `rejectUnauthorized: true`). Provide custom trusted CA certificates if internal roots are needed.",
        "confidence": "HIGH"
    },

    # 6. Insecure Deserialization
    {
        "id": "axim.security.deserialization.pickle-load",
        "name": "Insecure Deserialization via Python pickle",
        "severity": SEV_ERROR,
        "cwe": "CWE-502: Deserialization of Untrusted Data",
        "owasp": "A08:2021 - Software and Data Integrity Failures",
        "languages": ["python"],
        "regex": r"""(?i)(?:pickle|cPickle|_pickle)\.(?:load|loads)\s*\(""",
        "message": "Deserialization of data with pickle is inherently unsafe and can execute arbitrary Python bytecode.",
        "fix": "Use safe serialization formats like JSON, MessagePack, or Protocol Buffers.",
        "confidence": "HIGH"
    },

    # 7. Server-Side Request Forgery (SSRF)
    {
        "id": "axim.security.ssrf.unvalidated-request",
        "name": "Potential Server-Side Request Forgery (SSRF)",
        "severity": SEV_WARNING,
        "cwe": "CWE-918: Server-Side Request Forgery (SSRF)",
        "owasp": "A10:2021 - Server-Side Request Forgery (SSRF)",
        "languages": ["python", "javascript", "typescript", "go"],
        "regex": r"""(?i)(?:requests\.(?:get|post|put|delete)|fetch|axios\.(?:get|post|put|delete)|http\.Get)\s*\(\s*(?:req\.|params\.|request\.|query\.|input\.|url_param).*?\)""",
        "message": "Outbound HTTP request made with unvalidated user-supplied destination URL.",
        "fix": "Validate target URLs against an explicit allowlist and restrict requests to private IP ranges (127.0.0.1, 10.0.0.0/8, 192.168.0.0/16).",
        "confidence": "MEDIUM"
    },

    # 8. Memory & Concurrency Bugs
    {
        "id": "axim.quality.bugs.unclosed-resource",
        "name": "Unclosed Resource / Missing Context Manager",
        "severity": SEV_INFO,
        "cwe": "CWE-775: Missing Release of File Descriptor or Handle after Effective Lifetime",
        "owasp": "A04:2021 - Insecure Design",
        "languages": ["python"],
        "regex": r"""^\s*([a-zA-Z_0-9]+)\s*=\s*open\([^)]+\)(?!\s*as\s)""",
        "message": "File opened without `with` context manager. May leak file descriptors on exceptions.",
        "fix": "Use `with open(...) as f:` to guarantee proper descriptor cleanup.",
        "confidence": "MEDIUM"
    }
]

EXT_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".java": "java",
    ".swift": "swift",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "shell",
    ".bash": "shell"
}

IGNORED_DIRS = {
    ".git", ".svn", "node_modules", "DerivedData", ".build", "dist",
    "build", "venv", ".venv", "env", "__pycache__", ".next", ".cache",
    ".idea", ".vscode", "coverage"
}


class AximScanEngine:
    def __init__(self, external_cli_path: Optional[str] = None):
        self.cli_path = external_cli_path or shutil.which("semgrep")
        self.compiled_rules = self._compile_rules(BUILTIN_RULES)

    def _compile_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compiled = []
        for r in rules:
            rule_copy = dict(r)
            try:
                rule_copy["_regex"] = re.compile(r["regex"], re.MULTILINE)
                compiled.append(rule_copy)
            except Exception as e:
                sys.stderr.write(f"Failed to compile rule {r.get('id')}: {e}\n")
        return compiled

    def has_cli(self) -> bool:
        return bool(self.cli_path and os.path.isfile(self.cli_path) and os.access(self.cli_path, os.X_OK))

    def detect_language(self, path_or_name: str) -> str:
        ext = Path(path_or_name).suffix.lower()
        return EXT_MAP.get(ext, "unknown")

    def scan_code(self, code: str, language: str = "python", file_name: str = "inline") -> Dict[str, Any]:
        findings = []
        lines = code.splitlines()

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
                    "severity": rule["severity"],
                    "cwe": rule["cwe"],
                    "owasp": rule["owasp"],
                    "file": file_name,
                    "line": line_no,
                    "snippet": line_content.strip()[:160],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "confidence": rule["confidence"]
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
        max_files: int = 500
    ) -> Dict[str, Any]:
        target = Path(target_path).expanduser().resolve()
        if not target.exists():
            return {"status": "error", "error": f"Target path '{target_path}' does not exist"}

        # If external AST CLI is installed and user requested enterprise rule pack
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
                    ext = Path(f).suffix.lower()
                    if ext in EXT_MAP:
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
                res = self.scan_code(content, language=lang, file_name=str(fpath.relative_to(target) if target.is_dir() else fpath.name))
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
        rules = []
        for r in BUILTIN_RULES:
            rules.append({
                "id": r["id"],
                "name": r["name"],
                "severity": r["severity"],
                "cwe": r["cwe"],
                "owasp": r["owasp"],
                "languages": r["languages"],
                "message": r["message"]
            })
        return rules

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
            lines.append("No security weaknesses, code smells, or hardcoded secrets were detected in the scanned files.")
            return "\n".join(lines)

        lines.append("## Findings Summary")
        lines.append("")
        lines.append("| Severity | ID | File : Line | Description |")
        lines.append("|---|---|---|---|")
        for f in findings:
            sev_badge = "🔴 ERROR" if f["severity"] == SEV_ERROR else ("🟡 WARNING" if f["severity"] == SEV_WARNING else "ℹ️ INFO")
            lines.append(f"| {sev_badge} | `{f['id']}` | `{f['file']}:{f['line']}` | {f['name']} |")

        lines.append("")
        lines.append("## Detailed Vulnerability Analysis")
        lines.append("")

        for i, f in enumerate(findings, 1):
            sev_badge = "🔴 ERROR" if f["severity"] == SEV_ERROR else ("🟡 WARNING" if f["severity"] == SEV_WARNING else "ℹ️ INFO")
            lines.append(f"### {i}. {f['name']} ({sev_badge})")
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
            lines.append(f"**Remediation Recommendation**:")
            lines.append(f"{f['fix']}")
            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        return "\n".join(lines)


if __name__ == "__main__":
    engine = AximScanEngine()
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    res = engine.scan_path(target)
    print(engine.format_markdown(res))
