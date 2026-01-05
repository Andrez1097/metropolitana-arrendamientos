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

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
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

/* ======================================================
   OBTENER ID DESDE URL LIMPIA
====================================================== */

function getInmuebleIdFromUrl() {
  // /inmueble/1-apartamento-en-laureles
  const parts = window.location.pathname.split("/").filter(Boolean);
  if (parts[0] !== "inmueble" || !parts[1]) return null;

  const id = parts[1].split("-")[0];
  return /^\d+$/.test(id) ? id : null;
}

/* ======================================================
   SEO
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

/* ======================================================
   JSON-LD helpers
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

function buildBreadcrumbSchema(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: safeText(it.name),
      item: it.url ? String(it.url) : undefined
    }))
  };
}

function buildInmuebleSchema(inmueble) {
  const type = inmueble?.tipo === "casa" ? "House" : "Apartment";
  const baseUrl = window.location.origin;

  return {
    "@context": "https://schema.org",
    "@type": type,
    name: safeText(inmueble.titulo),
    description: safeText(inmueble.descripcion),
    url: `${baseUrl}${inmueble.url_publica}`,
    image: Array.isArray(inmueble.imagenes) ? inmueble.imagenes : [],
    address: {
      "@type": "PostalAddress",
      addressLocality: safeText(inmueble?.zona?.nombre || "Medellín"),
      addressRegion: "Antioquia",
      addressCountry: "CO"
    },
    floorSize: inmueble.area_m2
      ? { "@type": "QuantitativeValue", value: inmueble.area_m2, unitCode: "MTK" }
      : undefined,
    numberOfRooms: inmueble.habitaciones || undefined,
    numberOfBathroomsTotal: inmueble.banos || undefined,
    offers: {
      "@type": "Offer",
      priceCurrency: "COP",
      price: inmueble.precio_cop || undefined,
      availability: "https://schema.org/InStock",
      url: `${baseUrl}${inmueble.url_publica}`
    }
  };
}

/* ======================================================
   BREADCRUMB (VISIBLE)
====================================================== */

function ensureBreadcrumb() {
  let el = document.getElementById("breadcrumb");
  if (el) return el;

  const nav = document.querySelector(".nav");
  if (!nav) return null;

  el = document.createElement("nav");
  el.id = "breadcrumb";
  el.setAttribute("aria-label", "Breadcrumb");
  el.style.fontSize = "13px";
  el.style.margin = "6px 0 12px";
  nav.parentNode.insertBefore(el, nav.nextSibling);
  return el;
}

function renderBreadcrumb(items) {
  const host = ensureBreadcrumb();
  if (!host) return;

  host.innerHTML = items
    .map(it =>
      it.url
        ? `<a href="${it.url}" style="color:#0066cc;text-decoration:none;">${safeText(it.name)}</a>`
        : `<span>${safeText(it.name)}</span>`
    )
    .join(" &nbsp;›&nbsp; ");
}

/* ======================================================
   WHATSAPP (NUMERO + MENSAJE)
====================================================== */

function buildWhatsappLink(msg) {
  const number = (window.WHATSAPP_NUMBER || "573001112233").replace(/[^\d]/g, "");
  const text = encodeURIComponent(msg || "Hola, me interesa este inmueble. ¿Me das más información?");
  return `https://wa.me/${number}?text=${text}`;
}

/* ======================================================
   DETALLE DE INMUEBLE (⭐ CLAVE ⭐)
====================================================== */

async function cargarDetalle() {
  const id = getInmuebleIdFromUrl();
  if (!id) return;

  const cont = document.getElementById("detalle");
  if (!cont) return;

  try {
    const inmueble = await apiGet(`/api/inmuebles/${id}`);

    // ✅ Asegurar contenedor del mapa con ID correcto (#mapa)
    // (tu mapa.js usa "mapa", no "map")
    cont.innerHTML = `
      <h1>${safeText(inmueble.titulo)}</h1>

      <p><strong>Precio:</strong> ${formatCOP(inmueble.precio_cop)}</p>
      <p><strong>Tipo:</strong> ${safeText(inmueble.tipo)}</p>
      <p><strong>Área:</strong> ${inmueble.area_m2 ?? "-"} m²</p>
      <p><strong>Habitaciones:</strong> ${inmueble.habitaciones ?? "-"}</p>
      <p><strong>Baños:</strong> ${inmueble.banos ?? "-"}</p>

      <p style="margin-top:10px;">${safeText(inmueble.descripcion)}</p>

      <div id="galeria" style="margin-top:16px;"></div>

      <a class="btn" id="btnWhatsapp" target="_blank" rel="noopener">
        📲 Contactar por WhatsApp
      </a>

      <h2 style="margin-top:22px;">📍 Ubicación aproximada</h2>
      <div id="mapa" style="height:320px;margin-top:10px;border-radius:12px;overflow:hidden;"></div>
    `;

    // -------- GALERÍA --------
    const galeria = document.getElementById("galeria");
    (Array.isArray(inmueble.imagenes) ? inmueble.imagenes : []).forEach(src => {
      const img = document.createElement("img");
      img.src = src;
      img.loading = "lazy";
      img.alt = safeText(inmueble.titulo);
      img.style.maxWidth = "320px";
      img.style.margin = "6px";
      img.style.borderRadius = "10px";
      galeria.appendChild(img);
    });

    // -------- WHATSAPP --------
    const btn = document.getElementById("btnWhatsapp");
    if (btn) {
      btn.href = buildWhatsappLink(inmueble.contacto_whatsapp || `Hola, me interesa el inmueble: ${inmueble.titulo}`);
    }

    // -------- SEO (TITLE por barrio) --------
    const barrio = safeText(inmueble?.zona?.nombre || "Medellín");
    setMeta({
      title: `${safeText(inmueble.titulo)} en ${barrio} | Metropolitana de Arrendamientos`,
      description: truncate(`${safeText(inmueble.titulo)} en arriendo en ${barrio}. ${safeText(inmueble.descripcion)}`, 155)
    });

    setCanonical(`${window.location.origin}${inmueble.url_publica}`);

    // -------- BREADCRUMB + JSONLD --------
    const crumbs = [
      { name: "Inicio", url: "/" },
      { name: "Arriendos", url: "/arriendos/medellin" },
      { name: barrio, url: `/arriendos/medellin/${encodeURIComponent(barrio.toLowerCase().replace(/\s+/g, "-"))}` },
      { name: inmueble.titulo }
    ];

    renderBreadcrumb(crumbs);
    upsertJsonLd("breadcrumb", buildBreadcrumbSchema(crumbs));
    upsertJsonLd("inmueble", buildInmuebleSchema(inmueble));

    // 👉 El mapa se renderiza desde mapa.js automáticamente por ruta
    // (no llamamos nada aquí)

  } catch (e) {
    cont.innerHTML = "<h2>Inmueble no encontrado</h2>";
    console.error(e);
  }
}

/* ======================================================
   AUTO
====================================================== */

document.addEventListener("DOMContentLoaded", () => {
  cargarDetalle();
});
