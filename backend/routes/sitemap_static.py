from fastapi import APIRouter, Response
import os

router = APIRouter(prefix="/sitemaps")

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

@router.get("/sitemap-static.xml", include_in_schema=False)
async def sitemap_static():
    urls = [
        "/",
        "/listado.html",
    ]

    xml_urls = "".join(
        f"""
        <url>
            <loc>{PUBLIC_BASE_URL}{u}</loc>
            <changefreq>daily</changefreq>
            <priority>1.0</priority>
        </url>
        """
        for u in urls
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}
</urlset>
"""

    return Response(content=xml, media_type="application/xml")
