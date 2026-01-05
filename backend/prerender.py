from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

from playwright.async_api import async_playwright, Browser, Playwright, Page


BOT_UA_KEYWORDS = (
    "googlebot",
    "bingbot",
    "slurp",  # yahoo
    "duckduckbot",
    "baiduspider",
    "yandexbot",
    "sogou",
    "exabot",
    "facebot",
    "facebookexternalhit",
    "twitterbot",
    "linkedinbot",
    "whatsapp",
    "telegrambot",
    "discordbot",
    "pinterest",
)

ASSET_EXTENSIONS = (
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".ico",
    ".map",
    ".json",
    ".txt",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
)


def is_probably_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    return any(k in ua for k in BOT_UA_KEYWORDS)


def should_prerender_path(path: str) -> bool:
    # No pre-render para API ni assets
    p = (path or "").lower()
    if p.startswith("/api"):
        return False
    if any(p.endswith(ext) for ext in ASSET_EXTENSIONS):
        return False

    # Pre-render para páginas html o root
    if p == "/" or p.endswith(".html"):
        return True

    # Si no tiene extensión (ej: /listado) también podría ser página.
    # En tu caso usas .html, pero esto lo deja listo para futuro.
    if "." not in p.split("/")[-1]:
        return True

    return False


@dataclass
class CacheItem:
    html: str
    created_at: float


class Prerenderer:
    """
    Prerenderer con Playwright (Chromium headless) + cache en memoria con TTL.
    """
    def __init__(self, ttl_seconds: int = 60, max_cache: int = 200):
        self.ttl_seconds = ttl_seconds
        self.max_cache = max_cache

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

        self._cache: Dict[str, CacheItem] = {}

    async def start(self) -> None:
        async with self._lock:
            if self._browser:
                return
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)

    async def stop(self) -> None:
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            self._cache.clear()

    def _cache_get(self, key: str) -> Optional[str]:
        item = self._cache.get(key)
        if not item:
            return None
        if (time.time() - item.created_at) > self.ttl_seconds:
            self._cache.pop(key, None)
            return None
        return item.html

    def _cache_set(self, key: str, html: str) -> None:
        # Evitar crecer indefinidamente
        if len(self._cache) >= self.max_cache:
            # elimina el más viejo
            oldest_key = min(self._cache.items(), key=lambda kv: kv[1].created_at)[0]
            self._cache.pop(oldest_key, None)
        self._cache[key] = CacheItem(html=html, created_at=time.time())

    async def render(self, url: str) -> str:
        # Cache
        cached = self._cache_get(url)
        if cached:
            return cached

        await self.start()
        assert self._browser is not None

        async with self._lock:
            # Nota: un page por request (simple y estable)
            context = await self._browser.new_context(
                viewport={"width": 1365, "height": 768},
                java_script_enabled=True,
            )
            page = await context.new_page()

            html = ""
            try:
                await page.goto(url, wait_until="networkidle", timeout=45_000)

                # Espera "señal" de tu JS (lo definimos en inmuebles.js):
                # window.__PRERENDER_STATE__ para saber que ya cargó y filtró.
                # Si no existe, igual devolvemos HTML.
                try:
                    await page.wait_for_function(
                        "window.__PRERENDER_STATE__ !== undefined",
                        timeout=12_000
                    )
                except Exception:
                    pass

                # Asegura que haya <title> (SEO) y JSON-LD (schema) en el DOM final
                # (tu JS ya lo hace; esto solo espera un poco si hace falta)
                try:
                    await page.wait_for_function(
                        "document.title && document.title.length > 0",
                        timeout=5_000
                    )
                except Exception:
                    pass

                html = await page.content()

            finally:
                await page.close()
                await context.close()

        # Cachea
        if html:
            self._cache_set(url, html)
        return html
