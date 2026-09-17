"""Script amministrativo idempotente per creare/recuperare in Paddle i
prodotti e i price ID del catalogo whitelist (app/billing/paddle_products.py)
— invocato da `flask paddle-sync-catalog` (vedi app/__init__.py). Non usa il
MCP Paddle (non affidabile in questo ambiente al momento della stesura: vedi
docs/paddle-billing.md) — chiama direttamente l'API REST via
app/billing/paddle_client.py, con la stessa API key/environment già
configurati per il resto dell'app.

Idempotenza SENZA una tabella di mappatura dedicata (i price ID vivono in
.env, non in DB — vedi Fase 2 del piano): prima di creare, cerca un prodotto
Paddle già esistente con lo stesso `name` esatto (Paddle non ha un
"external_id"/chiave stabile lato prodotto in questa versione dell'API, il
nome è la chiave più stabile che abbiamo) e, dentro quello, un price con lo
stesso billing_cycle + description. Se li trova, li riusa; altrimenti li
crea. Rilanciabile senza mai duplicare — vedi test in
tests/test_paddle_catalog_sync.py."""
from __future__ import annotations

from dataclasses import dataclass

from app.billing.paddle_client import api_request as _request
from app.billing.paddle_products import PADDLE_CREDIT_PACKAGES, PADDLE_SUBSCRIPTION_PLANS

PRODUCT_NAME_PREFIX = "LinkBay CMS"


def _subscription_product_name(key: str) -> str:
    label = PADDLE_SUBSCRIPTION_PLANS[key]["label"]
    return f"{PRODUCT_NAME_PREFIX} — Pro ({label})"


def _credit_product_name(key: str) -> str:
    label = PADDLE_CREDIT_PACKAGES[key]["label"]
    return f"{PRODUCT_NAME_PREFIX} — AI Credits ({label})"


@dataclass(frozen=True)
class CatalogSyncEntry:
    internal_key: str
    kind: str  # "subscription" | "ai_credits"
    product_name: str
    product_id: str
    price_id: str
    price_env_var: str
    created_product: bool
    created_price: bool


def _list_all_products() -> list[dict]:
    products: list[dict] = []
    after = None
    while True:
        path = "/products?per_page=200" + (f"&after={after}" if after else "")
        body = _request("GET", path)
        products.extend(body.get("data") or [])
        cursor = (body.get("meta") or {}).get("pagination") or {}
        if not cursor.get("has_more"):
            break
        after = cursor.get("next")
        if not after:
            break
    return products


def _list_prices_for_product(product_id: str) -> list[dict]:
    body = _request("GET", f"/prices?product_id={product_id}&per_page=200")
    return body.get("data") or []


def _find_product_by_name(products: list[dict], name: str) -> dict | None:
    for p in products:
        if p.get("name") == name and p.get("status") != "archived":
            return p
    return None


def _get_or_create_product(products_cache: list[dict], *, name: str, description: str) -> tuple[dict, bool]:
    existing = _find_product_by_name(products_cache, name)
    if existing is not None:
        return existing, False
    created = _request(
        "POST", "/products", json={"name": name, "description": description, "tax_category": "saas"}
    )
    product = created.get("data") or created
    products_cache.append(product)
    return product, True


def _find_matching_price(prices: list[dict], *, unit_price_amount: str, currency: str, billing_cycle: dict | None) -> dict | None:
    for price in prices:
        if price.get("status") == "archived":
            continue
        up = price.get("unit_price") or {}
        if up.get("amount") != unit_price_amount or up.get("currency_code") != currency:
            continue
        if (price.get("billing_cycle") or None) != billing_cycle:
            continue
        return price
    return None


