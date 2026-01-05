from __future__ import annotations

import re
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from db.database import get_session
from models.inmueble import Inmueble, Zona

router = APIRouter(prefix="/api/inmuebles", tags=["inmuebles"])


# ======================================================
# CONFIGURACIÓN GLOBAL SEO
# ======================================================

PUBLIC_BASE_URL = "https://tudominio.com"  # ← cambia solo aquí en prod


# ======================================================
# HELPERS SEO / SLUG / URL CANÓNICA
# ======================================================

def slugify(text: str) -> str:
    """
    Convierte texto a slug SEO-safe, estable y consistente.
    NO depende del idioma.
    """
    text = text.lower().strip()
    text = (
        text.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace("ü", "u")
    )
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def build_inmueble_slug(i: Inmueble, z: Optional[Zona]) -> str:
    """
    Slug SEMÁNTICO y ESTABLE para SEO.
    No usa el título completo (evita cambios futuros).
    """
    parts = [
        i.tipo or "inmueble",
        "en",
        z.nombre if z else "",
    ]
    return slugify(" ".join(parts))


def build_public_url(i: Inmueble, z: Optional[Zona]) -> str:
    """
    URL pública canónica definitiva.
    """
    slug = build_inmueble_slug(i, z)
    return f"/inmueble/{i.id}-{slug}"


def inmueble_to_dict(i: Inmueble, z: Optional[Zona]) -> dict:
    """
    Serializador único (NO repetir lógica).
    """
    slug = build_inmueble_slug(i, z)

    return {
        # =============================
        # Identidad SEO
        # =============================
        "id": i.id,
        "slug": slug,
        "url_publica": build_public_url(i, z),

        # =============================
        # Datos del inmueble
        # =============================
        "titulo": i.titulo,
        "tipo": i.tipo,
        "precio_cop": i.precio_cop,
        "area_m2": i.area_m2,
        "habitaciones": i.habitaciones,
        "banos": i.banos,
        "descripcion": i.descripcion,

        # =============================
        # Media
        # =============================
        "imagenes": [
            x.strip()
            for x in (i.imagenes or "").split(",")
            if x.strip()
        ],

        # =============================
        # Contacto
        # =============================
        "direccion_referencia": i.direccion_referencia,
        "contacto_whatsapp": i.contacto_whatsapp,

        # =============================
        # Zona (SEO + mapas)
        # =============================
        "zona": (
            {
                "id": z.id,
                "nombre": z.nombre,
                "slug": slugify(z.nombre),
                "ciudad": z.ciudad,
                "lat": z.lat,
                "lng": z.lng,
                "radio_m": z.radio_m,
            }
            if z
            else None
        ),
    }


# ======================================================
# LISTADO DE INMUEBLES (API)
# ======================================================

@router.get("")
def listar_inmuebles(
    q: Optional[str] = None,
    tipo: Optional[str] = Query(default=None, description="apartamento|casa"),
    zona: Optional[str] = Query(default=None, description="Nombre de zona"),
    precio_min: Optional[int] = None,
    precio_max: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """
    Listado API:
    - Usado por frontend
    - Usado por sitemap
    - Usado por schema
    """

    stmt = select(Inmueble).where(Inmueble.publicado == True)  # noqa

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            Inmueble.titulo.ilike(like)
            | Inmueble.descripcion.ilike(like)
        )

    if tipo:
        stmt = stmt.where(Inmueble.tipo == tipo.lower())

    if zona:
        z = session.exec(select(Zona).where(Zona.nombre == zona)).first()
        if not z:
            return []
        stmt = stmt.where(Inmueble.zona_id == z.id)

    if precio_min is not None:
        stmt = stmt.where(Inmueble.precio_cop >= precio_min)

    if precio_max is not None:
        stmt = stmt.where(Inmueble.precio_cop <= precio_max)

    inmuebles = session.exec(stmt).all()
    out: List[dict] = []

    for i in inmuebles:
        z = session.get(Zona, i.zona_id)
        out.append(inmueble_to_dict(i, z))

    return out


# ======================================================
# DETALLE INMUEBLE (API JSON)
# ======================================================

@router.get("/{inmueble_id}")
def obtener_inmueble(
    inmueble_id: int,
    session: Session = Depends(get_session)
):
    """
    API detalle:
    - Frontend
    - Schema PRO
    """

    i = session.get(Inmueble, inmueble_id)
    if not i or not i.publicado:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    z = session.get(Zona, i.zona_id)
    return inmueble_to_dict(i, z)


# ======================================================
# URL SEO LIMPIA + REDIRECCIÓN 301 DEFINITIVA
# ======================================================

@router.get("/seo/{inmueble_id}-{slug}", include_in_schema=False)
def inmueble_seo_redirect(
    inmueble_id: int,
    slug: str,
    session: Session = Depends(get_session),
):
    """
    Endpoint SEO:
    - Valida slug
    - Fuerza URL canónica
    - Redirección 301 definitiva
    """

    i = session.get(Inmueble, inmueble_id)
    if not i or not i.publicado:
        raise HTTPException(status_code=404)

    z = session.get(Zona, i.zona_id)
    canonical_path = build_public_url(i, z)
    canonical_url = f"{PUBLIC_BASE_URL}{canonical_path}"

    expected_slug = build_inmueble_slug(i, z)

    # Slug incorrecto → 301
    if slug != expected_slug:
        return RedirectResponse(
            url=canonical_url,
            status_code=301
        )

    # Siempre redirige a la canónica
    return RedirectResponse(
        url=canonical_url,
        status_code=301
    )
