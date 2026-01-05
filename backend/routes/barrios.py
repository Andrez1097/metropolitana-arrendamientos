from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

# ======================================================
# Router
# ======================================================
router = APIRouter()

# ======================================================
# Configuración base
# ======================================================
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

# Ruta al frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"

# ======================================================
# Definición territorial (ESCALABLE)
# ======================================================
# Hoy: Área Metropolitana
# Mañana: Colombia completa (solo agregas ciudades)

TERRITORIO = {
    "medellin": {
        "nombre": "Medellín",
        "region": "Antioquia",
        "barrios": [
            "laureles",
            "el-poblado",
            "belen",
            "robledo",
            "manrique"
        ]
    },
    "envigado": {
        "nombre": "Envigado",
        "region": "Antioquia",
        "barrios": [
            "zona-centro",
            "loma-del-escobero"
        ]
    },
    "sabaneta": {
        "nombre": "Sabaneta",
        "region": "Antioquia",
        "barrios": []
    }
}

# ======================================================
# MAPA CANÓNICO DE BARRIOS
# ======================================================
BARRIOS_CANONICOS = {}
for ciudad, cfg in TERRITORIO.items():
    for barrio in cfg["barrios"]:
        BARRIOS_CANONICOS[barrio] = ciudad

# ======================================================
# UTILIDADES
# ======================================================
def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()

def load_frontend() -> str:
    if not INDEX_HTML.exists():
        return "<h1>Frontend no encontrado</h1>"
    return INDEX_HTML.read_text(encoding="utf-8")

def build_seo(ciudad: str, barrio: Optional[str] = None):
    if barrio:
        title = f"Arriendos en {slug_to_title(barrio)}, {slug_to_title(ciudad)}"
        description = (
            f"Inmuebles en arriendo en {slug_to_title(barrio)}, "
            f"{slug_to_title(ciudad)}. Casas y apartamentos disponibles."
        )
    else:
        title = f"Arriendos en {slug_to_title(ciudad)} | Metropolitana de Arrendamientos"
        description = (
            f"Apartamentos y casas en arriendo en {slug_to_title(ciudad)}. "
            "Zonas verificadas y atención personalizada."
        )
    return title, description

def build_schema_barrio(ciudad: str, barrio: str):
    ciudad_cfg = TERRITORIO[ciudad]

    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Place",
                "@id": f"{PUBLIC_BASE_URL}/arriendos/{barrio}#place",
                "name": f"{slug_to_title(barrio)}, {ciudad_cfg['nombre']}",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": slug_to_title(barrio),
                    "addressRegion": ciudad_cfg["region"],
                    "addressCountry": "CO"
                }
            },
            {
                "@type": "AdministrativeArea",
                "name": ciudad_cfg["nombre"],
                "containedInPlace": {
                    "@type": "AdministrativeArea",
                    "name": ciudad_cfg["region"],
                    "addressCountry": "CO"
                }
            },
            {
                "@type": "RealEstateAgent",
                "name": "Metropolitana de Arrendamientos",
                "url": PUBLIC_BASE_URL,
                "areaServed": {
                    "@type": "Place",
                    "name": f"{slug_to_title(barrio)}, {ciudad_cfg['nombre']}"
                }
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Inicio",
                        "item": f"{PUBLIC_BASE_URL}/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Arriendos",
                        "item": f"{PUBLIC_BASE_URL}/arriendos/{ciudad}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": slug_to_title(barrio),
                        "item": f"{PUBLIC_BASE_URL}/arriendos/{barrio}"
                    }
                ]
            }
        ]
    }

def inject_seo(html: str, title: str, description: str, canonical: str, schema: dict):
    html = html.replace("<title>", f"<title>{title} | ")
    return html.replace(
        "</head>",
        f"""
        <meta name="description" content="{description}">
        <link rel="canonical" href="{canonical}">
        <script type="application/ld+json">
        {json.dumps(schema, ensure_ascii=False, indent=2)}
        </script>
        </head>
        """
    )

# ======================================================
# REDIRECCIÓN LEGACY (301)
# ======================================================
@router.get("/listado.html", include_in_schema=False)
async def legacy_listado_redirect(zona: Optional[str] = None):
    if not zona:
        return RedirectResponse(f"{PUBLIC_BASE_URL}/arriendos/medellin", status_code=301)

    slug = zona.lower().replace(" ", "-")

    if slug in BARRIOS_CANONICOS:
        return RedirectResponse(f"{PUBLIC_BASE_URL}/arriendos/{slug}", status_code=301)

    return RedirectResponse(f"{PUBLIC_BASE_URL}/arriendos/medellin", status_code=301)

# ======================================================
# URL CANÓNICA BARRIO (SEO REAL)
# ======================================================
@router.get("/arriendos/{barrio}", response_class=HTMLResponse, include_in_schema=False)
async def arriendos_barrio_canonico(request: Request, barrio: str):
    barrio = barrio.lower()

    if barrio not in BARRIOS_CANONICOS:
        return HTMLResponse("<h1>Barrio no encontrado</h1>", status_code=404)

    ciudad = BARRIOS_CANONICOS[barrio]

    title, description = build_seo(ciudad, barrio)
    schema = build_schema_barrio(ciudad, barrio)

    html = load_frontend()
    html = inject_seo(
        html=html,
        title=title,
        description=description,
        canonical=f"{PUBLIC_BASE_URL}/arriendos/{barrio}",
        schema=schema
    )

    return HTMLResponse(content=html)

# ======================================================
# URL CIUDAD
# ======================================================
@router.get("/arriendos/{ciudad}", response_class=HTMLResponse)
async def arriendos_ciudad(request: Request, ciudad: str):
    ciudad = ciudad.lower()

    if ciudad not in TERRITORIO:
        return HTMLResponse("<h1>Ciudad no encontrada</h1>", status_code=404)

    title, description = build_seo(ciudad)

    html = load_frontend()
    html = inject_seo(
        html=html,
        title=title,
        description=description,
        canonical=f"{PUBLIC_BASE_URL}/arriendos/{ciudad}",
        schema={}
    )

    return HTMLResponse(content=html)

# ======================================================
# URL SECUNDARIA CIUDAD/BARRIO (NO INDEXABLE)
# ======================================================
@router.get("/arriendos/{ciudad}/{barrio}", include_in_schema=False)
async def arriendos_barrio_secundario(ciudad: str, barrio: str):
    barrio = barrio.lower()

    if barrio not in BARRIOS_CANONICOS:
        return HTMLResponse("<h1>Barrio no encontrado</h1>", status_code=404)

    return RedirectResponse(
        url=f"{PUBLIC_BASE_URL}/arriendos/{barrio}",
        status_code=302
    )
