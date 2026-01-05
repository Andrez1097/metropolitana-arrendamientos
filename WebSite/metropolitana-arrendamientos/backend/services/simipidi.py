"""
Integración futura Simipidi.
Misma lógica que HomilityService.
"""

from __future__ import annotations
from typing import Any


class SimipidiService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def fetch_inmuebles(self) -> list[dict[str, Any]]:
        return []

    async def fetch_inmueble(self, inmueble_id: int) -> dict[str, Any] | None:
        return None

    async def fetch_zonas(self) -> list[dict[str, Any]]:
        return []
