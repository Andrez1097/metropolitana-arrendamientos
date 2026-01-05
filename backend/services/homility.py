"""
Integración futura Homility.

La idea: Homility/Simipidi es el “maestro” de inmuebles.
Aquí se implementa:
- fetch_inmuebles()
- fetch_inmueble(id)
- fetch_zonas()
y se sincroniza a la BD local si lo deseas.

Por ahora es un placeholder.
"""

from __future__ import annotations

from typing import Any


class HomilityService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def fetch_inmuebles(self) -> list[dict[str, Any]]:
        return []

    async def fetch_inmueble(self, inmueble_id: int) -> dict[str, Any] | None:
        return None

    async def fetch_zonas(self) -> list[dict[str, Any]]:
        return []
