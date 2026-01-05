function initMapaZona(zona) {
  if (!zona) return;

  const map = L.map("mapa").setView([zona.lat, zona.lng], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap"
  }).addTo(map);

  L.circle([zona.lat, zona.lng], {
    radius: zona.radio_m,
    color: "#2563eb",
    fillColor: "#3b82f6",
    fillOpacity: 0.25
  }).addTo(map);
}
