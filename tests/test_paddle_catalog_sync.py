"""Script di sync catalogo (app/billing/paddle_catalog_sync.py) — idempotente:
un secondo run non deve mai creare un secondo prodotto/price per lo stesso
piano/pacchetto. Nessuna chiamata di rete reale: monkeypatch di _request."""
from app.billing.paddle_catalog_sync import sync_catalog
from app.billing.paddle_products import PADDLE_CREDIT_PACKAGES, PADDLE_SUBSCRIPTION_PLANS


class _FakeCatalog:
    """Simula lo stato di Paddle (prodotti/prezzi) in memoria, con lo stesso
    contratto minimo di GET/POST /products e /prices usato da
    paddle_catalog_sync.py — abbastanza per verificare l'idempotenza senza
    una vera API."""

    def __init__(self):
        self.products = []  # list[dict]
        self.prices = {}  # product_id -> list[dict]
        self._next_id = 1

    def _id(self, prefix):
        self._next_id += 1
        return f"{prefix}_{self._next_id}"

    def __call__(self, method, path, json=None):
        if method == "GET" and path.startswith("/products"):
            return {"data": self.products, "meta": {"pagination": {"has_more": False}}}
        if method == "POST" and path == "/products":
            product = {"id": self._id("pro"), "name": json["name"], "status": "active"}
            self.products.append(product)
            self.prices[product["id"]] = []
            return {"data": product}
        if method == "GET" and path.startswith("/prices"):
            product_id = path.split("product_id=")[1].split("&")[0]
            return {"data": self.prices.get(product_id, [])}
        if method == "POST" and path == "/prices":
            price = {
                "id": self._id("pri"), "product_id": json["product_id"],
                "unit_price": json["unit_price"], "billing_cycle": json.get("billing_cycle"),
                "status": "active",
            }
            self.prices[json["product_id"]].append(price)
            return {"data": price}
        raise AssertionError(f"chiamata non attesa: {method} {path}")


def test_sync_catalog_creates_one_product_and_price_per_entry(app, monkeypatch):
    fake = _FakeCatalog()
    monkeypatch.setattr("app.billing.paddle_catalog_sync._request", fake)

    with app.test_request_context():
        entries = sync_catalog(environment="sandbox")

    expected_count = len(PADDLE_SUBSCRIPTION_PLANS) + len(PADDLE_CREDIT_PACKAGES)
    assert len(entries) == expected_count
    assert all(e.created_product and e.created_price for e in entries)
    assert len(fake.products) == expected_count


def test_sync_catalog_is_idempotent_on_second_run(app, monkeypatch):
    fake = _FakeCatalog()
    monkeypatch.setattr("app.billing.paddle_catalog_sync._request", fake)

    with app.test_request_context():
        first = sync_catalog(environment="sandbox")
        second = sync_catalog(environment="sandbox")

    expected_count = len(PADDLE_SUBSCRIPTION_PLANS) + len(PADDLE_CREDIT_PACKAGES)
    assert len(fake.products) == expected_count  # non raddoppiato
    assert all(not e.created_product and not e.created_price for e in second)
    assert {e.price_id for e in first} == {e.price_id for e in second}


def test_sync_catalog_dry_run_never_calls_the_api(app, monkeypatch):
    calls = []
    monkeypatch.setattr("app.billing.paddle_catalog_sync._request", lambda *a, **k: calls.append((a, k)))

    with app.test_request_context():
        entries = sync_catalog(environment="sandbox", dry_run=True)

    assert calls == []
    assert len(entries) == len(PADDLE_SUBSCRIPTION_PLANS) + len(PADDLE_CREDIT_PACKAGES)
