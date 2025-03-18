document.addEventListener("DOMContentLoaded", function () {
    var navbarEditor = grapesjs.init({
        container: '#navbar-editor',
        height: 'auto',
        width: '100%',
        storageManager: false,
        fromElement: true,
        blockManager: false,
        panels: { defaults: [] },
        styleManager: { sectors: [] },
        layerManager: false,
        traitManager: false
    });

    navbarEditor.on("load", () => {
        const navbarComponent = navbarEditor.getWrapper().find("#editable-navbar")[0];
        if (navbarComponent) {
            navbarComponent.set({ selectable: true, draggable: true, editable: true });
    
            // 🔹 Rendi editabili anche i link e i bottoni della navbar
            navbarComponent.find("a").forEach(link => link.set({ editable: true }));
            navbarComponent.find("button").forEach(btn => btn.set({ editable: true }));
        }
    }); 

    window.saveNavbar = async function () {
        var navbarContent = navbarEditor.getHtml();
        var navbarStyles = navbarEditor.getCss();

        try {
            await fetch("/api/save-navbar", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: navbarContent,
                    styles: navbarStyles
                })
            });
            console.log("✅ Navbar saved successfully!");
        } catch (error) {
            console.error("❌ Error saving navbar:", error);
        }
    };
});