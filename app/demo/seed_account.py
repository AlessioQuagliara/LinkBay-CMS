"""Genera/ripristina un account demo con siti e storico Search Console
sintetici, per testare e registrare video promozionali di Pagine in calo e
Audit Presentation senza toccare account reali.

Tutto è isolato per user_id: `seed_demo_account` cancella e ricrea SOLO le
righe di quell'utente (nessuna FK verso MonitoredSite/GscConnection dalle
tabelle a valle, vedi i docstring dei modelli — sicuro anche a ripetere).
Gli alert non sono inventati a mano: il traffico sintetico è costruito per
attraversare le soglie reali del rule engine (app/rules/filters.py) e
`run_for_site` (app/rules/service.py, INVARIATO) li calcola per davvero — le
stesse identiche regole che varrebbero per un utente vero connesso a Google
Search Console. Nessun account reale, cron o job in coda viene toccato:
- niente chiamate a Google (nessuna GscConnection valida: vedi seed_gsc_connection);
- niente email cron (weekly_digest_enabled=False);
- niente crediti AI consumati (build_presentation è chiamato direttamente,
  non passa dal job che li scala).
"""
import math
import random
import zlib
from datetime import date, datetime, timedelta, timezone

from app.extensions import db
from app.models import (
    AuditPresentation,
    GscConnection,
    GscPageMonthly,
    GscSiteDaily,
    MonitoredSite,
    PageAlert,
    User,
)

MONTHS_OF_HISTORY = 16
LONG_TAIL_FACTOR = 1.6  # traffico di sito oltre le pagine modellate singolarmente

SITES = [
    {
        "site_url": "sc-domain:negozio-modaverde.it",
        "pages": [
            ("https://negozio-modaverde.it/", "stable", 260, 6.5),
            ("https://negozio-modaverde.it/collezioni/donna", "stable", 210, 7.0),
            ("https://negozio-modaverde.it/collezioni/uomo", "stable", 150, 8.0),
            ("https://negozio-modaverde.it/collezioni/accessori", "stable", 95, 9.5),
            ("https://negozio-modaverde.it/prodotto/borsa-a-tracolla", "stable", 90, 10.5),
            ("https://negozio-modaverde.it/spedizioni-e-resi", "stable", 70, 12.0),
            ("https://negozio-modaverde.it/blog/lavaggio-capi-lana", "stable", 65, 11.0),
            ("https://negozio-modaverde.it/chi-siamo", "stable", 40, 14.0),
            ("https://negozio-modaverde.it/faq", "stable", 35, 15.0),
            ("https://negozio-modaverde.it/collezioni/saldi", "seasonal_dip", 180, 9.0),
            ("https://negozio-modaverde.it/prodotto/giacca-in-lino", "decline_severe", 640, 4.5),
            ("https://negozio-modaverde.it/prodotto/scarpe-eco-sneaker", "decline_position", 310, 6.0),
            ("https://negozio-modaverde.it/blog/guida-taglie", "decline_demand", 240, 8.5),
            ("https://negozio-modaverde.it/prodotto/cappotto-lana", "decline_yoy", 420, 5.5),
        ],
    },
    {
        "site_url": "sc-domain:blog-viaggiverso.it",
        "pages": [
            ("https://blog-viaggiverso.it/", "stable", 300, 6.0),
            ("https://blog-viaggiverso.it/destinazioni/lago-di-garda", "stable", 140, 8.5),
            ("https://blog-viaggiverso.it/guide/voli-low-cost", "stable", 190, 9.5),
            ("https://blog-viaggiverso.it/destinazioni/dolomiti-estate", "stable", 110, 10.0),
            ("https://blog-viaggiverso.it/newsletter", "stable", 25, 16.0),
            ("https://blog-viaggiverso.it/chi-siamo", "stable", 30, 13.0),
            ("https://blog-viaggiverso.it/guide/documenti-viaggio-ue", "stable", 85, 11.5),
            ("https://blog-viaggiverso.it/destinazioni/portogallo-15-giorni", "stable", 100, 9.0),
            ("https://blog-viaggiverso.it/destinazioni/capodanno-a-roma", "seasonal_dip", 150, 9.0),
            ("https://blog-viaggiverso.it/destinazioni/toscana-on-the-road", "decline_severe", 780, 3.8),
            ("https://blog-viaggiverso.it/guide/valigia-a-mano-consigli", "decline_demand", 260, 7.5),
            ("https://blog-viaggiverso.it/destinazioni/sicilia-10-giorni", "decline_position", 340, 5.5),
            ("https://blog-viaggiverso.it/guide/assicurazione-viaggio", "decline_yoy", 230, 8.0),
        ],
    },
]


def _closed_months(n=MONTHS_OF_HISTORY):
    """n mesi chiusi più recenti, dal più vecchio al più recente. Mai il mese
    corrente (ancora incompleto) — stessa convenzione di
    app.rules.service._window_start."""
    anchor = date.today().replace(day=1)
    y, m = anchor.year, anchor.month
    m -= 1
    if m == 0:
        y -= 1
        m = 12
    months = []
    for _ in range(n):
        months.append(date(y, m, 1))
        m -= 1
        if m == 0:
            y -= 1
            m = 12
    months.reverse()
    return months


def _month_days(d: date) -> int:
    nxt = date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)
    return (nxt - d).days


def _seed(*parts: str) -> int:
    return zlib.crc32("|".join(parts).encode())


def _profile_curve(profile: str, n: int, rng: random.Random):
    """(click_mult, position_delta, impr_mult): un moltiplicatore/delta per
    mese (vecchio -> recente). Le soglie di riferimento sono quelle di
    app.rules.types.Thresholds (default): finestra 3 mesi, calo >=30%,
    persistenza 2/3 mesi, margine sito 10 punti — ogni profilo "decline_*" è
    tarato con un margine ampio sopra queste soglie per non dipendere dal
    rumore casuale."""
    click_mult = [1.0] * n
    pos_delta = [0.0] * n
    impr_mult = [1.0] * n

    if profile == "stable":
        # Rumore mensile indipendente e limitato (±10%): la media di una
        # finestra di 3 mesi non può mai scostarsi del 30% da quella
        # precedente, quindi non supera mai il filtro pct_loss (per
        # costruzione, non per fortuna).
        for i in range(n):
            click_mult[i] = 1.0 + rng.uniform(-0.10, 0.10)
            pos_delta[i] = rng.uniform(-0.4, 0.4)
            impr_mult[i] = 1.0 + rng.uniform(-0.10, 0.10)
        return click_mult, pos_delta, impr_mult

    if profile in ("decline_position", "decline_demand", "decline_severe"):
        drop = {"decline_position": 0.55, "decline_demand": 0.55, "decline_severe": 0.72}[profile]
        for i in range(n):
            click_mult[i] = 1.0 + rng.uniform(-0.06, 0.06)
            pos_delta[i] = rng.uniform(-0.3, 0.3)
            impr_mult[i] = 1.0 + rng.uniform(-0.06, 0.06)
        tail = min(3, n)  # allineato a window_months=3: non contamina la finestra precedente
        for j, i in enumerate(range(n - tail, n)):
            ramp = (j + 1) / tail
            click_mult[i] = max(0.05, 1.0 - drop * ramp) + rng.uniform(-0.03, 0.03)
            if profile in ("decline_position", "decline_severe"):
                pos_delta[i] = (7.0 if profile == "decline_position" else 13.0) * ramp
            if profile in ("decline_demand", "decline_severe"):
                impr_mult[i] = max(0.10, 1.0 - drop * 0.6 * ramp) + rng.uniform(-0.03, 0.03)
        return click_mult, pos_delta, impr_mult

    if profile == "decline_yoy":
        # Erosione di fondo su tutta la storia (conferma il calo anche vs un
        # anno fa, niente stagionalità) + frenata più netta negli ultimi 3
        # mesi (l'innesco vero e proprio dell'alert).
        for i in range(n):
            t = i / (n - 1)
            slow = 0.28 * t
            click_mult[i] = max(0.15, 1.0 - slow) + rng.uniform(-0.05, 0.05)
            pos_delta[i] = 5.0 * t
            impr_mult[i] = max(0.20, 1.0 - slow * 0.8) + rng.uniform(-0.05, 0.05)
        tail = min(3, n)
        for j, i in enumerate(range(n - tail, n)):
            ramp = (j + 1) / tail
            click_mult[i] *= 1.0 - 0.45 * ramp
            pos_delta[i] += 6.0 * ramp
            impr_mult[i] *= 1.0 - 0.30 * ramp
        return click_mult, pos_delta, impr_mult

    if profile == "seasonal_dip":
        # Bassa stagione ricorrente ogni 12 mesi (fase -8 così l'ultimo
        # trimestre cade in piena bassa stagione): il filtro stagionalità
        # (app.rules.filters.check_seasonality) la deve SCARTARE, perché lo
        # stesso trimestre di un anno fa è altrettanto basso — non è un vero
        # calo. Dimostra la precisione del motore, non solo i falsi positivi.
        for i in range(n):
            season = math.cos(2 * math.pi * (i - 8) / 12)
            click_mult[i] = 1.0 + 0.45 * season + rng.uniform(-0.05, 0.05)
            pos_delta[i] = -1.5 * season
            impr_mult[i] = 1.0 + 0.40 * season + rng.uniform(-0.05, 0.05)
        return click_mult, pos_delta, impr_mult

    raise ValueError(f"profilo sconosciuto: {profile}")


def _page_monthly_rows(user_id, site_url, page_url, profile, base_clicks, base_position, months, rng):
    click_mult, pos_delta, impr_mult = _profile_curve(profile, len(months), rng)
    impr_ratio = rng.uniform(11.0, 16.0)  # impressions ≈ clicks * questo rapporto, a parità di ctr

    rows = []
    for i, month in enumerate(months):
        clicks = max(0, round(base_clicks * click_mult[i]))
        impressions = max(clicks, round(base_clicks * impr_ratio * impr_mult[i]))
        ctr = round(clicks / impressions, 4) if impressions else 0.0
        position = round(max(1.0, base_position + pos_delta[i]), 1)
        rows.append(GscPageMonthly(
            user_id=user_id, site_url=site_url, page_url=page_url, month=month,
            clicks=clicks, impressions=impressions, ctr=ctr, position=position,
        ))
    return rows


def _site_monthly_targets(base_clicks_total, base_impr_total, base_position, months, rng):
    """Andamento di sito INDIPENDENTE dalle singole pagine (rumore contenuto +
    una lieve deriva verso il basso, max ~-8% da inizio a fine storia).

    Deliberatamente non è la somma mese per mese delle pagine modellate: se lo
    fosse, un sito con più pagine in vero calo simultaneo trascinerebbe giù
    anche la media di sito, ed eroderebbe il margine richiesto dal filtro
    site_relative (page_pct <= site_pct - 10 punti, app/rules/filters.py) fino
    a farlo fallire per le pagine con calo più vicino alla soglia — proprio
    quello che è successo in fase di taratura di questo seed. Nessun codice
    del prodotto confronta GscSiteDaily con la somma di GscPageMonthly (sono
    fonti indipendenti anche per un utente reale, letture live separate — vedi
    app/gsc/insights.py), quindi disaccoppiarle qui è sicuro."""
    n = len(months)
    targets = []
    for i, m in enumerate(months):
        drift = 1.0 - 0.08 * (i / (n - 1))
        clicks = max(1, round(base_clicks_total * drift * (1 + rng.uniform(-0.05, 0.05))))
        impressions = max(clicks, round(base_impr_total * drift * (1 + rng.uniform(-0.05, 0.05))))
        position = max(1.0, base_position + 1.5 * (i / (n - 1)) + rng.uniform(-0.3, 0.3))
        targets.append((m, clicks, impressions, position))
    return targets


def _site_daily_rows(user_id, site_url, monthly_targets, rng):
    """monthly_targets: [(month, clicks_totali, impressions_totali,
    posizione_media)]. Distribuisce ogni mese sui suoi giorni con rumore,
    poi ricostruisce ctr/posizione coerenti giorno per giorno."""
    rows = []
    for month, clicks_total, impr_total, position in monthly_targets:
        days_in_month = _month_days(month)
        weights = [max(0.4, 1.0 + rng.uniform(-0.35, 0.35)) for _ in range(days_in_month)]
        wsum = sum(weights)
        allocated_clicks = allocated_impr = 0
        for d in range(days_in_month):
            day = month + timedelta(days=d)
            is_last = d == days_in_month - 1
            if is_last:
                day_clicks = max(0, clicks_total - allocated_clicks)
                day_impr = max(day_clicks, impr_total - allocated_impr)
            else:
                share = weights[d] / wsum
                day_clicks = max(0, round(clicks_total * share))
                day_impr = max(day_clicks, round(impr_total * share))
            allocated_clicks += day_clicks
            allocated_impr += day_impr
            ctr = round(day_clicks / day_impr, 4) if day_impr else 0.0
            day_position = round(max(1.0, position + rng.uniform(-0.8, 0.8)), 1)
            rows.append(GscSiteDaily(
                user_id=user_id, site_url=site_url, date=day,
                clicks=day_clicks, impressions=day_impr, ctr=ctr, position=day_position,
            ))
    return rows


def _reset_demo_data(user_id: int) -> None:
    """Cancella SOLO le righe di questo user_id nelle tabelle popolate dal
    seed, per poter rilanciare il comando in modo idempotente. Nessuna FK a
    cascata da queste tabelle verso User/MonitoredSite (chiavano su
    user_id/site_url stringa, vedi i docstring dei modelli): sicuro."""
    AuditPresentation.query.filter_by(user_id=user_id).delete()
    PageAlert.query.filter_by(user_id=user_id).delete()
    GscPageMonthly.query.filter_by(user_id=user_id).delete()
    GscSiteDaily.query.filter_by(user_id=user_id).delete()
    MonitoredSite.query.filter_by(user_id=user_id).delete()
    GscConnection.query.filter_by(user_id=user_id).delete()
    db.session.commit()


