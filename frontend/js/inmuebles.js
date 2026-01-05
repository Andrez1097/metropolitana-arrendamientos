const API_BASE = "http://127.0.0.1:8000";

/* ======================================================
   UTILIDADES GENERALES
   ====================================================== */

function formatCOP(value) {
  return Number(value || 0).toLocaleString("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0
  });
}

function getQueryParams() {
  return Object.fromEntries(new URLSearchParams(window.location.search));
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { credentials: "same-origin" });
  if (!res.ok) throw new Error(`Error API ${res.status}`);
  return res.json();
}

function safeText(s) {
  return String(s || "").replace(/\s+/g, " ").trim();
}

function truncate(s, n = 160) {
  const t = safeText(s);
  if (t.length <= n) return t;
  return t.slice(0, n - 1).trim() + "…";
}

function slugToTitle(slug) {
  return safeText(String(slug || ""))
    .replace(/-/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

/* ======================================================
   SEO META + CANONICAL + HREFLANG
   ====================================================== */

function setMeta({ title, description }) {
  if (title) document.title = title;

  let metaDesc = document.querySelector("meta[name='description']");
  if (!metaDesc) {
    metaDesc = document.createElement("meta");
    metaDesc.name = "description";
    document.head.appendChild(metaDesc);
  }
  if (description) metaDesc.content = description;
}

function setCanonical(url) {
  let link = document.querySelector('link[rel="canonical"]');
  if (!link) {
    link = document.createElement("link");
    link.rel = "canonical";
    document.head.appendChild(link);
  }
  link.href = url || window.location.href;
}

function setHreflangLinks() {
  try {
    document
      .querySelectorAll('link[rel="alternate"][hreflang]')
      .forEach((n) => n.remove());

    const defaults = [
      { lang: "es-CO", href: window.location.href },
      { lang: "x-default", href: window.location.href }
    ];

    const alternates = Array.isArray(window.__I18N_ALTERNATES__)
      ? window.__I18N_ALTERNATES__
      : defaults;

    alternates.forEach((a) => {
      if (!a?.lang || !a?.href) return;
      const link = document.createElement("link");
      link.rel = "alternate";
      link.hreflang = a.lang;
      link.href = a.href;
      document.head.appendChild(link);
    });
  } catch (_) {}
}

/* ======================================================
   JSON-LD
   ====================================================== */

function upsertJsonLd(id, schema) {
  if (!schema) return;
  const sid = `jsonld-${id}`;
  let el = document.getElementById(sid);
  if (!el) {
    el = document.createElement("script");
    el.type = "application/ld+json";
    el.id = sid;
    document.head.appendChild(el);
  }
  el.textContent = JSON.stringify(schema, null, 2);
}

/* ======================================================
   CONFIG MARCA (ESCALABLE)
   ====================================================== */

function getBrandConfig() {
  const base = window.location.origin;
  return {
    name: "Metropolitana de Arrendamientos",
    baseUrl: base,
    countryCode: "CO",
    regionName: "Antioquia",
    cityDefault: "Medellín",
    inLanguage: "es-CO"
  };
}

/* ======================================================
   BREADCRUMB PROFESIONAL (VISIBLE + SCHEMA)
   ====================================================== */

function detectContext() {
  const path = window.location.pathname.split("/").filter(Boolean);
  const q = getQueryParams();

  if (!path.length) return { type: "home" };

  if (path[0] === "arriendos" && path.length === 1)
    return { type: "ciudad", ciudad: "medellin" };

  if (path[0] === "arriendos" && path.length === 2)
    return { type: "barrio", barrio: path[1] };

  if (
    (path[0] === "inmueble" || path[0] === "inmuebles") &&
    path[1]
  )
    return { type: "detalle", id: path[1] };

  if (path[path.length - 1] === "inmueble.html" && q.id)
    return { type: "detalle", id: q.id };

  return { type: "other" };
}

function ensureBreadcrumbContainer() {
  let el = document.getElementById("breadcrumb");
  if (el) return el;

  const nav = document.querySelector(".nav");
  if (!nav) return null;

  el = document.createElement("nav");
  el.id = "breadcrumb";
  el.setAttribute("aria-label", "Breadcrumb");
  el.style.fontSize = "13px";
  el.style.margin = "6px 0 12px";
  el.style.color = "#555";

  nav.parentNode.insertBefore(el, nav.nextSibling);
  return el;
}

function renderBreadcrumb(items) {
  const host = ensureBreadcrumbContainer();
  if (!host) return;

  host.innerHTML = items
    .map((it) =>
      it.url
        ? `<a href="${it.url}" style="color:#0066cc;text-decoration:none;">${safeText(it.name)}</a>`
        : `<span>${safeText(it.name)}</span>`
    )
    .join(" &nbsp;›&nbsp; ");
}

function buildBreadcrumbSchema(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((it, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": safeText(it.name),
      "item": it.url || undefined
    }))
  };
}

/* ======================================================
   AUTO (NO ROMPE NADA EXISTENTE)
   ====================================================== */

if (typeof cargarListado !== "function") function cargarListado() {}
if (typeof cargarDetalle !== "function") function cargarDetalle() {}

document.addEventListener("DOMContentLoaded", async () => {
  setHreflangLinks();

  try { await cargarListado(); } catch (_) {}
  try { await cargarDetalle(); } catch (_) {}

  const brand = getBrandConfig();
  const ctx = detectContext();

  const crumbs = [
    { name: "Inicio", url: `${brand.baseUrl}/` }
  ];

  if (ctx.type === "ciudad") {
    crumbs.push({ name: "Arriendos", url: `${brand.baseUrl}/arriendos/medellin` });
  }

  if (ctx.type === "barrio") {
    crumbs.push({ name: "Arriendos", url: `${brand.baseUrl}/arriendos/medellin` });
    crumbs.push({ name: slugToTitle(ctx.barrio) });
  }

  if (ctx.type === "detalle") {
    crumbs.push({ name: "Arriendos", url: `${brand.baseUrl}/arriendos/medellin` });
    crumbs.push({ name: "Detalle de inmueble" });
  }

  renderBreadcrumb(crumbs);
  upsertJsonLd("breadcrumb", buildBreadcrumbSchema(crumbs));
});
