from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from prerender import Prerenderer, is_probably_bot

# ======================================================
# CARGA VARIABLES DE ENTORNO
# ======================================================
load_dotenv()

# ======================================================
# APP PRINCIPAL
# ======================================================
app = FastAPI(
    title=os.getenv("APP_NAME", "Metropolitana de Arrendamientos"),
    docs_url=None,
    redoc_url=None,
)

# ======================================================
# ENV / FLAGS
# ======================================================
ENV = os.getenv("ENV", "dev").lower().strip()

# Si es "1/true/yes/on" => habilita
ENABLE_PRERENDER = os.getenv("ENABLE_PRERENDER", "0").lower().strip() in ("1", "true", "yes", "on")

# ======================================================
# BASE URL PÚBLICA
# ======================================================
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# ======================================================
# DIRECTORIOS
# ======================================================
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

# ======================================================
# PRERENDER (SEO – SOLO BOTS)
# ======================================================
prerenderer = Prerenderer(ttl_seconds=60, max_cache=200)

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

# API
app.include_router(inmuebles_router, prefix="/api")
app.include_router(zonas_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")

# SEO
app.include_router(robots_router)
app.include_router(sitemap_index_router)
app.include_router(sitemap_static_router)
app.include_router(sitemap_barrios_router)
app.include_router(sitemap_inmuebles_router)

# ======================================================
# STARTUP / SHUTDOWN
# ======================================================

@app.on_event("startup")
async def startup():
    """
    En DEV:
      - NO iniciamos Playwright (evita crash local)
    En PROD:
      - Solo iniciamos si ENABLE_PRERENDER=1
    """
    if ENV == "prod" and ENABLE_PRERENDER:
        try:
            await prerenderer.start()
            print("✅ Prerender ENABLED (Playwright iniciado)")
        except Exception as e:
            # NO rompe la app si falla
            print(f"⚠️ Prerender NO se pudo iniciar: {e}")
    else:
        print("ℹ️ Prerender DISABLED (modo dev o flag apagado)")

@app.on_event("shutdown")
async def shutdown():
    if ENV == "prod" and ENABLE_PRERENDER:
        try:
            await prerenderer.stop()
        except Exception:
            pass

# ======================================================
# MIDDLEWARE PRERENDER (SOLO BOTS, SOLO HTML)
# ======================================================

@app.middleware("http")
async def prerender_middleware(request: Request, call_next):
    path = request.url.path

    # Bypass absoluto: nunca prerender API ni archivos
    if (
        path.startswith("/api")
        or path == "/robots.txt"
        or path.startswith("/sitemap")
        or path.endswith(".xml")
        or path.endswith(".txt")
        or path.endswith(".json")
        or path.startswith("/assets")
        or path.startswith("/static")
    ):
        return await call_next(request)

    # Si prerender no está habilitado, nunca hacemos nada
    if not (ENV == "prod" and ENABLE_PRERENDER):
        return await call_next(request)

    ua = request.headers.get("user-agent", "")
    qp = dict(request.query_params)

    force = qp.get("prerender") == "1" or "_escaped_fragment_" in qp
    if not (force or is_probably_bot(ua)):
        return await call_next(request)

    url = f"{PUBLIC_BASE_URL}{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    try:
        html = await prerenderer.render(url)
        if html:
            return HTMLResponse(content=html, status_code=200, headers={"X-Prerendered": "1"})
    except Exception:
        pass

    return await call_next(request)

# ======================================================
# FRONTEND SPA
# ======================================================
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    async def missing_frontend():
        return HTMLResponse("<h1>Frontend no encontrado</h1>", status_code=500)
