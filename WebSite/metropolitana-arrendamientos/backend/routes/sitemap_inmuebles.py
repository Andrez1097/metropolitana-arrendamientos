from __future__ import annotations

import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Response

import requests

# ======================================================
# Router
# ======================================================

router = APIRouter(prefix="/sitemaps")

# ======================================================
# Configuración
# ======================================================

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:8000"
)

API_INMUEBLES_URL = f"{PUBLIC_BASE_URL}/api/inmuebles"

LASTMOD = datetime.utcnow().strftime("%Y-%m-%d")


# ======================================================
# Sitemap Inmuebles (URL limpia)
# ======================================================

@router.get(
    "/sitemap-inmuebles.xml",
    include_in_schema=False
)
def sitemap_inmuebles():
    """
    Sitemap de inmuebles usando URL pública canónica:
      /inmueble/{id}-{slug}

    ✔ SEO-safe
    ✔ Google-safe
    ✔ Compatible con Search Console
    ✔ Preparado para expansión futura
    """

    try:
        resp = requests.get(API_INMUEBLES_URL, timeout=10)
        resp.raise_for_status()
        inmuebles: List[dict] = resp.json()
    except Exception:
        # En caso de error, no rompemos Google
        inmuebles = []

    urls_xml = []

    for i in inmuebles:
        url_publica = i.get("url_publica")
        if not url_publica:
            continue

        urls_xml.append(
            f"""
            <url>
                <loc>{PUBLIC_BASE_URL}{url_publica}</loc>
                <lastmod>{LASTMOD}</lastmod>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """.strip()
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
>
{chr(10).join(urls_xml)}
</urlset>
"""

    return Response(
        content=xml.strip(),
        media_type="application/xml"
    )
