// Widget di chat pubblico sulla landing (app/templates/landing/partials/chat-widget.html).
// Cronologia tenuta solo lato client (nessuna sessione/persistenza server —
// vedi app/chat/routes.py): ogni richiesta rimanda gli ultimi turni.
(function () {
  "use strict";

  const script = document.getElementById("chat-widget-script");
  if (!script) return;

  const ASK_URL = script.dataset.askUrl;
  const LANG = script.dataset.lang || "en";

  const STRINGS = {
    en: {
      error: "Sorry, something went wrong. Please try again in a moment.",
      rateLimited: "You're asking a lot of questions! Please wait a minute and try again.",
      thinking: "Typing…",
    },
    it: {
      error: "Si è verificato un errore. Riprova tra poco.",
      rateLimited: "Stai facendo tante domande! Aspetta un minuto e riprova.",
      thinking: "Sta scrivendo…",
    },
  };
  const t = (key) => (STRINGS[LANG] && STRINGS[LANG][key]) || STRINGS.en[key];

  const toggle = document.getElementById("chat-widget-toggle");
  const panel = document.getElementById("chat-widget-panel");
  const iconOpen = document.getElementById("chat-widget-icon-open");
  const iconClose = document.getElementById("chat-widget-icon-close");
  const messages = document.getElementById("chat-widget-messages");
  const form = document.getElementById("chat-widget-form");
  const input = document.getElementById("chat-widget-input");

  let history = []; // [{role, content}, ...] — solo client-side
  let open = false;
  let busy = false;

  // Escape anche di " e ': il risultato finisce pure dentro attributi
  // (title/href/data-*) con dati di Search Console scritti da terzi.
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function setOpen(next) {
    open = next;
    panel.classList.toggle("hidden", !open);
    iconOpen.classList.toggle("hidden", open);
    iconClose.classList.toggle("hidden", !open);
    toggle.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
  }

  function appendBubble(role, text) {
    const wrap = document.createElement("div");
    wrap.className = "chat " + (role === "user" ? "chat-end" : "chat-start");
    const bubbleClass = role === "user" ? "chat-bubble" : "chat-bubble chat-bubble-error text-white";
    wrap.innerHTML = `<div class="${bubbleClass} text-sm">${esc(text)}</div>`;
    messages.appendChild(wrap);
    messages.scrollTop = messages.scrollHeight;
    return wrap;
  }

  toggle.addEventListener("click", () => setOpen(!open));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || busy) return;

    input.value = "";
    appendBubble("user", text);
    const thinking = appendBubble("assistant", t("thinking"));
    busy = true;

    try {
      const res = await fetch(ASK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history }),
      });

      if (res.status === 429) {
        thinking.querySelector(".chat-bubble").textContent = t("rateLimited");
      } else if (!res.ok) {
        thinking.querySelector(".chat-bubble").textContent = t("error");
      } else {
        const data = await res.json();
        thinking.querySelector(".chat-bubble").textContent = data.reply;
        history.push({ role: "user", content: text });
        history.push({ role: "assistant", content: data.reply });
        history = history.slice(-8); // stesso limite lato server, evita payload che crescono all'infinito
      }
    } catch (err) {
      thinking.querySelector(".chat-bubble").textContent = t("error");
    } finally {
      busy = false;
      messages.scrollTop = messages.scrollHeight;
    }
  });
})();
