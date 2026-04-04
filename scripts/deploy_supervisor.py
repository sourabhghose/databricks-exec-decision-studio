#!/usr/bin/env python3
"""
Automates the full supervisor agent deployment pipeline via DABs:
  1. databricks bundle deploy  (deploy jobs + infra, skip endpoint if model missing)
  2. databricks bundle run eds_supervisor_pipeline_job  (02 RAG → 03 Agents, registers model)
  3. databricks bundle deploy  (now model exists → creates eds-supervisor endpoint)
  4. Rebuild frontend + sync backend + deploy app

Usage:
  python3 scripts/deploy_supervisor.py [--skip-jobs] [--skip-app]

Requires: databricks CLI authenticated as fe-vm-ausnet-process-intel
"""

import argparse
import subprocess
import sys
import time

PROFILE = "fe-vm-ausnet-process-intel"
WORKSPACE = "https://fevm-ausnet-process-intel.cloud.databricks.com"
APP_NAME = "exec-decision-studio"
APP_SOURCE = f"/Workspace/Users/sourabh.ghose@databricks.com/{APP_NAME}"

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True
).stdout.strip() or "."

CATALOG = "ausnet_process_intel_catalog"
MODEL_NAME = f"{CATALOG}.eds_agents.rag_chain"
ENDPOINT_NAME = "eds-supervisor"


# ── Helpers ────────────────────────────────────────────────────────────────────

def run(cmd: list[str], cwd: str = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
    if result.returncode != 0:
        if result.stderr:
            for line in result.stderr.strip().splitlines():
                print(f"    [stderr] {line}")
        if check:
            print(f"\n  ✗ Command failed (exit {result.returncode})")
            sys.exit(1)
    return result


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"▶  {title}")


# ── Steps ──────────────────────────────────────────────────────────────────────

def bundle_deploy():
    """Run databricks bundle deploy (dev target — jobs only, no serving endpoint)."""
    cmd = ["databricks", "bundle", "deploy", "--target", "dev", "--profile", PROFILE]
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    for line in output.splitlines():
        print(f"    {line}")
    if result.returncode != 0:
        print(f"\n  ✗ bundle deploy failed")
        sys.exit(1)
    return True


def get_token() -> str:
    result = subprocess.run(
        ["databricks", "auth", "token", "--profile", PROFILE],
        capture_output=True, text=True, check=True
    )
    import json as _json
    return _json.loads(result.stdout)["access_token"]


