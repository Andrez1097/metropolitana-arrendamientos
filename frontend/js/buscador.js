// ===============================
// CONFIG
// ===============================
const API_BASE = "http://127.0.0.1:8000";

// ===============================
// HELPERS
// ===============================
function formatCOP(value) {
  const n = Number(value || 0);
  return n.toLocaleString("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0
  });
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

function getQueryParams() {
  const p = new URLSearchParams(window.location.search);
  const obj = {};
  for (const [k, v] of p.entries()) obj[k] = v;
  return obj;
}

// ===============================
// CARD DE INMUEBLE
// ===============================
function inmuebleCard(i) {
  const img = i.imagenes?.[0] || "";
  const zonaTxt = i.zona
    ? `${i.zona.nombre} · ${i.zona.ciudad}`
    : "Zona no disponible";

  return `
    <div class="card">
      <img src="${img}" alt="inmueble" />
      <div class="content">
        <div class="title">${i.titulo}</div>
        <div class="meta">
          ${zonaTxt} · ${i.tipo} · ${i.habitaciones} hab · ${i.banos} baños · ${i.area_m2} m²
        </div>
        <div class="price">${formatCOP(i.precio_cop)}</div>
        <div style="display:flex; gap:10px; margin-top:12px;">
          <a class="btn" href="./inmueble.html?id=${i.id}">Ver detalle</a>
          ${
            i.zona
              ? `<a class="btn secondary" href="./listado.html?zona=${encodeURIComponent(i.zona.nombre)}">Más en la zona</a>`
              : ""
          }
        </div>
      </div>
    </div>
  `;
}

// ===============================
// INDEX.HTML – CARGA ZONAS
// ===============================
async function loadZonasToSelect() {
  const select = document.getElementById("zona");
  if (!select) return;

  try {
    const zonas = await apiGet("/api/zonas");
    zonas.forEach(z => {
      const opt = document.createElement("option");
      opt.value = z.nombre;
      opt.textContent = `${z.nombre} (${z.ciudad})`;
      select.appendChild(opt);
    });
  } catch (e) {
    console.warn("No se pudieron cargar zonas:", e);
  }
}

// ===============================
// INDEX.HTML – DESTACADOS
// ===============================
async function loadDestacados() {
  const cont = document.getElementById("destacados");
  if (!cont) return;

  try {
    const data = await apiGet("/api/inmuebles");
    cont.innerHTML = data.slice(0, 6).map(inmuebleCard).join("");
  } catch (e) {
    cont.innerHTML = `
      <div style="color:var(--muted);">
        No se pudieron cargar inmuebles destacados.
      </div>
    `;
  }
}

// ===============================
// LISTADO.HTML – RESULTADOS
// ===============================
async function loadListado() {
  const cards = document.getElementById("cards");
  const resumen = document.getElementById("resumen");
  if (!cards || !resumen) return;

  const q = getQueryParams();

  try {
    let data = await apiGet("/api/inmuebles");

    // FILTROS FRONTEND
    if (q.zona) {
      data = data.filter(i => i.zona?.nombre === q.zona);
    }

    if (q.tipo) {
      data = data.filter(i => i.tipo === q.tipo);
    }

    if (q.precio) {
      data = data.filter(i => i.precio_cop <= Number(q.precio));
    }

    if (q.hab) {
      data = data.filter(i => i.habitaciones >= Number(q.hab));
    }

    resumen.textContent = `${data.length} resultado(s)`;

    cards.innerHTML = data.length
      ? data.map(inmuebleCard).join("")
      : `<div style="color:var(--muted);">No hay resultados con esos filtros.</div>`;

  } catch (e) {
    cards.innerHTML = `
      <div style="color:var(--muted);">
        No se pudieron cargar resultados. Backend apagado o CORS.
      </div>
    `;
  }
}

// ===============================
// INMUEBLE.HTML – DETALLE
// ===============================
async function loadDetalle() {
  const cont = document.getElementById("detalle");
  if (!cont) return;

  const { id } = getQueryParams();
  if (!id) {
    cont.innerHTML = `<div style="color:var(--muted);">Falta el parámetro <b>id</b>.</div>`;
    return;
  }

  try {
    const i = await apiGet(`/api/inmuebles/${id}`);
    const imgs = i.imagenes || [];
    const main = imgs[0] || "";

    cont.innerHTML = `
      <div class="row">
        <div class="left">
          <div class="gallery">
            <img src="${main}" alt="principal" />
          </div>

          <h2>${i.titulo}</h2>
          <div class="meta">
            ${i.zona?.nombre || ""} · ${i.zona?.ciudad || ""} · ${i.tipo}
          </div>

          <div class="price">${formatCOP(i.precio_cop)}</div>

          <div class="kv">
            <div class="box"><div class="k">Área</div><div class="v">${i.area_m2} m²</div></div>
            <div class="box"><div class="k">Habitaciones</div><div class="v">${i.habitaciones}</div></div>
            <div class="box"><div class="k">Baños</div><div class="v">${i.banos}</div></div>
          </div>

          <div class="panel">
            <h3>Descripción</h3>
            <div style="color:var(--muted); white-space:pre-line;">
              ${i.descripcion}
            </div>
          </div>

          <div class="panel">
            <h3>Referencia de ubicación</h3>
            <div style="color:var(--muted);">
              ${i.direccion_referencia}<br/>
              <small>Ubicación exacta no revelada.</small>
            </div>
          </div>
        </div>

        <div class="right">
          <div class="panel">
            <h3>Contacto</h3>
            <a class="btn" id="btnWa">Contactar por WhatsApp</a>
          </div>

          <div class="panel">
            <h3>Mapa por zona</h3>
            <div id="map" class="map"></div>
          </div>
        </div>
      </div>
    `;

    // WhatsApp
    const wa = document.getElementById("btnWa");
    const msg = encodeURIComponent(i.contacto_whatsapp || `Hola, me interesa el inmueble ID ${i.id}`);
    wa.href = `https://wa.me/?text=${msg}`;

    // Mapa
    if (i.zona) {
      renderZonaMap("map", i.zona.lat, i.zona.lng, i.zona.radio_m, i.zona.nombre);
    }

  } catch (e) {
    cont.innerHTML = `
      <div style="color:var(--muted);">
        No se pudo cargar el inmueble. Verifica el backend.
      </div>
    `;
  }
}

// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", async () => {
  await loadZonasToSelect();
  await loadDestacados();
  await loadListado();
  await loadDetalle();
});