def _seed_fake_gsc_connection(user_id: int) -> None:
    """Riga GscConnection fittizia — serve SOLO a superare il gate `{% if
    connection %}` nei template dashboard/*.html, che altrimenti nascondono
    Pagine in calo / Audit dietro un CTA "connetti Google". access_token
    scaduto e refresh_token assente: un eventuale uso reale (es. bottone
    "Scan now") fallisce SUBITO lato client, senza nessuna chiamata di rete a
    Google, ed è assorbito dagli except già presenti in app/gsc/gsc.py e nei
    job — i cron reali (sync-full-history, run-decay-rules) già saltano allo
    stesso modo un utente "non connesso", quindi anche questo non li altera."""
    from app.gsc.repository import save_gsc_credentials

    save_gsc_credentials(user_id, {
        "token": "demo-fake-access-token",
        "refresh_token": None,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/webmasters.readonly"],
        "expiry": datetime.now(timezone.utc) - timedelta(days=1),
    })


def seed_demo_account(email: str, password: str, name: str = "Alessio Demo") -> dict:
    """Crea/ripristina un account demo con siti finti, 16 mesi di storico GSC
    sintetico e alert generati dal VERO rule engine (non inventati a mano).
    Idempotente: ogni run azzera e rigenera solo i dati di questo indirizzo
    email, non tocca nessun altro account."""
    from app.rules.service import run_for_site

    email = email.lower().strip()
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(name=name, email=email)
        db.session.add(user)
    user.name = name
    user.set_password(password)
    user.email_verified = True
    user.is_admin = False
    user.locale = "it"
    user.subscription_status = "active"
    user.plan_type = "subscription_annual"
    user.billing_interval = "annual"
    user.weekly_digest_enabled = False  # niente email reali dal cron settimanale per questo account
    db.session.commit()

    _reset_demo_data(user.id)
    _seed_fake_gsc_connection(user.id)

    summary = {"user_id": user.id, "email": user.email, "sites": []}
    months = _closed_months()

    for site in SITES:
        site_url = site["site_url"]
        db.session.add(MonitoredSite(
            user_id=user.id, site_url=site_url, is_active=True,
            last_synced_at=datetime.now(timezone.utc),
        ))
        db.session.commit()

        base_clicks_total = base_impr_total = base_weighted_pos = 0.0
        for page_url, profile, base_clicks, base_position in site["pages"]:
            rng = random.Random(_seed(site_url, page_url))
            rows = _page_monthly_rows(user.id, site_url, page_url, profile, base_clicks, base_position, months, rng)
            db.session.bulk_save_objects(rows)
            base_clicks_total += base_clicks
            base_impr_total += base_clicks * 13.5  # stima del rapporto impression/click medio usato in _page_monthly_rows
            base_weighted_pos += base_position * base_clicks
        db.session.commit()

        site_rng = random.Random(_seed(site_url, "site-daily"))
        monthly_targets = _site_monthly_targets(
            base_clicks_total * LONG_TAIL_FACTOR, base_impr_total * LONG_TAIL_FACTOR,
            base_weighted_pos / base_clicks_total, months, site_rng,
        )
        db.session.bulk_save_objects(_site_daily_rows(user.id, site_url, monthly_targets, site_rng))
        db.session.commit()

        # Nessuna sincronizzazione GSC qui: run_for_site legge solo
        # GscPageMonthly/GscSiteDaily già in DB e applica le stesse regole di
        # produzione — è la funzione vera, non una simulazione.
        candidates = run_for_site(user.id, site_url)
        summary["sites"].append({
            "site_url": site_url, "pages": len(site["pages"]), "alerts": len(candidates),
        })

    # Audit presentation vera (stessa pipeline dell'app: DeepSeek trasforma
    # gli alert in slide, vedi app/audits/service.py) per il sito con più
    # alert. Chiamata direttamente (non passa dal job/dal gate crediti AI):
    # il seed non deve consumare crediti né dipendere da un worker RQ attivo.
    top_site = max(summary["sites"], key=lambda s: s["alerts"], default=None)
    summary["audit_presentation"] = None
    if top_site and top_site["alerts"] > 0:
        try:
            from app.audits.service import build_presentation

            presentation = build_presentation(user.id, top_site["site_url"])
            summary["audit_presentation"] = {
                "id": presentation.id, "site_url": presentation.site_url, "title": presentation.title,
            }
        except Exception as exc:  # noqa: BLE001 — l'audit è un bonus: non deve far fallire il seed
            summary["audit_presentation_error"] = str(exc)

    return summary
