document.addEventListener("DOMContentLoaded", function () {
  const stripeData = document.getElementById("stripe-data");
  const stripePk = stripeData.dataset.stripePk;
  const shopName = stripeData.dataset.shopName;
  const stripe = Stripe(stripePk);

  document.addEventListener("click", async function (e) {
    if (e.target && e.target.classList.contains("btn-purchase-domain")) {
      const domain = e.target.dataset.domain;
      const price = e.target.dataset.price;

      try {
        const res = await fetch("/api/domains/checkout_session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            domain: domain,
            price: price,
            shop_name: shopName
          })
        });

        const session = await res.json();
        if (session.success && session.url) {
          window.location.href = session.url;
        } else {
          console.error("Stripe session error:", session);
          Swal.fire({
            icon: "error",
            title: "Errore pagamento",
            text: session.message || "Impossibile avviare il pagamento con Stripe."
          });
        }
      } catch (err) {
        console.error(err);
        alert("Errore durante il pagamento.");
      }
    }
  });
});
