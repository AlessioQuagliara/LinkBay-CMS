// -------------------------------------------------------------------------------------------------------------------------
// Edit SEO ----------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
    const saveSeoButton = document.getElementById('save-seo');
    const seoForm = document.getElementById('seo-form');
    
    saveSeoButton.addEventListener('click', function() {
        const formData = new FormData(seoForm);
        const data = {
            id: formData.get('id'),
            title: formData.get('title'),
            description: formData.get('description'),
            keywords: formData.get('keywords'),
            slug: formData.get('slug')
        };

        fetch('/admin/cms/function/save-seo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: 'SEO settings updated successfully!',
                }).then(() => {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('seoModal'));
                    modal.hide(); // Chiudi il modale dopo il salvataggio
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error saving SEO settings.',
                });
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error saving SEO settings.',
            });
        });
    });

// -------------------------------------------------------------------------------------------------------------------------
// Chips Script ------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------
    
    const keywordsContainer = document.getElementById('seo-keywords-container');
    const keywordsInput = document.createElement('input');
    const hiddenKeywordsInput = document.getElementById('seo-keywords');

    keywordsInput.type = 'text';
    keywordsInput.placeholder = 'Add a keyword';
    keywordsContainer.appendChild(keywordsInput);

    const existingKeywords = hiddenKeywordsInput.value.split(',');
    existingKeywords.forEach(function(keyword) {
        if (keyword.trim()) {
            addKeywordChip(keyword.trim());
        }
    });

    keywordsInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const keyword = keywordsInput.value.trim();

            if (keyword && !isDuplicate(keyword)) {
                addKeywordChip(keyword);
                updateHiddenInput();
                keywordsInput.value = '';
            }
        }
    });

    keywordsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('close-btn')) {
            event.target.parentElement.remove();
            updateHiddenInput();
        }
    });

    function addKeywordChip(keyword) {
        const chip = document.createElement('div');
        chip.classList.add('chip');
        chip.textContent = keyword;

        const closeBtn = document.createElement('span');
        closeBtn.classList.add('close-btn');
        closeBtn.textContent = 'x';
        chip.appendChild(closeBtn);

        keywordsContainer.insertBefore(chip, keywordsInput);
    }

    function updateHiddenInput() {
        const chips = keywordsContainer.getElementsByClassName('chip');
        const keywordsArray = Array.from(chips).map(chip => chip.textContent.slice(0, -1));
        hiddenKeywordsInput.value = keywordsArray.join(',');
    }

    function isDuplicate(keyword) {
        const chips = keywordsContainer.getElementsByClassName('chip');
        return Array.from(chips).some(chip => chip.textContent.slice(0, -1).toLowerCase() === keyword.toLowerCase());
    }
});
    

// -------------------------------------------------------------------------------------------------------------------------
// Create page -------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    const createPageButton = document.getElementById('create-page');
    const createPageForm = document.getElementById('create-page-form');

    createPageButton.addEventListener('click', function() {
        const formData = new FormData(createPageForm);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            keywords: formData.get('keywords'),
            slug: formData.get('slug'),
            content: formData.get('content'),
            theme_name: formData.get('theme_name'),
            paid: formData.get('paid'),
            language: formData.get('language'),
            published: formData.get('published')
        };

        fetch('/admin/cms/function/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire(
                    'Created!',
                    'Your page has been successfully created.',
                    'success'
                ).then(() => {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('createPageModal'));
                    modal.hide(); // Chiudi il modale dopo il salvataggio
                    window.location.reload(); // Ricarica la pagina per vedere la nuova pagina nella lista
                });
            } else {
                Swal.fire(
                    'Error!',
                    'There was an error creating the page.',
                    'error'
                );
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            Swal.fire(
                'Error!',
                'There was an error creating the page.',
                'error'
            );
        });
    });

// -------------------------------------------------------------------------------------------------------------------------
// Chips Script ------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------

    const keywordsContainer = document.getElementById('keywords-container');
    const keywordsInput = document.createElement('input');
    const hiddenKeywordsInput = document.getElementById('keywords');

    keywordsInput.type = 'text';
    keywordsInput.placeholder = 'Add a keyword';
    keywordsContainer.appendChild(keywordsInput);

    keywordsInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const keyword = keywordsInput.value.trim();

            if (keyword && !isDuplicate(keyword)) {
                addKeywordChip(keyword);
                updateHiddenInput();
                keywordsInput.value = '';
            }
        }
    });

    keywordsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('close-btn')) {
            event.target.parentElement.remove();
            updateHiddenInput();
        }
    });

    function addKeywordChip(keyword) {
        const chip = document.createElement('div');
        chip.classList.add('chip');
        chip.textContent = keyword;

        const closeBtn = document.createElement('span');
        closeBtn.classList.add('close-btn');
        closeBtn.textContent = 'x';
        chip.appendChild(closeBtn);

        keywordsContainer.insertBefore(chip, keywordsInput);
    }

    function updateHiddenInput() {
        const chips = keywordsContainer.getElementsByClassName('chip');
        const keywordsArray = Array.from(chips).map(chip => chip.textContent.slice(0, -1));
        hiddenKeywordsInput.value = keywordsArray.join(',');
    }

    function isDuplicate(keyword) {
        const chips = keywordsContainer.getElementsByClassName('chip');
        return Array.from(chips).some(chip => chip.textContent.slice(0, -1).toLowerCase() === keyword.toLowerCase());
    }
});

// -------------------------------------------------------------------------------------------------------------------------
// Edit SLUG ----------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    const titleInput = document.getElementById('title');
    const slugInput = document.getElementById('slug');

    titleInput.addEventListener('input', function() {
        let slug = titleInput.value
            .toLowerCase()  // Converti tutto in minuscolo
            .replace(/[^a-z0-9\s-]/g, '')  // Rimuove tutti i caratteri non alfanumerici eccetto gli spazi e i trattini
            .replace(/\s+/g, '-')  // Sostituisce gli spazi con i trattini
            .replace(/-+/g, '-');  // Elimina i trattini multipli consecutivi

        slugInput.value = slug;
    });
});

// -------------------------------------------------------------------------------------------------------------------------
// SIDEBAR ----------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------

$(document).ready(function(){
    $('.navbar-toggler').on('click', function(){
        $('#editor-bar').toggleClass('show');
    });

    // Nasconde la sidebar quando si clicca fuori da essa
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#editor-bar, .navbar-toggler').length) {
            $('#editor-bar').removeClass('show');
        }
    });
});

// -------------------------------------------------------------------------------------------------------------------------
// CANCELLA PAGINA ----------------------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
    const deleteButtons = document.querySelectorAll('.nav-link.text-danger');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const pageId = this.getAttribute('data-id-page');

            Swal.fire({
                title: 'Sei sicuro?',
                text: "Questa azione eliminerà definitivamente la pagina!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sì, cancellala!'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Invia la richiesta al server
                    fetch('/admin/cms/function/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ id: pageId })  // Invia l'ID della pagina
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Cancellata!',
                                text: 'La pagina è stata cancellata con successo.'
                            }).then(() => {
                                window.location.href = '/admin/cms/store_editor/editor_interface';  // Reindirizza dopo la cancellazione
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Errore!',
                                text: data.message
                            });
                        }
                    })
                    .catch((error) => {
                        console.error('Errore:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Errore!',
                            text: 'Si è verificato un errore durante la cancellazione della pagina.'
                        });
                    });
                }
            });
        });
    });
});