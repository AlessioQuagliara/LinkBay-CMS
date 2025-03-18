document.addEventListener("DOMContentLoaded", function () {
    var editor = grapesjs.init({
        container: '#editor',
        height: '100vh',
        width: '100%',
        storageManager: false,
        fromElement: true,
        plugins: [],
        blockManager: false, // 🔥 Disabilita la UI GrapesJS
        panels: { defaults: [] },
        styleManager: { sectors: [] },
        layerManager: false,
        traitManager: false,
        canvas: {
            styles: [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css'
            ],
            scripts: [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
            ]
        }
    });

    // 🔹 Recupera gli stili salvati dal server
    async function loadStyles() {
        try {
            const pageID = window.pageID; // Assumiamo che il page ID sia definito in un <script> nell'HTML
            const response = await fetch(`/api/get-page-styles/${pageID}`);
            const data = await response.json();

            if (data.success && data.styles) {
                editor.setStyle(data.styles);
            } else {
                console.warn("⚠️ Nessun stile trovato per questa pagina.");
            }
        } catch (error) {
            console.error("❌ Errore nel recupero degli stili:", error);
        }
    }

    loadStyles(); // Chiama la funzione per caricare gli stili
    
    let selectedComponent = null;



    

    // Gestione dei pulsanti Undo/Redo
    document.getElementById('undo-btn').addEventListener('click', () => {
        editor.UndoManager.undo();
    });
    
    document.getElementById('redo-btn').addEventListener('click', () => {
        editor.UndoManager.redo();
    });

    // 🔹 Pulsante per il fullscreen
    const fullscreenBtn = document.getElementById("toggleFullscreen");

    fullscreenBtn.addEventListener("click", () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log("Fullscreen non supportato:", err);
            });
            fullscreenBtn.innerHTML = "⏏ Exit";
        } else {
            document.exitFullscreen();
            fullscreenBtn.innerHTML = "⛶ Zen Mode";
        }
    });

    


    editor.on("component:selected", function (component) {
        selectedComponent = component;
        updateStyleControls(component);
    });

    function updateStyleControls(component) {
        if (!component) return;

        const styles = component.getStyle();

        document.getElementById("bg-color-select").value = styles["background-color"] || "#ffffff";
        document.getElementById("bg-image-select").value = styles["background-image"] ? styles["background-image"].replace(/url\(['"]?(.*?)['"]?\)/, '$1') : "";
        document.getElementById("text-color-select").value = styles["color"] || "#000000";
        document.getElementById("text-shadow-select").value = styles["text-shadow"] || "";
        document.getElementById("font-size-range").value = parseInt(styles["font-size"]) || 16;
        document.getElementById("border-select").value = styles["border"] || "";
        document.getElementById("border-radius-range").value = parseInt(styles["border-radius"]) || 0;
        document.getElementById("box-shadow-select").value = styles["box-shadow"] || "";
        document.getElementById("padding-range").value = parseInt(styles["padding"]) || 10;
        document.getElementById("margin-range").value = parseInt(styles["margin"]) || 10;
        document.getElementById("text-align-select").value = styles["text-align"] || "left";
        document.getElementById("position-select").value = styles["position"] || "static";
        document.getElementById("font-family-select").value = styles["font-family"] || "Arial, sans-serif";
        document.getElementById("flex-direction-select").value = styles["flex-direction"] || "row";
        document.getElementById("justify-content-select").value = styles["justify-content"] || "flex-start";
        document.getElementById("align-items-select").value = styles["align-items"] || "stretch";

        // Se è un link, aggiorna i controlli
        if (component.is('link')) {
            document.getElementById("link-url-input").value = component.getAttributes()["href"] || "";
            document.getElementById("link-target-select").value = component.getAttributes()["target"] || "_self";
        }
    }

    function applyStyle(property, value) {
        if (selectedComponent) {
            selectedComponent.addStyle({ [property]: value });
        }
    }

    // 🔹 EVENT LISTENERS PER OGNI INPUT
    document.getElementById("bg-color-select").addEventListener("input", function () {
        applyStyle("background-color", this.value);
    });

    document.getElementById("bg-image-select").addEventListener("input", function () {
        applyStyle("background-image", `url('${this.value}')`);
    });

    document.getElementById("text-color-select").addEventListener("input", function () {
        applyStyle("color", this.value);
    });

    document.getElementById("text-shadow-select").addEventListener("input", function () {
        applyStyle("text-shadow", this.value);
    });

    document.getElementById("font-size-range").addEventListener("input", function () {
        applyStyle("font-size", this.value + "px");
    });

    document.getElementById("border-select").addEventListener("input", function () {
        applyStyle("border", this.value);
    });

    document.getElementById("border-radius-range").addEventListener("input", function () {
        applyStyle("border-radius", this.value + "px");
    });

    document.getElementById("box-shadow-select").addEventListener("input", function () {
        applyStyle("box-shadow", this.value);
    });

    document.getElementById("padding-range").addEventListener("input", function () {
        applyStyle("padding", this.value + "px");
    });

    document.getElementById("margin-range").addEventListener("input", function () {
        applyStyle("margin", this.value + "px");
    });

    document.getElementById("text-align-select").addEventListener("change", function () {
        applyStyle("text-align", this.value);
    });

    document.getElementById("position-select").addEventListener("change", function () {
        applyStyle("position", this.value);
    });

    document.getElementById("font-family-select").addEventListener("change", function () {
        applyStyle("font-family", this.value);
    });

    document.getElementById("flex-direction-select").addEventListener("change", function () {
        applyStyle("flex-direction", this.value);
    });

    document.getElementById("justify-content-select").addEventListener("change", function () {
        applyStyle("justify-content", this.value);
    });

    document.getElementById("align-items-select").addEventListener("change", function () {
        applyStyle("align-items", this.value);
    });

    document.getElementById("link-url-input").addEventListener("input", function () {
        if (selectedComponent && selectedComponent.is('link')) {
            selectedComponent.addAttributes({ href: this.value });
        }
    });
    
    document.getElementById("link-target-select").addEventListener("change", function () {
        if (selectedComponent && selectedComponent.is('link')) {
            selectedComponent.addAttributes({ target: this.value });
        }
    });





    let blocks = {};  // Variabile per contenere i blocchi caricati

    // Carica i blocchi da un file JSON
    fetch('../../../../static/js/admin/blocks.json')
        .then(response => response.json())
        .then(data => {
            blocks = data;  // Salva i blocchi nella variabile globale
            renderBlocks();  // Aggiungi la funzione per popolare il modal con i blocchi
        })
        .catch(error => console.error('Errore nel caricamento dei blocchi:', error));

    // Funzione per aggiungere un blocco
    function addBlock(type) {
        // Verifica se il blocco esiste nei dati caricati
        if (blocks[type]) {
            const content = blocks[type].content;
            editor.addComponents(content);  // Aggiungi il blocco all'editor
        } else {
            console.error(`Blocco '${type}' non trovato`);
        }
    }

    // Funzione per rendere dinamicamente i blocchi nel modal
    function renderBlocks() {
        const sectionsTab = document.getElementById('sections-list');
        const elementsTab = document.getElementById('elements-list');
    
        // Clear existing content in the tabs
        sectionsTab.innerHTML = '';
        elementsTab.innerHTML = '';
    
        // Aggiungi i blocchi delle Sections
        Object.keys(blocks).forEach(blockType => {
            const block = blocks[blockType];
    
            if (block.category === 'Sections') {
                const blockElement = document.createElement('div');
                blockElement.classList.add('col-6', 'col-md-4', 'mb-3');  // Modifica per garantire una disposizione in righe
                blockElement.innerHTML = `
                    <div class="card text-center">
                        <img src="${block.image || 'https://via.placeholder.com/600x400'}" class="card-img-top" alt="${block.label}">
                        <div class="card-body">
                            <h5 class="card-title">${block.label}</h5>
                            <button class="btn btn-outline-dark w-100" onclick="addBlock('${blockType}')">Add</button>
                        </div>
                    </div>
                `;
                sectionsTab.appendChild(blockElement);
            } else if (block.category === 'Elements') {
                // Aggiungi i blocchi degli Elements con icone FontAwesome
                const blockElement = document.createElement('div');
                blockElement.classList.add('col-6', 'col-md-3', 'mb-3');  // Modifica per garantire una disposizione in righe
                blockElement.innerHTML = `
                    <div class="card text-center">
                        <i class="fa-solid fa-${block.icon} fa-3x my-3"></i>
                        <div class="card-body">
                            <h5 class="card-title">${block.label}</h5>
                            <button class="btn btn-outline-dark w-100" onclick="addBlock('${blockType}')">Add</button>
                        </div>
                    </div>
                `;
                elementsTab.appendChild(blockElement);
            }
        });
    
        // Imposta layout Flex per la visualizzazione a griglia per i blocchi
        sectionsTab.classList.add('row', 'g-3', 'd-flex', 'flex-wrap');
        elementsTab.classList.add('row', 'g-3', 'd-flex', 'flex-wrap');
    }

    // Aggiungi la funzione `addBlock` globalmente
    window.addBlock = addBlock;

    
    function undo() { editor.UndoManager.undo(); }
    function redo() { editor.UndoManager.redo(); }
    function clearCanvas() { editor.DomComponents.clear(); }
    
    window.undo = undo;
    window.redo = redo;
    window.clearCanvas = clearCanvas;
    

    function setView(mode) {
        editor.setDevice(mode);
    }
    window.setView = setView;
    

    document.getElementById('save-page').addEventListener('click', async function() {
        var content = editor.getHtml();
        var styles = editor.getCss();  
        var slug = pageSlug;     
        var page_id = pageID;    
        var language = document.getElementById('language-selector').value;

        if (!content) {
            Swal.fire('Error!', 'Content is empty.', 'error');
            return;
        }

            // Mostra un messaggio di caricamento
            Swal.fire({
                title: 'Saving...',
                text: 'Processing your content and uploading images.',
                icon: 'info',
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => Swal.showLoading(),
            });

        // Funzione per gestire l'upload delle immagini in formato base64
        async function uploadBase64Image(base64Image) {
            try {
                const response = await fetch('/upload-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: base64Image })
                });
        
                const data = await response.json();
                if (data.success && data.url) {
                    return data.url; 
                } else {
                    console.error('Image upload failed:', data.error);
                    return null;
                }
            } catch (error) {
                console.error('Error uploading image:', error);
                return null;
            }
        }

        // Processa tutte le immagini base64 trovate nel contenuto
        var div = document.createElement('div');
        div.innerHTML = content;
        var images = div.querySelectorAll('img');
        var uploadPromises = [];

        // Carica tutte le immagini in base64 e sostituisci i riferimenti nel contenuto
        for (let img of images) {
            if (img.src.startsWith('data:image')) {
                const uploadPromise = uploadBase64Image(img.src).then(url => {
                    if (url) {
                        img.src = url;  
                    }
                });
                uploadPromises.push(uploadPromise);
            }
        }

        // Aspetta che tutte le immagini siano caricate e sostituite
        await Promise.all(uploadPromises);

        // Salva il contenuto nella tabella `pages`, identificando la lingua
        fetch("/api/function/save", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: page_id,
                content: div.innerHTML,   
                styles: styles,
                language: language        
            })
        }).then(response => response.json()).then(data => {
            if (data.success) {
                Swal.fire('Saved!', 'Your page content has been successfully saved.', 'success');
            } else {
                Swal.fire('Error!', 'There was an error saving the page content.', 'error');
            }
        }).catch(error => {
            console.error('Error:', error);
            Swal.fire('Error!', 'There was an error saving the page content.', 'error');
        });



    });
});