function createChatbotUI() {
  const root = document.getElementById("chatbot");
  if (!root) return;

  root.innerHTML = `
    <div class="chatbot-header">
      <div class="title">Asistente · Metropolitana</div>
      <div style="display:flex; gap:8px;">
        <button id="chatToggle">Abrir</button>
      </div>
    </div>
    <div class="chatbot-body" id="chatBody"></div>
    <div class="chatbot-footer">
      <input id="chatInput" placeholder="Escribe: 'apto en Laureles hasta 2.5M'..." />
      <button id="chatSend">Enviar</button>
    </div>
  `;

  const body = document.getElementById("chatBody");
  addBot("Hola 👋 Soy tu asistente. Dime zona, tipo y presupuesto para ayudarte.");

  const toggleBtn = document.getElementById("chatToggle");
  toggleBtn.addEventListener("click", () => {
    root.classList.toggle("chatbot-collapsed");
    toggleBtn.textContent = root.classList.contains("chatbot-collapsed") ? "Abrir" : "Cerrar";
  });

  document.getElementById("chatSend").addEventListener("click", sendMessage);
  document.getElementById("chatInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  function addUser(text) {
    const div = document.createElement("div");
    div.className = "bubble user";
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function addBot(text) {
    const div = document.createElement("div");
    div.className = "bubble bot";
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  async function sendMessage() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (!msg) return;

    addUser(msg);
    input.value = "";

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      addBot(data.reply || "No entendí. ¿Me repites?");
    } catch (e) {
      addBot("No puedo conectar al servidor ahora. Verifica que el backend esté encendido.");
    }
  }
}

document.addEventListener("DOMContentLoaded", createChatbotUI);
