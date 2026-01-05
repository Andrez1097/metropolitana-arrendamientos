from __future__ import annotations

import re
import unicodedata
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

# ======================================================
# Helper: slugify (mismo criterio que barrios.py)
# ======================================================

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text


# ======================================================
# REDIRECCIÓN 301
# /listado.html?zona=Laureles → /arriendos/laureles
# ======================================================

@router.get("/listado.html", include_in_schema=False)
async def redirect_listado_zona(request: Request):
    qp = dict(request.query_params)

    zona = qp.get("zona")
    if not zona:
        # Sin parámetro zona → NO redirige
        return None

    slug = slugify(zona)

    return RedirectResponse(
        url=f"/arriendos/{slug}",
        status_code=301
    )
