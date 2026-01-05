const API_BASE = "http://127.0.0.1:8000";

let mapInstance = null;
let markersLayer = null;

/* ======================================================
   UTILIDADES
   ====================================================== */

function getInmuebleIdFromUrl() {
  // /inmueble/1-apartamento-en-laureles
  const parts = window.location.pathname.split("/").filter(Boolean);
  if (parts[0] !== "inmueble" || !parts[1]) return null;
  const id = parts[1].split("-")[0];
  return /^\d+$/.test(id) ? id : null;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

function formatCOP(value) {
  return Number(value || 0).toLocaleString("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0
  });
}

function calcularZoom(radio) {
  if (!radio) return 14;
  if (radio <= 800) return 15;
  if (radio <= 1200) return 14;
  if (radio <= 2000) return 13;
  return 12;
}

/* ======================================================
   MAPA BASE
   ====================================================== */

function initMap(lat = 6.2442, lng = -75.5812, zoom = 12) {
  const mapaDiv = document.getElementById("mapa");
  if (!mapaDiv) return null;

  // Si ya existe, destruir para evitar bugs
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }

  mapInstance = L.map("mapa", {
    scrollWheelZoom: false
  }).setView([lat, lng], zoom);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap"
  }).addTo(mapInstance);

  markersLayer = L.layerGroup().addTo(mapInstance);

  // 🔑 Fix crítico para render correcto
  setTimeout(() => {
    mapInstance.invalidateSize();
  }, 200);

  return mapInstance;
}

/* ======================================================
   MARCADORES
   ====================================================== */

function getCustomMarkerIcon() {
  return L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
  });
}

function addMarker({ lat, lng, titulo, precio, url }) {
  if (!markersLayer) return null;

  const marker = L.marker([lat, lng], {
    icon: getCustomMarkerIcon()
  }).addTo(markersLayer);

  marker.bindPopup(`
    <strong>${titulo}</strong><br/>
    <span>${precio}</span><br/>
    <a href="${url}">Ver inmueble</a><br/>
    <small>Ubicación aproximada</small>
  `);

  return marker;
}

/* ======================================================
   MAPA DETALLE INMUEBLE
   ====================================================== */

async function cargarMapaDetalle() {
  const id = getInmuebleIdFromUrl();
  if (!id) return;

  const inmueble = await apiGet(`/api/inmuebles/${id}`);

  const lat = inmueble?.zona?.lat;
  const lng = inmueble?.zona?.lng;
  const radio = inmueble?.zona?.radio_m || 1200;

  if (!lat || !lng) return;

  initMap(lat, lng, calcularZoom(radio));

  addMarker({
    lat,
    lng,
    titulo: inmueble.titulo,
    precio: formatCOP(inmueble.precio_cop),
    url: inmueble.url_publica
  });

  // Círculo aproximado
  if (mapInstance) {
    L.circle([lat, lng], {
      radius: radio,
      color: "#2a7",
      fillOpacity: 0.12
    }).addTo(mapInstance);
  }
}

/* ======================================================
   MAPA LISTADO
   ====================================================== */

async function cargarMapaListado() {
  const data = await apiGet("/api/inmuebles");
  if (!Array.isArray(data) || !data.length) return;

  const first = data.find(x => x?.zona?.lat && x?.zona?.lng) || data[0];

  initMap(
    first?.zona?.lat || 6.2442,
    first?.zona?.lng || -75.5812,
    12
  );

  data.forEach((i) => {
    if (!i?.zona?.lat || !i?.zona?.lng) return;

    addMarker({
      lat: i.zona.lat,
      lng: i.zona.lng,
      titulo: i.titulo,
      precio: formatCOP(i.precio_cop),
      url: i.url_publica
    });
  });
}

/* ======================================================
   AUTO — ESPERA REAL AL DOM DINÁMICO
   ====================================================== */

document.addEventListener("DOMContentLoaded", () => {
  if (typeof L === "undefined") return;

  let intentos = 0;

  const waitForMap = setInterval(async () => {
    const mapaDiv = document.getElementById("mapa");
    intentos++;

    if (mapaDiv) {
      clearInterval(waitForMap);

      try {
        if (window.location.pathname.startsWith("/inmueble/")) {
          await cargarMapaDetalle();
        } else {
          await cargarMapaListado();
        }
      } catch (e) {
        console.warn("Mapa no disponible", e);
      }
    }

    if (intentos > 25) clearInterval(waitForMap);
  }, 150);
});
