from __future__ import annotations

from fastapi import APIRouter, Response
from datetime import datetime
from typing import List, Dict
import os
import unicodedata
import re

router = APIRouter(prefix="/sitemaps")

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
LASTMOD = datetime.utcnow().date().isoformat()

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text

def build_url(loc: str, priority: str = "0.8", changefreq: str = "weekly") -> str:
    return f"""
    <url>
        <loc>{loc}</loc>
        <lastmod>{LASTMOD}</lastmod>
        <changefreq>{changefreq}</changefreq>
        <priority>{priority}</priority>
    </url>
    """.strip()

# ======================================================
# FUENTE DE BARRIOS (ESCALABLE A NIVEL NACIONAL)
# ======================================================
BARRIOS: List[Dict[str, str]] = [
    {"nombre": "Laureles", "ciudad": "Medellín", "region": "Antioquia"},
    {"nombre": "El Poblado", "ciudad": "Medellín", "region": "Antioquia"},
    {"nombre": "Belén", "ciudad": "Medellín", "region": "Antioquia"},
    {"nombre": "Robledo", "ciudad": "Medellín", "region": "Antioquia"},
    {"nombre": "Estadio", "ciudad": "Medellín", "region": "Antioquia"},
    {"nombre": "Envigado", "ciudad": "Envigado", "region": "Antioquia"},
    {"nombre": "Sabaneta", "ciudad": "Sabaneta", "region": "Antioquia"},
    {"nombre": "Itagüí", "ciudad": "Itagüí", "region": "Antioquia"},
    {"nombre": "Bello", "ciudad": "Bello", "region": "Antioquia"},
    {"nombre": "La Estrella", "ciudad": "La Estrella", "region": "Antioquia"},
]

@router.get("/sitemap-barrios.xml", include_in_schema=False)
async def sitemap_barrios():
    urls_xml = []

    for barrio in BARRIOS:
        slug = slugify(barrio["nombre"])
        loc = f"{PUBLIC_BASE_URL}/arriendos/{slug}"
        urls_xml.append(build_url(loc))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls_xml)}
</urlset>
"""
    return Response(content=xml.strip(), media_type="application/xml")