def api_get(token: str, path: str) -> dict:
    import urllib.request
    req = urllib.request.Request(
        f"{WORKSPACE}{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        import json as _json
        return _json.loads(resp.read())


def api_post(token: str, path: str, body: dict) -> dict:
    import urllib.request, json as _json
    req = urllib.request.Request(
        f"{WORKSPACE}{path}",
        data=_json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return _json.loads(resp.read())


def api_put(token: str, path: str, body: dict) -> dict:
    import urllib.request, json as _json
    req = urllib.request.Request(
        f"{WORKSPACE}{path}",
        data=_json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return _json.loads(resp.read())


def get_latest_model_version(token: str) -> str | None:
    try:
        resp = api_get(token, f"/api/2.1/unity-catalog/models/{MODEL_NAME}/versions?max_results=10")
        versions = resp.get("model_versions", [])
        if not versions:
            return None
        return str(max(int(v["version"]) for v in versions))
    except Exception as e:
        print(f"  ✗ Could not fetch model version: {e}")
        return None


def create_or_update_endpoint(token: str, model_version: str) -> bool:
    section(f"Creating/updating serving endpoint: {ENDPOINT_NAME} (model v{model_version})")
    served_entity = {
        "name": ENDPOINT_NAME,
        "entity_name": MODEL_NAME,
        "entity_version": model_version,
        "scale_to_zero_enabled": True,
        "workload_size": "Small",
    }
    try:
        api_get(token, f"/api/2.0/serving-endpoints/{ENDPOINT_NAME}")
        # Exists — update
        api_put(token, f"/api/2.0/serving-endpoints/{ENDPOINT_NAME}/config",
                {"served_entities": [served_entity]})
        print("  ✓ Endpoint updated")
    except Exception:
        # Create new
        api_post(token, "/api/2.0/serving-endpoints", {
            "name": ENDPOINT_NAME,
            "config": {"served_entities": [served_entity]},
        })
        print("  ✓ Endpoint created (warming up ~5-10 min)")
    return True


def run_pipeline_job():
    """Run the [EDS] 04 supervisor pipeline job and wait for completion."""
    section("Running [EDS] 04 - Deploy Supervisor Pipeline")
    print("  This runs jobs 02 (RAG Chain) → 03 (Deploy Agents) in sequence.")
    print("  Estimated time: 20-40 minutes\n")
    # --no-wait lets us stream output; without it the CLI blocks until done
    run([
        "databricks", "bundle", "run",
        "eds_supervisor_pipeline_job",
        "--profile", PROFILE,
    ])
    print("  ✓ Pipeline job completed")


def deploy_app():
    """Build frontend, sync backend, upload dist, deploy app."""
    import os
    app_dir = f"{ROOT}/app"
    frontend_dir = f"{app_dir}/frontend"

    section("Building & deploying app")

    print("  Building frontend...")
    run(["npm", "run", "build"], cwd=frontend_dir)
    print("  ✓ Frontend built")

    print("  Syncing backend to workspace...")
    run([
        "databricks", "sync", app_dir, APP_SOURCE,
        "--profile", PROFILE,
        "--exclude", "frontend/node_modules",
        "--exclude", "frontend/src",
        "--exclude", "frontend/public",
        "--exclude", "frontend/.vite",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
    ])
    print("  ✓ Backend synced")

    print("  Uploading frontend/dist...")
    run([
        "databricks", "workspace", "import-dir",
        f"{frontend_dir}/dist",
        f"{APP_SOURCE}/frontend/dist",
        "--profile", PROFILE,
        "--overwrite",
    ])
    print("  ✓ Frontend dist uploaded")

    print("  Deploying Databricks App...")
    run([
        "databricks", "apps", "deploy", APP_NAME,
        "--source-code-path", APP_SOURCE,
        "--profile", PROFILE,
    ])
    print("  ✓ App deployed")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Deploy EDS supervisor agent end-to-end via DABs")
    parser.add_argument("--skip-jobs", action="store_true",
                        help="Skip running the pipeline job (02+03 already ran, model already registered)")
    parser.add_argument("--skip-app", action="store_true",
                        help="Skip frontend build and app deploy")
    args = parser.parse_args()

    print("=" * 60)
    print("  EDS Supervisor Agent — Automated Deployment (via DABs)")
    print("=" * 60)

    print("\n▶  Fetching auth token...")
    token = get_token()
    print("  ✓ Authenticated")

    # Step 1: Bundle deploy (creates/updates jobs)
    section("Step 1/4 — bundle deploy (jobs)")
    bundle_deploy()

    if not args.skip_jobs:
        # Step 2: Run pipeline job (02 RAG → 03 Agents), registers rag_chain model in UC
        section("Step 2/4 — Run supervisor pipeline job (02 → 03)")
        run_pipeline_job()
    else:
        print("\n  (skipping pipeline job)")

    # Step 3: Create/update serving endpoint via REST API (dynamic version)
    section("Step 3/4 — Serving endpoint")
    version = get_latest_model_version(token)
    if not version:
        print(f"  ✗ Model {MODEL_NAME} not found in registry. Run without --skip-jobs first.")
        sys.exit(1)
    print(f"  Found model version: {version}")
    create_or_update_endpoint(token, version)

    # Step 4: Build and deploy the app
    if not args.skip_app:
        section("Step 4/4 — App deploy")
        deploy_app()
    else:
        print("\n  (skipping app deploy)")

    print(f"\n{'='*60}")
    print("  ✓ All done!")
    print(f"  Endpoint: {WORKSPACE}/serving-endpoints/eds-supervisor")
    print(f"  App logs: databricks apps logs {APP_NAME} --profile {PROFILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
