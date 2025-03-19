// AGGIUNGI AL CARRELLO ----------------------------------------------------------------------------------------------------------------------------------------------------------------

// FUNZIONI PER IL CARRELLO DINAMICO ----------------------------------------------------------------------------------------------------------------------------------------------------------------

// POPOLA LA NAVBAR ED IL FOTER ----------------------------------------------------------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    async function fetchNavbarLinks() {
        try {
            const response = await fetch("/api/navbar");
            const data = await response.json();
            
            if (data.error) {
                console.error("Error fetching navbar:", data.error);
                return;
            }

            const navLinksContainer = document.getElementById("nav-links");
            const navControlsContainer = document.getElementById("nav-controls");

            if (!navLinksContainer || !navControlsContainer) {
                console.error("Navbar containers not found.");
                return;
            }

            function createNavItem(link) {
                const navItem = document.createElement("li");
                navItem.classList.add("nav-item");
                
                if (link.link_url === "show_collections") {
                    return createCollectionsDropdown(link.link_text);
                }
                
                const navLink = document.createElement("a");
                navLink.classList.add("nav-link");
                navLink.href = link.link_url;
                navLink.innerText = link.link_text;
                navItem.appendChild(navLink);
                return navItem;
            }
            
            async function createCollectionsDropdown(linkText) {
                try {
                    const collectionsResponse = await fetch("/api/collections");
                    const collectionsData = await collectionsResponse.json();
                    
                    const dropdown = document.createElement("li");
                    dropdown.classList.add("nav-item", "dropdown");
                    
                    const dropdownToggle = document.createElement("a");
                    dropdownToggle.classList.add("nav-link", "dropdown-toggle");
                    dropdownToggle.href = "#";
                    dropdownToggle.setAttribute("data-bs-toggle", "dropdown");
                    dropdownToggle.innerText = linkText;
                    
                    const dropdownMenu = document.createElement("ul");
                    dropdownMenu.classList.add("dropdown-menu");
                    
                    collectionsData.collections.forEach(collection => {
                        const dropdownItem = document.createElement("li");
                        const dropdownLink = document.createElement("a");
                        dropdownLink.classList.add("dropdown-item");
                        dropdownLink.href = `/collections/${collection.slug}`;
                        dropdownLink.innerText = collection.name;
                        
                        if (collection.image_url) {
                            const img = document.createElement("img");
                            img.src = collection.image_url;
                            img.classList.add("me-2");
                            img.style.width = "30px";
                            dropdownLink.prepend(img);
                        }
                        
                        dropdownItem.appendChild(dropdownLink);
                        dropdownMenu.appendChild(dropdownItem);
                    });
                    
                    dropdown.appendChild(dropdownToggle);
                    dropdown.appendChild(dropdownMenu);
                    return dropdown;
                } catch (error) {
                    console.error("Error fetching collections:", error);
                    return document.createElement("li");
                }
            }
            
            function createActionButton(action) {
                const button = document.createElement("button");
                button.classList.add("btn", "nav-link");
                button.innerHTML = getIconForAction(action);
                button.onclick = () => handleAction(action);
                button.style.color = "white"; // Imposta il colore come i nav-links
                return button;
            }
            
            function getIconForAction(action) {
                const icons = {
                    "cart": "<i class='fa-solid fa-shopping-cart'></i>",
                    "search": "<i class='fa-solid fa-search'></i>",
                    "account": "<i class='fa-solid fa-user'></i>"
                };
                return icons[action] || "<i class='fa-solid fa-question'></i>";
            }
            
            function handleAction(action) {
                switch (action) {
                    case "cart":
                        window.location.href = "/cart";
                        break;
                    case "search":
                        showSearchModal();
                        break;
                    case "account":
                        window.location.href = "/account";
                        break;
                }
            }
            
            function showSearchModal() {
                const searchModal = new bootstrap.Modal(document.getElementById("searchModal"));
                searchModal.show();
            }
            
            const navList = document.createElement("ul");
            navList.classList.add("navbar-nav", "ms-auto", "mb-2", "mb-lg-0");
            
            let actionButtons = [];
            
            data.navbar.forEach(async (link) => {
                if (["cart", "search", "account"].includes(link.link_url)) {
                    actionButtons.push(createActionButton(link.link_url));
                } else {
                    const navItem = await createNavItem(link);
                    if (navItem) navList.appendChild(navItem);
                }
            });
            
            navLinksContainer.innerHTML = "";
            navLinksContainer.appendChild(navList);
            navLinksContainer.style.marginRight = "20px"; // Sposta i nav-links leggermente a sinistra
            
            navControlsContainer.innerHTML = "";
            actionButtons.forEach(button => navControlsContainer.appendChild(button));
        } catch (error) {
            console.error("Error loading navbar links:", error);
        }
    }

    fetchNavbarLinks();
});

// RENDERIZZA I NAVBAR LINKS ----------------------------------------------------------------------------------------------------------------------------------------------------------------

// COOKIE BANNER ----------------------------------------------------------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    const cookieBar = document.getElementById("cookie-bar");
    const acceptBtn = document.getElementById("accept-cookies");
    const rejectBtn = document.getElementById("reject-cookies");

    if (!cookieBar) return;

    // Controlla se i cookie sono già stati accettati
    if (!localStorage.getItem("cookiesAccepted")) {
        cookieBar.classList.remove("d-none");
    }

    acceptBtn.addEventListener("click", function () {
        localStorage.setItem("cookiesAccepted", "true");
        cookieBar.classList.add("d-none");
    });

    rejectBtn.addEventListener("click", function () {
        localStorage.setItem("cookiesAccepted", "false");
        cookieBar.classList.add("d-none");
    });
});