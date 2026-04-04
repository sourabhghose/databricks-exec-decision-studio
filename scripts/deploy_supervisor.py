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

def bundle_deploy(ignore_errors: bool = False, target: str = "dev"):
    """Run databricks bundle deploy. Optionally ignore failures (e.g. model not registered yet)."""
    cmd = ["databricks", "bundle", "deploy", "--target", target, "--profile", PROFILE]
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    for line in output.splitlines():
        print(f"    {line}")

    if result.returncode != 0:
        if ignore_errors and "does not exist" in output:
            print("  ⚠  Endpoint skipped (model not registered yet — expected on first run)")
            return False
        print(f"\n  ✗ bundle deploy failed")
        sys.exit(1)
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

    # Step 1: Initial bundle deploy (creates jobs; endpoint may fail if model missing)
    section("Step 1/4 — bundle deploy (initial)")
    if args.skip_jobs:
        # Model already registered — deploy with-serving target to create/update endpoint
        bundle_deploy(ignore_errors=False, target="with-serving")
    else:
        # First time — deploy dev target only (no endpoint, model not registered yet)
        bundle_deploy(ignore_errors=False, target="dev")

    if not args.skip_jobs:
        # Step 2: Run pipeline job (02 → 03), registers rag_chain model in UC
        section("Step 2/4 — Run supervisor pipeline job (02 → 03)")
        run_pipeline_job()

        # Step 3: Re-deploy with the with-serving target → creates endpoint now that model exists
        section("Step 3/4 — bundle deploy --target with-serving (creates eds-supervisor endpoint)")
        bundle_deploy(ignore_errors=False, target="with-serving")
    else:
        print("\n  (skipping jobs and second bundle deploy)")

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
