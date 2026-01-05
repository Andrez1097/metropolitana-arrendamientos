from fastapi import APIRouter, Response
import os

router = APIRouter()

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:8000"
)

@router.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    content = f"""
User-agent: *
Allow: /

Sitemap: {PUBLIC_BASE_URL}/sitemap-index.xml
""".strip()

    return Response(
        content=content,
        media_type="text/plain"
    )