def sync_catalog(*, environment: str, currency: str = "EUR", dry_run: bool = False) -> list[CatalogSyncEntry]:
    """Crea/recupera in Paddle (per l'`environment` dato — MAI production da
    qui senza che il chiamante lo scelga esplicitamente, vedi il comando CLI)
    un prodotto+price per ogni piano Pro e ogni pacchetto crediti del
    catalogo whitelist. Con `dry_run=True` non chiama l'API: stampa solo
    cosa farebbe (vedi CLI --dry-run)."""
    from flask import current_app

    if dry_run:
        entries = []
        for key, entry in PADDLE_SUBSCRIPTION_PLANS.items():
            entries.append(
                CatalogSyncEntry(
                    internal_key=key, kind="subscription", product_name=_subscription_product_name(key),
                    product_id="(dry-run)", price_id="(dry-run)", price_env_var=entry["sandbox_env"] if environment == "sandbox" else entry["production_env"],
                    created_product=False, created_price=False,
                )
            )
        for key, entry in PADDLE_CREDIT_PACKAGES.items():
            entries.append(
                CatalogSyncEntry(
                    internal_key=key, kind="ai_credits", product_name=_credit_product_name(key),
                    product_id="(dry-run)", price_id="(dry-run)", price_env_var=entry["sandbox_env"] if environment == "sandbox" else entry["production_env"],
                    created_product=False, created_price=False,
                )
            )
        return entries

    # PADDLE_ENVIRONMENT decide l'endpoint (vedi app/billing/paddle_client.py)
    # — sovrascriviamo temporaneamente la config per la durata dello script,
    # così `--environment production` non richiede di riavviare il processo
    # con una diversa env var.
    previous_env = current_app.config.get("PADDLE_ENVIRONMENT")
    current_app.config["PADDLE_ENVIRONMENT"] = environment
    try:
        products_cache = _list_all_products()
        results: list[CatalogSyncEntry] = []

        for key, entry in PADDLE_SUBSCRIPTION_PLANS.items():
            name = _subscription_product_name(key)
            product, created_product = _get_or_create_product(
                products_cache, name=name, description=f"LinkBay CMS Pro subscription — billed every {entry['billing_cycle']['frequency']} {entry['billing_cycle']['interval']}(s)."
            )
            prices = _list_prices_for_product(product["id"])
            amount_minor = str(int(round(entry["price"] * 100)))
            billing_cycle = entry["billing_cycle"]
            price = _find_matching_price(prices, unit_price_amount=amount_minor, currency=currency, billing_cycle=billing_cycle)
            created_price = False
            if price is None:
                created = _request(
                    "POST", "/prices",
                    json={
                        "product_id": product["id"],
                        "description": f"{name} — {currency} {entry['price']:.2f}",
                        "unit_price": {"amount": amount_minor, "currency_code": currency},
                        "billing_cycle": billing_cycle,
                        "quantity": {"minimum": 1, "maximum": 1},
                    },
                )
                price = created.get("data") or created
                created_price = True

            env_var = entry["sandbox_env"] if environment == "sandbox" else entry["production_env"]
            results.append(
                CatalogSyncEntry(
                    internal_key=key, kind="subscription", product_name=name,
                    product_id=product["id"], price_id=price["id"], price_env_var=env_var,
                    created_product=created_product, created_price=created_price,
                )
            )

        for key, entry in PADDLE_CREDIT_PACKAGES.items():
            name = _credit_product_name(key)
            product, created_product = _get_or_create_product(
                products_cache, name=name, description=f"One-time purchase of {entry['credits']} LinkBay CMS AI credits."
            )
            prices = _list_prices_for_product(product["id"])
            amount_minor = str(int(round(entry["price"] * 100)))
            price = _find_matching_price(prices, unit_price_amount=amount_minor, currency=currency, billing_cycle=None)
            created_price = False
            if price is None:
                created = _request(
                    "POST", "/prices",
                    json={
                        "product_id": product["id"],
                        "description": f"{name} — {currency} {entry['price']:.2f}",
                        "unit_price": {"amount": amount_minor, "currency_code": currency},
                        "quantity": {"minimum": 1, "maximum": 1},
                    },
                )
                price = created.get("data") or created
                created_price = True

            env_var = entry["sandbox_env"] if environment == "sandbox" else entry["production_env"]
            results.append(
                CatalogSyncEntry(
                    internal_key=key, kind="ai_credits", product_name=name,
                    product_id=product["id"], price_id=price["id"], price_env_var=env_var,
                    created_product=created_product, created_price=created_price,
                )
            )

        return results
    finally:
        current_app.config["PADDLE_ENVIRONMENT"] = previous_env
