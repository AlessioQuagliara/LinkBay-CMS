// API PER IL RICEVIMENTO DATI ----------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    loadRecentOrders();
    loadRecentCustomers();
    loadActivityFeed();
    loadBestSellingProducts();
    
    // Chiamiamo il grafico SOLO se non è già in fase di caricamento
    if (!window.salesChartLoading) {
        renderSalesChart();
    }

    function loadRecentOrders() {
        fetch("/api/latest-orders")
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById("latestOrdersList");
                list.innerHTML = "";

                if (data.success && data.orders.length > 0) {
                    data.orders.forEach(order => {
                        list.innerHTML += `
                            <li class="list-group-item">
                                <strong>#${order.order_number}</strong> - ${order.status} - 
                                <span class="text-success fw-bold">${order.total_amount.toFixed(2)} €</span>
                                <br>
                                <small class="text-muted">
                                    ${order.customer_name ? `👤 ${order.customer_name} | ` : ""}
                                    📅 ${order.created_at}
                                </small>
                            </li>`;
                    });
                } else {
                    list.innerHTML = `<li class="list-group-item text-muted">No recent orders.</li>`;
                }
            })
            .catch(error => console.error("Error fetching latest orders:", error));
    }    

    function loadRecentCustomers() {
        fetch("/api/recent-customers")
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById("recentCustomersList");
                list.innerHTML = "";

                if (data.success && data.customers.length > 0) {
                    data.customers.forEach(customer => {
                        list.innerHTML += `
                            <li class="list-group-item">
                                <i class="fa-solid fa-user text-primary"></i> 
                                <strong>${customer.name}</strong> - 
                                <a href="mailto:${customer.email}" class="text-decoration-none">${customer.email}</a>
                                <br>
                                <small class="text-muted">📞 ${customer.phone} | 📅 ${customer.created_at}</small>
                            </li>`;
                    });
                } else {
                    list.innerHTML = `<li class="list-group-item text-muted">No recent customers found.</li>`;
                }
            })
            .catch(error => console.error("Error fetching recent customers:", error));
    }
});

document.addEventListener("DOMContentLoaded", function () {
    renderSalesChart();

    function renderSalesChart() {
        fetch("/api/sales-data")
            .then(response => response.json())
            .then(data => {
                if (!data.success || !data.dates || data.dates.length === 0) {
                    console.warn("⚠️ No sales data available.");
                    return;
                }

                // Assicuriamoci che il canvas esista prima di procedere
                const canvas = document.getElementById("salesChart");
                if (!canvas) {
                    console.error("❌ Errore: Canvas per il grafico vendite non trovato!");
                    return;
                }

                // Assicuriamoci che il container abbia dimensioni corrette
                const container = canvas.parentElement;
                container.style.height = "300px"; // Forza un'altezza per il grafico

                const ctx = canvas.getContext("2d");

                // Se un grafico esiste già, distruggilo prima di crearne uno nuovo
                if (window.salesChartInstance) {
                    window.salesChartInstance.destroy();
                    console.log("❌ Vecchio grafico rimosso.");
                }

                // Creazione del nuovo grafico
                window.salesChartInstance = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: data.dates,
                        datasets: [{
                            label: "Sales (€)",
                            data: data.sales,
                            borderColor: "#ff5757",
                            backgroundColor: "rgba(255, 87, 87, 0.2)",
                            borderWidth: 2,
                            tension: 0.4, // Rende il grafico più fluido
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: "#ff5757"
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                title: { display: true, text: "Date" },
                                ticks: { autoSkip: true, maxTicksLimit: 7 }
                            },
                            y: {
                                title: { display: true, text: "Sales (€)" },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        return `Sales: €${tooltipItem.raw.toLocaleString()}`;
                                    }
                                }
                            }
                        }
                    }
                });

                console.log("✅ Grafico vendite aggiornato.");
            })
            .catch(error => {
                console.error("❌ Errore nel caricamento dei dati del grafico vendite:", error);
            });
    }
});

// API PER CHAT CON INTELLIGENZA ARTIFICIALE -----------------------------------------------------------------------------

// Carica la chat salvata da localStorage al caricamento della pagina
document.addEventListener("DOMContentLoaded", function() {
    loadChatHistory();
});

// Funzione per salvare la chat corrente in localStorage
function saveChatHistory() {
    const chatBox = document.getElementById("chat-box");
    localStorage.setItem("chatHistory", chatBox.innerHTML);
}

