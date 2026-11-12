# AXIM Scan Plugin for AXIM & Berry
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills

The `axim-scan` plugin brings automated static application security testing (SAST), code vulnerability auditing, and bug detection to AXIM and Berry agents.

---

## Features

- **OWASP Top 10** vulnerabilities (SQL Injection, Command Injection, XSS, SSRF, Broken Access Control)
- **CWE Vulnerabilities** (Hardcoded credentials, path traversal, insecure cryptography, deserialization)
- **Hardcoded Secrets & API Keys** (AWS tokens, JWTs, private keys, bearer tokens)
- **Code Quality & Resource Leaks** (Unclosed handles, dangling descriptors, insecure configurations)
- **Remediation & Auto-Fix Guidance** for every detected vulnerability

---

## MCP Server Configuration

Connect directly to `axim-scan` as a standalone MCP server in your `mcp.json`:

```json
{
  "mcpServers": {
    "axim-scan": {
      "command": "python3",
      "args": ["/path/to/Axim-Skills/plugins/axim-scan/mcp_server.py"]
    }
  }
}
```

Or connect via the root `Axim-Skills` MCP server:
```json
{
  "mcpServers": {
    "axim-skills": {
      "command": "python3",
      "args": ["/path/to/Axim-Skills/mcp_server.py"]
    }
  }
}
```

---

## Cloud & Vercel Deployment

The `web/` directory includes a Vercel-ready serverless API endpoint (`web/api/scan.py`) and a web UI (`web/public/index.html`) that can be deployed directly to Vercel.
