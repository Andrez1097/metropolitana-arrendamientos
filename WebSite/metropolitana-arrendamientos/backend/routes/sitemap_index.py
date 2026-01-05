from __future__ import annotations

from fastapi import APIRouter, Response
from datetime import datetime
import os

router = APIRouter()

# ======================================================
# CONFIGURACIÓN
# ======================================================

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "https://tudominio.com"  # ← cambia solo aquí en producción
)

TODAY = datetime.utcnow().date().isoformat()


# ======================================================
# SITEMAP INDEX (CANÓNICO)
# ======================================================

@router.get("/sitemap-index.xml", include_in_schema=False)
async def sitemap_index():
    """
    Sitemap index oficial.
    Google Search Console:
    👉 este es el ÚNICO sitemap que se registra.
    """

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <!-- ===============================
       Páginas estáticas (home, legales, contacto)
       =============================== -->
  <sitemap>
    <loc>{PUBLIC_BASE_URL}/sitemaps/sitemap-static.xml</loc>
    <lastmod>{TODAY}</lastmod>
  </sitemap>

  <!-- ===============================
       Listados por ciudad / barrio
       =============================== -->
  <sitemap>
    <loc>{PUBLIC_BASE_URL}/sitemaps/sitemap-barrios.xml</loc>
    <lastmod>{TODAY}</lastmod>
  </sitemap>

  <!-- ===============================
       Inmuebles individuales (URLs limpias)
       =============================== -->
  <sitemap>
    <loc>{PUBLIC_BASE_URL}/sitemaps/sitemap-inmuebles.xml</loc>
    <lastmod>{TODAY}</lastmod>
  </sitemap>

</sitemapindex>
"""

    return Response(
        content=xml.strip(),
        media_type="application/xml"
    )
