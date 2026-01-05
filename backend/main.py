from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# ======================================================
# CARGA VARIABLES DE ENTORNO
# ======================================================
load_dotenv()

# ======================================================
# APP PRINCIPAL
# ======================================================
app = FastAPI(
    title="Metropolitana de Arrendamientos",
    docs_url=None,
    redoc_url=None
)

# ======================================================
# BASE URL PÚBLICA
# ======================================================
PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:8000"
)

# ======================================================
# DIRECTORIOS
# ======================================================
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

# ======================================================
# IMPORTAR ROUTERS
# ======================================================

from routes.inmuebles import router as inmuebles_router
from routes.zonas import router as zonas_router
from routes.chatbot import router as chatbot_router

from routes.robots import router as robots_router
from routes.sitemap_index import router as sitemap_index_router
from routes.sitemap_static import router as sitemap_static_router
from routes.sitemap_barrios import router as sitemap_barrios_router
from routes.sitemap_inmuebles import router as sitemap_inmuebles_router

# ======================================================
# REGISTRAR ROUTERS
# ======================================================

# ---------- API ----------
app.include_router(inmuebles_router, prefix="/api")
app.include_router(zonas_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")

# ---------- SEO ----------
app.include_router(robots_router)
app.include_router(sitemap_index_router)
app.include_router(sitemap_static_router)
app.include_router(sitemap_barrios_router)
app.include_router(sitemap_inmuebles_router)

# ======================================================
# FRONTEND SPA
# ======================================================

if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend"
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def missing_frontend():
        return HTMLResponse(
            "<h1>Frontend no encontrado</h1>"
            "<p>Se esperaba ./frontend/ junto a ./backend/</p>",
            status_code=500
        )
