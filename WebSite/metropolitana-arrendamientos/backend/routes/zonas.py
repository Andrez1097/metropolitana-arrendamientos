from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from db.database import get_session
from models.inmueble import Zona

router = APIRouter(prefix="/api/zonas", tags=["zonas"])


@router.get("")
def listar_zonas(session: Session = Depends(get_session)):
    zonas = session.exec(select(Zona)).all()
    return [
        {
            "id": z.id,
            "nombre": z.nombre,
            "ciudad": z.ciudad,
            "lat": z.lat,
            "lng": z.lng,
            "radio_m": z.radio_m,
        }
        for z in zonas
    ]
