    // RICERCA NELLA TABELLA
    document.addEventListener('DOMContentLoaded', function () {
        const searchToggleBtn = document.getElementById('search-toggle-btn');
        const searchInput = document.getElementById('search-input');
        const tableRows = document.querySelectorAll('.table-row');

        searchToggleBtn.addEventListener('click', function () {
            searchInput.classList.toggle('d-none');
            searchInput.focus();
        });

        searchInput.addEventListener('input', function () {
            const query = searchInput.value.toLowerCase().trim();
            tableRows.forEach(row => {
                const rowText = row.innerText.toLowerCase();
                if (rowText.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });