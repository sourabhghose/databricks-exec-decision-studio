"""
Executive Decision Studio — Alinta Energy
FastAPI backend serving React SPA + API routes.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.routes import chat, kpi, audit, actions, risks, decisions, documents, briefing, overview, market, export, upload, vector_search, simulate

print(f"[EDS] Python {sys.version.split()[0]} | FastAPI backend")

app = FastAPI(
    title="Executive Decision Studio",
    description="Alinta Energy — Agentic AI Strategic Intelligence Platform",
    version="2.0.0",
)

# ── API routes ───────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(kpi.router)
app.include_router(audit.router)
app.include_router(actions.router)
app.include_router(risks.router)
app.include_router(decisions.router)
app.include_router(documents.router)
app.include_router(briefing.router)
app.include_router(overview.router)
app.include_router(market.router)
app.include_router(export.router)
app.include_router(upload.router)
app.include_router(vector_search.router)
app.include_router(simulate.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "healthy", "app": "Executive Decision Studio", "version": "2.0.0"}


# ── Serve React SPA from frontend/dist ───────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    # Mount static assets (JS, CSS, images)
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Serve any other static files at root level (favicon, etc.)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't catch API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}

        # Try to serve the exact file first
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Fallback to index.html for SPA routing
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    print(f"[EDS] WARNING: {FRONTEND_DIR} not found. Run 'cd frontend && npm run build'")

    @app.get("/")
    async def no_frontend():
        return {
            "message": "Frontend not built. Run: cd frontend && npm install && npm run build",
            "api_health": "/api/health",
        }
