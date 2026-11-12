#!/usr/bin/env python3
"""
deploy_vercel.py — Zero-dependency direct deployer to Vercel via the Vercel REST API (v13).
Author: Cognitus
Repository: https://github.com/Cognitus-Lab/Axim-Skills

Deploys the AXIM Scan web app and serverless function directly to Vercel without requiring
the npm 'vercel' CLI or any external dependencies.

Usage:
    export VERCEL_TOKEN="your_token_here"
    python3 deploy_vercel.py

Or:
    python3 deploy_vercel.py --token "your_token_here"
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = WEB_DIR.parent
ENGINE_FILE = PLUGIN_DIR / "axim_scan_engine.py"

VERCEL_API_URL = "https://api.vercel.com/v13/deployments"


def deploy_to_vercel(token: str, project_name: str = "axim-scan", team_id: str = None) -> dict:
    # 1. Gather all files in web directory + engine file
    files_payload = []

    # Include axim_scan_engine.py into api/ so Vercel Python runtime imports it cleanly
    if ENGINE_FILE.exists():
        files_payload.append({
            "file": "api/axim_scan_engine.py",
            "data": ENGINE_FILE.read_text(encoding="utf-8")
        })

    for root, _, files in os.walk(WEB_DIR):
        for f in files:
            fpath = Path(root) / f
            rel = str(fpath.relative_to(WEB_DIR))
            # Skip python cache and deployment scripts
            if "__pycache__" in rel or rel.endswith(".pyc") or f == "deploy_vercel.py":
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                files_payload.append({
                    "file": rel,
                    "data": content
                })
            except Exception:
                continue

    req_body = {
        "name": project_name,
        "files": files_payload,
        "target": "production",
        "projectSettings": {
            "framework": None
        }
    }

    url = f"{VERCEL_API_URL}?teamId={team_id}" if team_id else VERCEL_API_URL
    req_data = json.dumps(req_body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Authorization": f"Bearer {token.strip()}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            deployment_url = resp_data.get("url")
            print(f"✅ Successfully deployed to Vercel!")
            print(f"🔗 Live URL: https://{deployment_url}")
            print(f"📊 Deployment ID: {resp_data.get('id')}")
            return resp_data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"❌ Vercel API Error ({e.code}): {err_msg}", file=sys.stderr)
        return {"error": err_msg, "code": e.code}
    except Exception as e:
        print(f"❌ Deployment failed: {e}", file=sys.stderr)
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Deploy AXIM Scan to Vercel directly via REST API.")
    parser.add_argument("--token", help="Vercel Access Token (or set VERCEL_TOKEN env var)")
    parser.add_argument("--project", default="axim-scan", help="Vercel project name (default: axim-scan)")
    parser.add_argument("--team", default="team_RxsLJNF5AWfkPshG4Yn9yPeu", help="Vercel team ID")
    args = parser.parse_args()

    token = args.token or os.environ.get("VERCEL_TOKEN")
    if not token:
        print("Error: No Vercel token provided. Provide via --token <token> or set VERCEL_TOKEN in environment.", file=sys.stderr)
        sys.exit(1)

    deploy_to_vercel(token, args.project, args.team)


if __name__ == "__main__":
    main()
