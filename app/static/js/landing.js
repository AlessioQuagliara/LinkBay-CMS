const html = document.documentElement
const topbar = document.getElementById("layout-topbar")
if (topbar) {
    const handleScroll = () =>
        topbar.setAttribute("data-at-top", window.scrollY < 30 ? "true" : "false")

    window.addEventListener("scroll", handleScroll, { passive: true })
    handleScroll()
}

const pricingCard = document.querySelector("[data-pricing-card]")
if (pricingCard) {
    const toggles = document.querySelectorAll("[data-pricing-toggle]")
    const setInterval_ = (interval) => {
        pricingCard.querySelectorAll("[data-monthly]").forEach((el) => {
            el.textContent = el.getAttribute(interval === "annual" ? "data-annual" : "data-monthly")
        })
        toggles.forEach((btn) => {
            btn.classList.toggle("btn-active", btn.getAttribute("data-pricing-toggle") === interval)
        })
    }
    toggles.forEach((btn) => {
        btn.addEventListener("click", () => setInterval_(btn.getAttribute("data-pricing-toggle")))
    })
    setInterval_("monthly")
}

document.querySelectorAll("[data-theme-control]").forEach((control) => {
    control.addEventListener("click", () => {
        const theme = control.getAttribute("data-theme-control")
        if (theme === "system") {
            html.removeAttribute("data-theme")
        } else {
            html.setAttribute("data-theme", theme)
        }
    })
})
