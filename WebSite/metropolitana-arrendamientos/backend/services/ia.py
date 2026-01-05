from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Metropolitana de Arrendamientos")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "573001112233")


def simple_chatbot_reply(message: str) -> str:
    """
    Chatbot básico por reglas (para arrancar hoy).
    Luego puedes cambiar esto por un modelo IA real.
    """
    msg = (message or "").strip().lower()

    if not msg:
        return f"Hola 👋 Soy el asistente de {APP_NAME}. ¿Buscas apartamento o casa? ¿En qué zona y presupuesto?"

    if any(k in msg for k in ["hola", "buenas", "buenos", "hey"]):
        return f"¡Hola! 👋 Soy el asistente de {APP_NAME}. Dime: tipo (apto/casa), zona (Laureles, Poblado, Belén, Envigado) y presupuesto."

    if "document" in msg or "requisit" in msg:
        return (
            "Normalmente te piden: cédula, carta laboral o extractos, codeudor (según el caso) "
            "y estudio de arrendamiento. Si me dices el inmueble (ID) te indico el proceso sugerido."
        )

    if any(k in msg for k in ["whatsapp", "contact", "asesor", "agendar", "visita"]):
        return (
            f"Perfecto. Para atención directa por WhatsApp: https://wa.me/{WHATSAPP_NUMBER} "
            "Cuéntame el ID del inmueble y tu horario."
        )

    if "precio" in msg or "presupuesto" in msg:
        return "Dime tu presupuesto máximo en COP (ej: 2500000) y la zona. Yo te muestro opciones."

    if any(k in msg for k in ["poblado", "laureles", "belén", "belen", "envigado"]):
        return "Listo ✅ Ahora dime tu presupuesto máximo (COP) y si buscas apartamento o casa."

    return (
        "Entendido ✅ Para ayudarte mejor dime:\n"
        "1) Zona (Laureles / El Poblado / Belén / Envigado)\n"
        "2) Tipo (apartamento o casa)\n"
        "3) Presupuesto máximo (COP)\n"
        "y te muestro opciones."
    )
