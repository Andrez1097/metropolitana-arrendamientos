from __future__ import annotations

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine, select
from models.inmueble import Inmueble, Zona

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metropolitana.db")

# sqlite: check_same_thread necesario
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    seed_if_empty()


def get_session() -> Session:
    return Session(engine)


def seed_if_empty() -> None:
    """
    Crea zonas e inmuebles de ejemplo para que la web funcione de inmediato.
    """
    with Session(engine) as session:
        any_zona = session.exec(select(Zona).limit(1)).first()
        if any_zona:
            return

        zonas = [
            Zona(nombre="Laureles", ciudad="Medellín", lat=6.2442, lng=-75.5976, radio_m=1200),
            Zona(nombre="El Poblado", ciudad="Medellín", lat=6.2086, lng=-75.5650, radio_m=1500),
            Zona(nombre="Belén", ciudad="Medellín", lat=6.2310, lng=-75.6018, radio_m=1400),
            Zona(nombre="Envigado", ciudad="Valle de Aburrá", lat=6.1759, lng=-75.5917, radio_m=1600),
        ]
        session.add_all(zonas)
        session.commit()

        zonas_db = session.exec(select(Zona)).all()
        zona_map = {z.nombre: z for z in zonas_db}

        inmuebles = [
            Inmueble(
                titulo="Apartamento moderno en Laureles",
                tipo="apartamento",
                precio_cop=2200000,
                area_m2=68,
                habitaciones=2,
                banos=2,
                descripcion="Apartamento iluminado, cerca de parques y restaurantes. Incluye balcón y parqueadero.",
                imagenes="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=60,https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=1200&q=60",
                zona_id=zona_map["Laureles"].id,
                direccion_referencia="Cerca al Segundo Parque (referencia general)",
                contacto_whatsapp="Hola, me interesa el apartamento en Laureles (ID: 1). ¿Me das más info?",
                publicado=True,
            ),
            Inmueble(
                titulo="Apartamento con vista en El Poblado",
                tipo="apartamento",
                precio_cop=3800000,
                area_m2=92,
                habitaciones=3,
                banos=2,
                descripcion="Unidad cerrada con piscina y gimnasio. Vista panorámica. Seguridad 24/7.",
                imagenes="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=60,https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=1200&q=60",
                zona_id=zona_map["El Poblado"].id,
                direccion_referencia="Sector Milla de Oro (referencia general)",
                contacto_whatsapp="Hola, me interesa el apartamento en El Poblado (ID: 2). ¿Agenda visita?",
                publicado=True,
            ),
            Inmueble(
                titulo="Casa familiar en Belén",
                tipo="casa",
                precio_cop=2800000,
                area_m2=110,
                habitaciones=4,
                banos=3,
                descripcion="Casa amplia ideal para familia. Patio interno y zona de ropas independiente.",
                imagenes="https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=60",
                zona_id=zona_map["Belén"].id,
                direccion_referencia="Cerca a estación Metroplús (referencia general)",
                contacto_whatsapp="Hola, me interesa la casa en Belén (ID: 3). ¿Qué documentos piden?",
                publicado=True,
            ),
            Inmueble(
                titulo="Apartamento en Envigado, sector tranquilo",
                tipo="apartamento",
                precio_cop=2400000,
                area_m2=72,
                habitaciones=2,
                banos=2,
                descripcion="Zona residencial tranquila. Buen transporte, cerca a comercio. Parqueadero cubierto.",
                imagenes="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=60",
                zona_id=zona_map["Envigado"].id,
                direccion_referencia="Cerca al Parque Principal (referencia general)",
                contacto_whatsapp="Hola, me interesa el apto en Envigado (ID: 4). ¿Está disponible?",
                publicado=True,
            ),
        ]
        session.add_all(inmuebles)
        session.commit()
