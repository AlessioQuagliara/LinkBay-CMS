document.addEventListener('DOMContentLoaded', () => {
  loadSupportTickets();

  document.getElementById('ticketForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
      shop_name: form.shop_name.value.trim(),
      title: form.title.value.trim(),
      category: form.category.value,
      priority: form.priority.value,
      message: form.message.value.trim()
    };

    try {
      const res = await fetch('/api/create_ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const result = await res.json();
      if (result.success) {
        Swal.fire('Successo', 'Ticket aperto con successo!', 'success');
        form.reset();
        loadSupportTickets();
        const modal = bootstrap.Modal.getInstance(document.getElementById('newTicketModal'));
        modal.hide();
      } else {
        Swal.fire('Errore', result.message || 'Errore imprevisto', 'error');
      }
    } catch (err) {
      console.error(err);
      Swal.fire('Errore', 'Errore di connessione al server.', 'error');
    }
  });
});

async function loadSupportTickets() {
const container = document.getElementById('ticketList');
  if (!container) return;

  container.innerHTML = '<p>Caricamento ticket...</p>';
  try {
    const res = await fetch('/api/my_tickets');
    const result = await res.json();

    if (!res.ok || !result.success || !Array.isArray(result.data)) {
        container.innerHTML = '<p>Errore durante il recupero dei ticket.</p>';
        return;
      }

    if (result.data.length === 0) {
        container.innerHTML = '<p>Nessun ticket aperto.</p>';
        return;
      }

    container.innerHTML = '';
    result.data.forEach(ticket => {
      const div = document.createElement('div');
      div.className = 'card mb-3 shadow-sm';
      div.innerHTML = `
        <div class="card-body">
          <div class="card-header bg-light border-0">
            <h5 class="card-title mb-0">${ticket.title}</h5>
          </div>
          <div class="card-body">
            <p class="card-text text-muted">
              ${ticket.category} 
            </p>
            <p class="card-text text-muted">
            Priorità: ${
                ticket.priority === 'low' ? '<span class="badge bg-success"><i class="fa-solid fa-arrow-down me-1"></i> Bassa</span>' :
                ticket.priority === 'normal' ? '<span class="badge bg-primary"><i class="fa-solid fa-arrow-right me-1"></i> Normale</span>' :
                ticket.priority === 'high' ? '<span class="badge bg-warning text-dark"><i class="fa-solid fa-arrow-up me-1"></i> Alta</span>' :
                ticket.priority === 'critical' ? '<span class="badge bg-danger"><i class="fa-solid fa-fire me-1"></i> Critica</span>' :
                `<span class="badge bg-secondary">${ticket.priority}</span>`
              }
            </p>
            <p class="card-text">${ticket.message.slice(0, 60)}${ticket.message.length > 60 ? '...' : ''}</p>
            <p class="card-text">
              <small class="text-muted">
                Stato:
                ${
                  ticket.status === 'open' ? '<span class="badge bg-danger"><i class="fa-solid fa-circle-exclamation me-1"></i> Aperto</span>' :
                  ticket.status === 'in_progress' ? '<span class="badge bg-warning text-dark"><i class="fa-solid fa-spinner me-1"></i> In lavorazione</span>' :
                  ticket.status === 'closed' ? '<span class="badge bg-success"><i class="fa-solid fa-circle-check me-1"></i> Chiuso</span>' :
                  `<span class="badge bg-secondary">${ticket.status}</span>`
                }
              </small>
            </p>
          </div>
          <div class="card-footer bg-white border-0 d-flex justify-content-end gap-2">
            <a class="btn btn-outline-danger btn-sm" href="/dashboard/support/chat/${ticket.id}">
              <i class="fa-solid fa-comments me-1"></i> Apri Chat
            </a>
            <button class="btn btn-outline-secondary btn-sm" onclick='showTicketModal(${JSON.stringify(ticket)})'>
              <i class="fa-solid fa-eye me-1"></i> Visualizza Ticket
            </button>
            <button class="btn btn-outline-dark btn-sm" onclick="deleteTicket(${ticket.id})">
              <i class="fa-solid fa-trash me-1"></i> Elimina Ticket
            </button>
          </div>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error(err);
    container.innerHTML = '<p>Errore durante il caricamento dei ticket.</p>';
  }
}

async function loadTicketChat(ticketId) {
  try {
    const res = await fetch(`/api/ticket_messages/${ticketId}`);
    const result = await res.json();

    if (!result.success) {
      Swal.fire('Errore', result.message || 'Errore nel caricamento dei messaggi.', 'error');
      return;
    }

    const modal = new bootstrap.Modal(document.getElementById('chatModal'));
    document.getElementById('chatTicketId').value = ticketId;
    const chatBody = document.getElementById('chatMessages');
    chatBody.innerHTML = '';

    result.messages.forEach(msg => {
      const div = document.createElement('div');
      div.className = `chat-message ${msg.sender_role === 'user' ? 'text-start' : 'text-end'}`;
      div.innerHTML = `
        <div class="p-2 rounded bg-light mb-2 d-inline-block">
          <small class="text-muted">${msg.sender_role}</small><br>
          ${msg.message}
        </div>
      `;
      chatBody.appendChild(div);
    });

    modal.show();
  } catch (err) {
    console.error(err);
    Swal.fire('Errore', 'Errore di rete durante il caricamento della chat.', 'error');
  }
}

document.getElementById('chatForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const ticketId = document.getElementById('chatTicketId').value;
  const message = document.getElementById('chatInput').value.trim();

  if (!message) return;

  try {
    const res = await fetch(`/api/ticket_messages/${ticketId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const result = await res.json();

    if (result.success) {
      document.getElementById('chatInput').value = '';
      loadTicketChat(ticketId);
    } else {
      Swal.fire('Errore', result.message || 'Impossibile inviare messaggio.', 'error');
    }
  } catch (err) {
    console.error(err);
    Swal.fire('Errore', 'Errore di rete durante l\'invio del messaggio.', 'error');
  }
});

async function deleteTicket(ticketId) {
  const confirm = await Swal.fire({
    title: 'Sei sicuro?',
    text: 'Questa azione eliminerà definitivamente il ticket.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sì, elimina',
    cancelButtonText: 'Annulla'
  });

  if (confirm.isConfirmed) {
    try {
      const res = await fetch(`/api/delete_ticket/${ticketId}`, {
        method: 'DELETE'
      });
      const result = await res.json();

      if (result.success) {
        Swal.fire('Eliminato!', 'Il ticket è stato eliminato.', 'success');
        loadSupportTickets();
      } else {
        Swal.fire('Errore', result.message || 'Errore durante l\'eliminazione.', 'error');
      }
    } catch (err) {
      console.error(err);
      Swal.fire('Errore', 'Errore durante l\'eliminazione del ticket.', 'error');
    }
  }
}

function showTicketModal(ticket) {
  const modalTitle = document.getElementById('ticketModalTitle');
  const modalBody = document.getElementById('ticketModalBody');

  if (modalTitle && modalBody) {
    modalTitle.textContent = ticket.title;
    modalBody.innerHTML = `
      <p><strong>Negozio:</strong> ${ticket.shop_name}</p>
      <p><strong>Categoria:</strong> ${ticket.category}</p>
      <p><strong>Priorità:</strong> ${ticket.priority}</p>
      <p><strong>Messaggio:</strong><br>${ticket.message}</p>
      <p><strong>Stato:</strong> ${ticket.status}</p>
    `;
    const modal = new bootstrap.Modal(document.getElementById('ticketModal'));
    modal.show();
  }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
      const res = await fetch("/api/user_shops_sales");
      const data = await res.json();

      const select = document.getElementById("shopNameSelect");
      select.innerHTML = '<option selected disabled>-- Seleziona --</option>';

      if (data && Array.isArray(data.data) && data.data.length > 0) {
        data.data.forEach(shop => {
          const option = document.createElement("option");
          option.value = shop.shop_name;
          option.textContent = `${shop.shop_name} (${shop.shop_type})`;
          select.appendChild(option);
        });
      } else {
        const option = document.createElement("option");
        option.disabled = true;
        option.textContent = "Nessun negozio trovato";
        select.appendChild(option);
      }
    } catch (err) {
      console.error("Errore nel caricamento dei negozi:", err);
      const select = document.getElementById("shopNameSelect");
      select.innerHTML = '<option disabled>Errore nel caricamento</option>';
    }
  });

  async function loadTicketChat(ticketId) {
    document.getElementById('currentTicketId').value = ticketId;
    document.getElementById('chatMessages').innerHTML = '<p>Caricamento messaggi...</p>';
    const chatModal = new bootstrap.Modal(document.getElementById('chatModal'));
    chatModal.show();

    try {
      const res = await fetch(`/api/ticket_messages/${ticketId}`);
      const result = await res.json();

      if (result.success && Array.isArray(result.messages)) {
        const chatBox = document.getElementById('chatMessages');
        chatBox.innerHTML = '';

        result.messages.forEach(msg => {
          const div = document.createElement('div');
          div.className = `alert ${msg.sender_role === 'user' ? 'alert-secondary text-end' : 'alert-danger text-start'}`;
          div.innerHTML = `<small class="d-block">${msg.created_at}</small><strong>${msg.sender_role}:</strong> ${msg.message}`;
          chatBox.appendChild(div);
        });

        chatBox.scrollTop = chatBox.scrollHeight;
      } else {
        document.getElementById('chatMessages').innerHTML = '<p>Nessun messaggio presente.</p>';
      }
    } catch (err) {
      document.getElementById('chatMessages').innerHTML = '<p>Errore nel caricamento messaggi.</p>';
      console.error(err);
    }
  }

  document.getElementById('chatForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    const ticketId = document.getElementById('currentTicketId').value;

    if (!input.value.trim()) return;

    try {
      const res = await fetch(`/api/ticket_messages/${ticketId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input.value.trim() })
      });

      const result = await res.json();

      if (result.success) {
        input.value = '';
        loadTicketChat(ticketId);
      } else {
        Swal.fire('Errore', result.message || 'Impossibile inviare il messaggio.', 'error');
      }
    } catch (err) {
      console.error(err);
      Swal.fire('Errore', 'Errore di connessione con il server.', 'error');
    }
  });
