from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field


class Zona(SQLModel, table=True):
    __tablename__ = "zona"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    ciudad: str
    lat: float
    lng: float
    radio_m: int = 1200


class Inmueble(SQLModel, table=True):
    __tablename__ = "inmueble"

    id: Optional[int] = Field(default=None, primary_key=True)

    titulo: str
    tipo: str  # apartamento | casa
    precio_cop: int
    area_m2: int
    habitaciones: int
    banos: int

    descripcion: str
    imagenes: str
    direccion_referencia: str
    contacto_whatsapp: str
    publicado: bool = True

    # Foreign key pura (SIN Relationship)
    zona_id: int = Field(foreign_key="zona.id")
