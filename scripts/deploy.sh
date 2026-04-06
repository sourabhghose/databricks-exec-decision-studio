#!/bin/bash
# EDS deploy script — syncs source + uploads built frontend dist (excluded from .gitignore)
# Usage: ./scripts/deploy.sh [profile]

set -e

PROFILE="${1:-fe-vm-ausnet-process-intel}"
WORKSPACE_PATH="/Workspace/Users/sourabh.ghose@databricks.com/eds-app"
APP_SOURCE_PATH="$WORKSPACE_PATH/app"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "[1/4] Building frontend..."
cd "$APP_DIR/app/frontend"
npm run build

echo "[2/4] Syncing source files..."
cd "$APP_DIR"
databricks sync . "$WORKSPACE_PATH" \
  --exclude node_modules \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude .git \
  --profile "$PROFILE" \
  --full

echo "[3/4] Uploading frontend dist (excluded from .gitignore, must be imported separately)..."
databricks workspace import-dir \
  "$APP_DIR/app/frontend/dist" \
  "$WORKSPACE_PATH/app/frontend/dist" \
  --overwrite \
  --profile "$PROFILE"

echo "[4/4] Deploying app..."
databricks apps deploy exec-decision-studio \
  --source-code-path "$APP_SOURCE_PATH" \
  --profile "$PROFILE"

echo "Done. App: https://exec-decision-studio-7474646159107961.aws.databricksapps.com"
