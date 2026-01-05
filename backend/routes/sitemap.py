from fastapi import APIRouter, Response
from datetime import datetime
import xml.etree.ElementTree as ET
import requests

router = APIRouter()

BASE_URL = "https://www.tusitio.com"  # 🔴 CAMBIA ESTO
API_INMUEBLES = "http://127.0.0.1:8000/api/inmuebles"


def iso_date(dt: datetime | None = None) -> str:
    return (dt or datetime.utcnow()).date().isoformat()


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    urlset = ET.Element(
        "urlset",
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    )

    def add_url(loc: str, lastmod: str, priority="0.8", changefreq="weekly"):
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = loc
        ET.SubElement(url, "lastmod").text = lastmod
        ET.SubElement(url, "changefreq").text = changefreq
        ET.SubElement(url, "priority").text = priority

    # ─────────────────────────────────────────────
    # URLs FIJAS
    # ─────────────────────────────────────────────
    add_url(f"{BASE_URL}/", iso_date(), "1.0", "daily")
    add_url(f"{BASE_URL}/listado.html", iso_date(), "0.9", "daily")

    # ─────────────────────────────────────────────
    # INMUEBLES + BARRIOS
    # ─────────────────────────────────────────────
    try:
        inmuebles = requests.get(API_INMUEBLES, timeout=10).json()
    except Exception:
        inmuebles = []

    zonas = set()

    for i in inmuebles:
        inmueble_id = i.get("id")
        zona = i.get("zona", {}).get("nombre")
        lastmod = iso_date()

        # Detalle inmueble
        if inmueble_id:
            add_url(
                f"{BASE_URL}/inmueble.html?id={inmueble_id}",
                lastmod,
                "0.7",
                "weekly"
            )

        # Guardamos zona para listado por barrio
        if zona:
            zonas.add(zona)

    # ─────────────────────────────────────────────
    # LISTADOS POR BARRIO (SEO POR ZONA)
    # ─────────────────────────────────────────────
    for zona in zonas:
        add_url(
            f"{BASE_URL}/listado.html?zona={zona.replace(' ', '%20')}",
            iso_date(),
            "0.8",
            "daily"
        )

    xml_bytes = ET.tostring(urlset, encoding="utf-8", xml_declaration=True)

    return Response(
        content=xml_bytes,
        media_type="application/xml"
    )