// Funzione per caricare la chat da localStorage
function loadChatHistory() {
    const chatBox = document.getElementById("chat-box");
    const savedChat = localStorage.getItem("chatHistory");
    if (savedChat) {
        chatBox.innerHTML = savedChat;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Funzione che esegue l'invio del messaggio
async function sendMessage() {
    const userInputField = document.getElementById('user-input');
    const userInput = userInputField.value.trim();
    if (!userInput) {
        alert("Please enter a valid query.");
        return;
    }
    
    const chatBox = document.getElementById('chat-box');

    // Aggiunge il messaggio utente alla chat
    const userMessage = document.createElement("div");
    userMessage.classList.add("alert", "alert-danger", "p-2");
    userMessage.innerHTML = `<strong>You:</strong> ${userInput}`;
    chatBox.appendChild(userMessage);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll automatico
    saveChatHistory();

    // Prepara il messaggio del bot con il container per l'animazione
    const botMessage = document.createElement("div");
    botMessage.classList.add("alert", "alert-secondary", "p-2");
    const typingSpan = document.createElement("span");
    botMessage.innerHTML = `<strong>LinkBayCMS AI:</strong> `;
    botMessage.appendChild(typingSpan);
    chatBox.appendChild(botMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
    saveChatHistory();

    // Resetta il campo input
    userInputField.value = "";

    // Avvia l'animazione dei tre puntini (simile a WhatsApp)
    let dotInterval = setInterval(() => {
        if (typingSpan.innerHTML.length < 3) {
            typingSpan.innerHTML += '.';
        } else {
            typingSpan.innerHTML = '';
        }
    }, 500);

    try {
        const response = await fetch('/assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userInput })
        });
        
        const data = await response.json();
        
        // Ferma l'animazione dei puntini
        clearInterval(dotInterval);
        
        if (response.ok) {
            // Anima la scrittura della risposta lettera per lettera
            typeText(typingSpan, data.response, () => {
                botMessage.innerHTML = `<strong>LinkBayCMS AI:</strong> ${data.response}`;
                chatBox.scrollTop = chatBox.scrollHeight;  // Scroll automatico dopo risposta
                saveChatHistory();
            });
        } else {
            botMessage.innerHTML = `<strong>LinkBayCMS AI:</strong> <span class="text-danger">Error processing your request.</span>`;
            saveChatHistory();
        }
    } catch (error) {
        console.error("Error:", error);
        botMessage.innerHTML = `<strong>LinkBayCMS AI:</strong> <span class="text-danger">An unexpected error occurred.</span>`;
        saveChatHistory();
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll automatico
}

// Collega il tasto send al click
document.getElementById('send-btn').addEventListener('click', sendMessage);

// Collega l'evento "Enter" sul campo input
document.getElementById('user-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

// Funzione per animare il typing (digitazione lettera per lettera)
function typeText(element, text, callback) {
    let i = 0;
    element.innerHTML = "";  // Resetta il testo
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, 30);  // Velocità di digitazione (30ms per carattere)
        } else if (callback) {
            callback();
        }
    }
    type();
}

// API PER CONTARE E STAMPARE IL NUMERO DEI VISITATORI ------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    let visitorMap = L.map("map-container").setView([20, 0], 2); // Centro approssimativo

    // Stile futuristico per la mappa (sfondo scuro)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
        maxZoom: 10,
    }).addTo(visitorMap);

    let markersLayer = L.layerGroup().addTo(visitorMap);

    function updateVisitors() {
        fetch("/api/get-site-visits")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("active-visitors").textContent = data.visits.length;
                    document.getElementById("last-update").textContent = "Last updated " + new Date().toLocaleTimeString();

                    // Rimuove i marker vecchi
                    markersLayer.clearLayers();

                    data.visits.forEach(visit => {
                        if (visit.latitude && visit.longitude) {
                            L.circleMarker([visit.latitude, visit.longitude], {
                                radius: 6,
                                fillColor: "#ff5757",
                                color: "#fff",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            }).addTo(markersLayer)
                            .bindPopup(`<strong>IP:</strong> ${visit.ip_address} <br> <small>${visit.page_url}</small>`);
                        }
                    });
                } else {
                    console.error("Error:", data.error);
                }
            })
            .catch(error => console.error("Error fetching visitor data:", error));
    }

    updateVisitors();  // Aggiorna all'inizio
    setInterval(updateVisitors, 10000);  // Aggiorna ogni 10 secondi
});


// SUBSCRIPTION -----------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    function loadSubscriptionStatus() {
        fetch("/api/get-subscription-status", { credentials: "include" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("plan-name").textContent = data.plan_name;
                    document.getElementById("renewal-date").textContent = data.renewal_date;
                    document.getElementById("subscription-status-text").textContent = data.status;

                    // Mostra avviso se l'abbonamento sta per scadere o è scaduto
                    if (data.status === "expiring" || data.status === "canceled") {
                        document.getElementById("subscription-alert").classList.remove("d-none");
                    }
                } else {
                    document.getElementById("subscription-status-text").textContent = "Error loading subscription";
                }
            })
            .catch(error => console.error("Error fetching subscription data:", error));
    }

    document.getElementById("renew-subscription").addEventListener("click", function () {
        window.location.href = "/billing"; // Reindirizza alla pagina di pagamento
    });

    loadSubscriptionStatus();
});

