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

    


    // 🔹 Quando un elemento viene selezionato nell'editor
    editor.on('component:selected', (component) => {
        selectedComponent = component;
        
        // Impostiamo i valori dei controlli con le classi correnti
        let currentClasses = selectedComponent.getClasses().join(' ');

        // Background Color
        document.getElementById('bg-color-select').value = currentClasses.match(/bg-\w+/)?.[0] || 'bg-light';
        
        // Padding
        document.getElementById('padding-select').value = currentClasses.match(/p-\d+/)?.[0] || 'p-0';
        
        // Margin
        document.getElementById('margin-select').value = currentClasses.match(/m-\d+/)?.[0] || 'm-0';
        
        // Text Color
        document.getElementById('text-color-select').value = currentClasses.match(/text-\w+/)?.[0] || 'text-dark';
        
        // Font Family
        document.getElementById('font-family-select').value = currentClasses.match(/font-\w+/)?.[0] || 'font-sans-serif';
        
        // Section Type
        document.getElementById('section-type-select').value = currentClasses.match(/container-fluid|container|section-full|section/)?.[0] || 'container';
        
        // Flex
        document.getElementById('flex-select').value = currentClasses.includes('d-flex') ? 'd-flex' : 'd-none';
    });

    // 🔹 Funzione per aggiornare le classi
    function updateClass(property, value) {
        if (selectedComponent) {
            // Prendi tutte le classi esistenti
            let currentClasses = selectedComponent.getClasses();
            
            // Rimuovi la classe se esiste già
            selectedComponent.removeClass(currentClasses.filter(c => c.startsWith(property)));

            // Aggiungi la nuova classe
            selectedComponent.addClass(value);
        }
    }

    // 🔹 Cambia la classe per il background
    document.getElementById('bg-color-select').addEventListener('change', function () {
        updateClass('bg', this.value);
    });

    // 🔹 Cambia la classe per il padding
    document.getElementById('padding-select').addEventListener('change', function () {
        updateClass('p', this.value);
    });

    // 🔹 Cambia la classe per il margin
    document.getElementById('margin-select').addEventListener('change', function () {
        updateClass('m', this.value);
    });

    // 🔹 Cambia la classe per il colore del testo
    document.getElementById('text-color-select').addEventListener('change', function () {
        updateClass('text', this.value);
    });

    // 🔹 Cambia la classe per il font family
    document.getElementById('font-family-select').addEventListener('change', function () {
        updateClass('font', this.value);
    });

    // 🔹 Cambia la classe per il tipo di sezione
    document.getElementById('section-type-select').addEventListener('change', function () {
        updateClass('section-type', this.value);
    });

    // 🔹 Cambia la classe per Flex
    document.getElementById('flex-select').addEventListener('change', function () {
        updateClass('d', this.value);
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
        var content = editor.getHtml();  // Ottieni il contenuto HTML dall'editor di GrapesJS
        var slug = pageSlug;     // Slug della pagina corrente
        var page_id = pageID;    // ID della pagina corrente
        var language = document.getElementById('language-selector').value; // Lingua selezionata

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
                if (data.url) {
                    return data.url; 
                } else {
                    throw new Error('Image upload failed');
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
        fetch("/api/save", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: page_id,
                content: div.innerHTML,   // Nuovo contenuto con immagini sostituite
                language: language        // Lingua selezionata
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