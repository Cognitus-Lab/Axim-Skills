#!/usr/bin/env python3
"""
Vercel serverless function endpoint for AXIM Scan API.
POST /api/scan
Body: {"code": "...", "language": "python", "format": "json"}
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Add current dir and parent directories so axim_scan_engine is accessible
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PARENT_DIR))

try:
    from axim_scan_engine import AximScanEngine
except ImportError:
    sys.path.insert(0, str(PARENT_DIR.parent))
    from axim_scan_engine import AximScanEngine

engine = AximScanEngine()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        rules = engine.list_rules()
        self.wfile.write(json.dumps({
            "service": "AXIM Scan Cloud API",
            "status": "online",
            "author": "Cognitus",
            "rules_count": len(rules)
        }).encode("utf-8"))

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len)

        try:
            req_data = json.loads(post_body.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON body"}).encode("utf-8"))
            return

        code = req_data.get("code", "")
        language = req_data.get("language", "python")
        output_format = req_data.get("format", "json")

        result = engine.scan_code(code, language=language)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")

        if output_format == "markdown":
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.end_headers()
            self.wfile.write(engine.format_markdown(result).encode("utf-8"))
        else:
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode("utf-8"))