// API PER ORDINARE LE CARD DINAMICHE ----------------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {
    const sectionsContainer = document.getElementById('sortable-sections-grid');
    const homepagePreferencesKey = 'homepageLayoutPreferences';

    // 🔹 Definizione delle sezioni disponibili sulla homepage
    const sections = [
        { id: 'assistant-container', label: 'AI Assistant', icon: 'fa-robot'},
        { id: 'subscription-status', label: 'Subscription', icon: 'fa-box-open' },
        { id: 'visitor-map', label: 'Visit Tracker', icon: 'fa-store' },
        { id: 'sales-chart', label: 'Sales Chart', icon: 'fa-chart-line' },
        { id: 'latest-orders', label: 'Latest Orders', icon: 'fa-clipboard-list' },
        { id: 'recent-customers', label: 'Recent Customers', icon: 'fa-users' },
        { id: 'activity-feed', label: 'Activity Feed', icon: 'fa-bell' },
        { id: 'best-selling-products', label: 'Best Selling Products', icon: 'fa-star' }
    ];

    function renderSectionOptions(preferences) {
        sectionsContainer.innerHTML = '';

        // 🔹 Usa l'ordine salvato o l'ordine di default
        const orderedSections = preferences.order || sections.map(sec => sec.id);

        orderedSections.forEach(sectionId => {
            const section = sections.find(sec => sec.id === sectionId);
            if (!section) return;

            const isChecked = preferences[section.id] ?? true;
            const sectionItem = document.createElement('div');
            sectionItem.classList.add('grid-item');
            if (section.fullWidth) sectionItem.classList.add('full-width');
            sectionItem.dataset.section = section.id;

            sectionItem.innerHTML = `
                <i class="fa-solid ${section.icon}"></i>
                <span>${section.label}</span>
                <input class="form-check-input section-toggle" type="checkbox" value="${section.id}" ${isChecked ? 'checked' : ''}>
            `;
            sectionsContainer.appendChild(sectionItem);
        });

        // 🔹 Aggiunge il listener per aggiornare la visibilità automaticamente
        document.querySelectorAll('.section-toggle').forEach(toggle => {
            toggle.addEventListener('change', function () {
                savePreferences();
                applyPreferences(loadPreferences());
            });
        });

        // 🔹 Rendi il contenitore delle sezioni ordinabile
        new Sortable(sectionsContainer, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function () {
                savePreferences(); // Salva il nuovo ordine
                applyPreferences(loadPreferences());
            }
        });
    }

    function savePreferences() {
        const preferences = { order: [] };
        document.querySelectorAll('#sortable-sections-grid .grid-item').forEach(item => {
            const sectionId = item.dataset.section;
            const checkbox = item.querySelector('.section-toggle');
            preferences[sectionId] = checkbox.checked;
            preferences.order.push(sectionId);
        });
        localStorage.setItem(homepagePreferencesKey, JSON.stringify(preferences));
    }

    function loadPreferences() {
        return JSON.parse(localStorage.getItem(homepagePreferencesKey)) || {};
    }

    function applyPreferences(preferences) {
        const orderedSections = preferences.order || sections.map(sec => sec.id);

        // 🔹 Riordina le sezioni nella homepage
        const homepageContainer = document.querySelector('.row[data-aos="fade-up"]');
        orderedSections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) homepageContainer.appendChild(section);
        });

        // 🔹 Nasconde/mostra le sezioni in base alle preferenze
        sections.forEach(section => {
            const isChecked = preferences[section.id] ?? true;
            const sectionElement = document.getElementById(section.id);
            if (sectionElement) {
                sectionElement.style.display = isChecked ? '' : 'none';
            }
        });

        // 🔹 Gestisce il layout delle sezioni
        applyGridLayout();
    }

    function applyGridLayout() {
        const firstSection = document.querySelector('.row[data-aos="fade-up"] > div:first-child');
        if (firstSection) firstSection.classList.add('col-12');

        document.querySelectorAll('.row[data-aos="fade-up"] > div:not(:first-child)').forEach(div => {
            div.classList.add('col-md-6');
        });
    }

    // 🚀 Inizializzazione
    const savedPreferences = loadPreferences();
    renderSectionOptions(savedPreferences);
    applyPreferences(savedPreferences);
});