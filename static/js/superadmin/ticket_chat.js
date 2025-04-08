document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatMessages");
  const sendForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("chatMessageInput");
  const ticketId = window.location.pathname.split("/").pop(); // ticket ID dalla URL

  async function loadMessages() {
    try {
      const res = await fetch(`/api/ticket_messages/${ticketId}`);
      const data = await res.json();

      if (!res.ok || !data.success || !Array.isArray(data.messages)) {
        chatBox.innerHTML = '<p class="text-muted">Errore durante il caricamento dei messaggi.</p>';
        return;
      }

      chatBox.innerHTML = "";
      if (data.messages.length === 0) {
        chatBox.innerHTML = '<p class="text-muted text-center mt-3">Nessun messaggio ancora.</p>';
      } else {
        data.messages.forEach(msg => {
          const msgDiv = document.createElement("div");
          msgDiv.className = `mb-3 ${msg.sender_role === "user" ? "text-end" : "text-start"}`;
          msgDiv.innerHTML = `
            <div class="d-inline-block p-2 rounded ${msg.sender_role === "user" ? "bg-danger text-white" : "bg-light border" }">
              <div class="small">${msg.message}</div>
              <div class="small text-muted text-end mt-1">${msg.created_at}</div>
            </div>
          `;
          chatBox.appendChild(msgDiv);
        });
      }

      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
      console.error("Errore nel caricamento della chat:", err);
      chatBox.innerHTML = '<p class="text-danger">Errore di rete. Riprova.</p>';
    }
  }

  async function sendMessage(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    try {
      const res = await fetch(`/api/ticket_messages/${ticketId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      const result = await res.json();
      if (res.ok && result.success) {
        messageInput.value = "";
        await loadMessages();
      } else {
        console.error("Errore nell'invio del messaggio:", result.message);
        Swal.fire("Errore", result.message || "Errore nell'invio del messaggio.", "error");
      }
    } catch (err) {
      console.error("Errore di connessione:", err);
      Swal.fire("Errore", "Connessione al server non riuscita.", "error");
    }
  }

  sendForm.addEventListener("submit", sendMessage);

  // Carica i messaggi ogni 5 secondi
  loadMessages();
  setInterval(loadMessages, 5000);
});
