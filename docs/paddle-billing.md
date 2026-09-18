# Paddle Billing — architettura, setup, operazioni

Integrazione Paddle Billing come provider **unico** per gli abbonamenti Pro
correnti e i pacchetti crediti AI, in parallelo al canale lifetime AppSumo
(non sostituito). Il vecchio canale Revolut Business (link di pagamento
manuali) è stato dismesso: i campi che scriveva restano in DB solo per
l'audit storico degli utenti già attivati così (vedi §12). Questo documento
copre architettura, setup, eventi gestiti, test, go-live, rollback,
riconciliazione e le policy sui casi limite (cancellazioni, mancati
pagamenti, rimborsi).

## 1. Architettura del flusso

```
Utente clicca "Pay with card"
        │
        ▼
POST /billing/checkout/subscription | /billing/checkout/credits   (app/billing/paddle_routes.py)
    - @login_required
    - valida "plan"/"credit_package" contro whitelist server-side
      (app/billing/paddle_products.py) — MAI un price_id/importo dal client
    - risolve il price_id per l'environment corrente
    - crea una transazione Paddle (POST /transactions, hosted checkout)
    - salva una riga PaddleTransaction status="pending"
    - ritorna { checkout_url } al browser
        │
        ▼
Il browser va su checkout_url (dominio Paddle) — paga lì, MAI sul nostro dominio
        │
        ▼
Paddle reindirizza su PADDLE_SUCCESS_URL (default: /billing/paddle/pending)
    - questa pagina NON legge alcuna prova di pagamento dall'URL/querystring
    - fa polling su GET /billing/status finché has_active_access non è true
        │
        │  (in parallelo, lato server-to-server)
        ▼
POST /webhooks/paddle   (app/webhooks/routes.py)
    - verifica firma HMAC sul RAW body (Paddle-Signature: ts=...;h1=...)
    - idempotenza per event_id (tabella paddle_webhook_events, UNIQUE)
    - subscription.* -> app/billing/paddle_subscriptions.py
        aggiorna User (subscription_status, plan_type, subscription_expires_at, ...)
    - transaction.completed (ai_credits) -> app/billing/paddle_transactions.py
        grant_credits() — stessa funzione condivisa con la quota mensile
    - UNA sola fonte di verità per l'accesso: SOLO il webhook scrive User.
      Il checkout non concede mai nulla, la pagina di ritorno non "vede" mai
      un pagamento riuscito prima del webhook.
```

**Principio cardine**: il callback client-side del checkout Paddle non è mai
trattato come prova di pagamento. `/billing/status` legge solo lo stato già
scritto in DB dal webhook verificato — se il webhook non è ancora arrivato,
l'utente vede "in elaborazione", mai un accesso concesso in anticipo.

## 2. Variabili d'ambiente

Vedi `.env.example` per i commenti riga per riga. Riepilogo:

| Variabile | Scopo |
|---|---|
| `PADDLE_ENVIRONMENT` | `sandbox` (default) o `production` — l'unica leva che decide base URL API e quale set di price ID viene letto |
| `PADDLE_API_KEY` | API key server-side, mai esposta al frontend |
| `PADDLE_WEBHOOK_SECRET` | Solo per verificare `Paddle-Signature` |
| `PADDLE_CLIENT_TOKEN` | Riservato per un futuro overlay Paddle.js — non usato dal checkout hosted attuale |
| `PADDLE_SUCCESS_URL` | Override facoltativo; default: pagina interna `/billing/paddle/pending` |
| `PADDLE_DEFAULT_CURRENCY` | `EUR` di default |
| `PADDLE_SANDBOX_PRICE_ID_*` | Price ID sandbox per i 3 piani Pro + 3 pacchetti crediti |
| `PADDLE_PRODUCTION_PRICE_ID_*` | Equivalenti production — **mai** gli stessi ID di sandbox |

**Nota sulle variabili trovate in `.env` prima di questa integrazione**:
`PADDLE_SANDBOX_API`, `PADDLE_API`, `PADDLE_ID_PRODUCT_1M/3M/12M` erano
scaffolding ad-hoc precedente (in gran parte vuoto), non usato da questa
integrazione — usa invece i nomi documentati sopra. Puoi rimuoverle da `.env`
una volta migrato.

## 3. Sandbox vs production

Il codice applicativo non contiene **mai** un `if environment == ...`
sparso in giro: ogni punto che deve sapere l'environment chiama
`app.billing.paddle_client.get_environment()`, che legge **solo**
`PADDLE_ENVIRONMENT`. Nessuna condizione su host, `DEBUG`, o deploy target.

Passare a production richiede **solo**:
1. `PADDLE_ENVIRONMENT=production`;
2. sostituire `PADDLE_API_KEY` e `PADDLE_WEBHOOK_SECRET` con i valori
   production (Paddle Dashboard, in alto a destra: switch da Sandbox a
   Live);
3. valorizzare i 6 `PADDLE_PRODUCTION_PRICE_ID_*` (vedi §4 sotto);
4. configurare nel Dashboard **production** un endpoint webhook che punti a
   `https://<tuo-dominio>/webhooks/paddle` (sandbox e production hanno
   endpoint/secret webhook separati in Paddle — vanno configurati entrambi
   se vuoi testare in sandbox e vendere in production).

Nessuna modifica al codice applicativo è richiesta per questo passaggio.

## 4. Catalogo e mappatura interna

I tre piani Pro (prezzi in
`app/billing/paddle_products.py::PADDLE_PLAN_PRICES`) sono **abbonamenti
ricorrenti**, uno per ciclo di fatturazione:

| Chiave interna | Ciclo Paddle | Prezzo/ciclo |
|---|---|---|
| `paddle_1m` | ogni 1 mese | €79.90 |
| `paddle_3m` | ogni 3 mesi | €209.90 |
| `paddle_12m` | ogni 1 anno | €790.00 |

Stessi identici limiti tecnici dei tre piani legacy `revolut_1m/3m/12m`
(canale dismesso, vedi §12) — è lo stesso prodotto Pro, cambia solo il
processore. A differenza di quel vecchio flusso (pagamento una tantum per un
periodo fisso, nessun rinnovo automatico), un abbonamento Paddle **si
rinnova da solo** a ogni ciclo finché non viene cancellato.

Pacchetti crediti AI (`app/entitlements/limits.py::AI_CREDIT_PACKS`):
venduti come transazione one-time.

Tutta la mappatura vive in `app/billing/paddle_products.py` — whitelist
server-side, mai un price_id/piano inventato o accettato dal client.

### Setup catalogo (sandbox)

Il server MCP `paddle-sandbox` è utilizzabile per creare/ispezionare
prodotti e price direttamente (usato per popolare il catalogo iniziale il
17/09/2026). In alternativa, o per rilanciare il sync in autonomia, usa il
comando idempotente:

```
flask paddle-sync-catalog --environment sandbox
```

Crea (o recupera, se già esistenti con lo stesso nome/importo) un
prodotto+price per ognuno dei 6 elementi del catalogo e stampa, per
ciascuno, quale variabile `.env` valorizzare:

```
[subscription] paddle_1m: LinkBay CMS — Pro (1 month)
    product_id=pro_xxx  price_id=pri_xxx  (creato)
    -> imposta PADDLE_SANDBOX_PRICE_ID_1M=pri_xxx in .env
...
```

Rilanciabile senza mai duplicare prodotti/prezzi (cerca per nome esatto +
importo/ciclo prima di creare). `--dry-run` mostra cosa farebbe senza
chiamare l'API. Per production: `flask paddle-sync-catalog --environment
production` (farlo solo a go-live deciso, vedi checklist §8).

## 5. Setup webhook Paddle

Nel Dashboard Paddle (sandbox, poi separatamente in production):
Developer Tools → Notifications → **+ New destination**.

- URL: `https://<tuo-dominio>/webhooks/paddle`
- Eventi da abilitare (vedi §6 per il perché di ciascuno):
  `subscription.created`, `subscription.updated`, `subscription.activated`,
  `subscription.past_due`, `subscription.paused`, `subscription.resumed`,
  `subscription.canceled`, `transaction.completed`,
  `transaction.payment_failed`.
- Copia il "Signing secret" mostrato dopo la creazione in
  `PADDLE_WEBHOOK_SECRET`.

## 6. Eventi gestiti

| Evento | Handler | Effetto |
|---|---|---|
| `subscription.created/updated/activated/resumed` | `apply_subscription_event` | Aggiorna `subscription_status`, `plan_type` (se il price_id è whitelistato), `subscription_expires_at`, `current_period_ends_at`, `cancel_at_period_end` |
| `subscription.past_due` | idem | `subscription_status = "past_due"`. **Nessuna grace period inventata**: l'accesso resta valido solo fino a `subscription_expires_at` già noto — nessuna policy di grazia era documentata prima di questa integrazione, quindi non ne aggiungiamo una arbitraria (vedi §9, decisione da confermare) |
| `subscription.paused` | idem | `subscription_status = "paused"` → nessun accesso (`has_active_entitlement` lo esclude esplicitamente) |
| `subscription.canceled` | idem | `subscription_status = "canceled"` → nessun accesso da questo momento nella nostra policy (vedi §9: Paddle a volte manda `canceled` solo a fine periodo, altre volte immediatamente — trattiamo `canceled` come "accesso finito", mai come "ancora attivo fino a una data") |
| `transaction.completed` (`purchase_type=subscription`) | `apply_transaction_completed` | Solo audit (`PaddleTransaction.status="completed"`) — l'accesso lo concede SOLO l'evento `subscription.*`, mai questo |
| `transaction.completed` (`purchase_type=ai_credits`) | idem | `grant_credits()` — una sola volta, idempotente su `paddle_transaction_id` |
| `transaction.payment_failed` | `apply_transaction_payment_failed` | `PaddleTransaction.status="failed"`, nessun credito, nessun cambio di stato subscription |
| qualunque altro tipo | — | Registrato in `paddle_webhook_events` con `status="ignored"`, nessun side effect |

**Idempotenza**: `event_id` è UNIQUE in `paddle_webhook_events` — un replay
Paddle (stesso evento consegnato più volte) ritorna `200 {"status":
"duplicate"}` senza rieseguire nulla. Per i crediti AI c'è una seconda difesa
indipendente: `AiCreditTransaction.payment_reference` è UNIQUE, quindi anche
due *event_id diversi* che puntassero allo stesso `transaction_id` Paddle
non accrediterebbero due volte.

**Fuori ordine**: ogni evento `subscription.*` porta un `occurred_at`. Se
arriva un evento con `occurred_at` più vecchio dell'ultimo già applicato per
quell'utente, viene scartato (`status="ignored"`, motivo salvato) invece di
far tornare indietro lo stato.

**Errori tecnici imprevisti**: se l'applicazione dell'evento solleva
un'eccezione non gestita, l'intera transazione DB fa rollback (nessuna riga
scritta, nemmeno `paddle_webhook_events`) e si risponde `500` — Paddle
ritenterà più tardi e il retry troverà lo stato esattamente come prima,
senza duplicati residui.

## 7. Procedura di test sandbox

1. `flask paddle-sync-catalog --environment sandbox` per popolare i price ID.
2. Esponi l'app in locale (es. `ngrok http 3000`) e registra il webhook
   sandbox (§5) sull'URL pubblico temporaneo.
3. Login come utente di test, vai su `/billing/upgrade`, clicca "Pay with
   card" su un piano.
4. Completa il pagamento con una [carta di test
   Paddle](https://developer.paddle.com/concepts/payment-methods/credit-debit-card#test-cards)
   (es. `4242 4242 4242 4242`, qualunque data futura/CVC).
5. Verifica: redirect su `/billing/paddle/pending` → dopo pochi secondi
   (arrivo del webhook) redirect automatico a `/billing/subscription` con
   piano attivo.
6. In `/admin/paddlewebhookevent/` verifica la riga `subscription.created`
   con `status=processed`; in `/admin/paddletransaction/` la riga
   `transaction.completed` collegata.
7. Ripeti per un pacchetto crediti AI su `/billing/credits` (richiede un
   utente su un piano con `ai_credit_topups_allowed=True`, oggi solo i tier
   AppSumo).

Suite automatica (nessuna chiamata di rete reale, tutto mockato):
```
pytest tests/test_paddle_*.py -q
```

## 8. Checklist go-live production

- [ ] `flask paddle-sync-catalog --environment production` eseguito, i 6
      `PADDLE_PRODUCTION_PRICE_ID_*` valorizzati in `.env` di produzione
- [ ] `PADDLE_API_KEY`/`PADDLE_WEBHOOK_SECRET` production impostati (mai gli
      stessi di sandbox)
- [ ] Endpoint webhook production creato nel Dashboard Paddle (Live), con
      gli stessi eventi elencati in §5
- [ ] `PADDLE_ENVIRONMENT=production` impostato **per ultimo**, dopo aver
      verificato tutto il resto
- [ ] Un acquisto reale di test (carta vera, importo minimo) completato e
      verificato end-to-end
- [ ] Team avvisato: da questo momento `/billing/upgrade` addebita
      davvero

## 9. Decisioni che richiedono conferma business

Questa implementazione **non inventa** policy non documentate nel codice
esistente. I punti seguenti sono stati risolti nel modo più conservativo
possibile e vanno confermati/affinati da chi decide il prodotto:

- **Grace period su `past_due`**: nessuna. L'accesso Paddle resta valido
  solo fino a `subscription_expires_at` già noto (l'ultimo
  `current_billing_period.ends_at` ricevuto) — non estendiamo l'accesso di
  giorni extra dopo un pagamento fallito. Se volete un grace period
  esplicito (es. 3 giorni), va aggiunto consapevolmente in
  `app/entitlements/service.py::has_active_entitlement`.
- **`subscription.canceled`**: trattato come "accesso terminato subito"
  nella nostra policy locale (`has_active_entitlement` esclude
  `"canceled"`), anche se Paddle a volte manda questo evento solo a fine
  periodo. Se la UX desiderata è "resta attivo fino alla fine del periodo
  già pagato anche dopo cancellazione", va deciso esplicitamente — oggi
  **non è questo il comportamento**.
- **Refund/chargeback**: NON gestiti automaticamente (nessun evento
  `adjustment.*`/webhook di refund sottoscritto). Un rimborso Paddle non
  revoca oggi né l'accesso né i crediti AI accreditati — non esisteva una
  policy di claw-back documentata da cui partire, anche se
  `adjust_credits()` in app/entitlements resta disponibile per uno storno
  manuale da admin. Se serve, va aggiunto un handler per l'evento di refund
  Paddle con una policy esplicita, non inventata qui.
- **Grace period per crediti AI insufficienti dopo downgrade**: non
  applicabile, i crediti non scadono mai (comportamento invariato).

## 10. Rollback

Paddle è additivo: disabilitarlo non richiede rimuovere codice.

- **Rollback immediato (nascondere le CTA)**: svuota tutti i
  `PADDLE_*_PRICE_ID_*` per l'environment attivo — le card "Pay with card"
  spariscono da `/billing/upgrade` e `/billing/credits` (bottone disabilitato
  invece di un price_id vuoto), AppSumo resta intatto.
- **Rollback completo**: rimuovi l'endpoint webhook dal Dashboard Paddle
  (Paddle smette di consegnare eventi) e svuota `PADDLE_API_KEY` — ogni
  chiamata di checkout fallirà con `503 not_configured` invece di un errore
  silenzioso.
- Nessun utente AppSumo/legacy viene mai toccato da questi rollback: i loro
  campi (`subscription_source` diverso da `"paddle"`) non sono letti da
  nessun codice Paddle.

## 11. Riconciliazione (webhook persi o stato incoerente)

```
flask paddle-reconcile --environment sandbox            # dry-run, sola lettura
flask paddle-reconcile --environment sandbox --apply    # scrive davvero
flask paddle-reconcile --environment production --user-id 42 --apply
```

Rilegge da Paddle lo stato reale di ogni subscription collegata a un utente
locale (`subscription_source == "paddle"`, stesso `paddle_environment`
richiesto) e lo riapplica con la **stessa** funzione usata dal webhook
(`apply_subscription_event`) — nessuna logica duplicata. Stampa un report
prima/dopo per ogni utente controllato. Non tocca mai utenti
AppSumo/legacy, né l'altro environment.

## 12. Utenti legacy Revolut/AppSumo

Il canale Revolut Business (link di pagamento manuali, attivazione da
Flask-Admin) è stato dismesso: il codice che lo implementava
(`app/billing/revolut_*.py`, le view admin dedicate, i template) non esiste
più. Gli utenti già attivati così restano com'erano — i campi che quel flusso
scriveva (`plan_type` in `revolut_1m/3m/12m`, `subscription_activated_at`,
`subscription_activation_reference`, ecc.) restano in DB solo per l'audit
storico, e `PLAN_LIMITS`/`has_active_access` continuano a riconoscerli senza
bisogno di alcuna migrazione: un utente Revolut manuale o AppSumo lifetime
continua esattamente come prima finché non effettua volontariamente un
acquisto Paddle (a quel punto `subscription_source` diventa `"paddle"` per
quell'utente). `app/billing/paddle_subscriptions.py::apply_subscription_event`
protegge esplicitamente gli account `subscription_status == "lifetime"`: un
evento Paddle non può mai declassare un account AppSumo, qualunque cosa
dica il payload.

Associazione manuale (recupero di un `custom_data` perso, o migrazione
concordata col cliente): campi `paddle_customer_id`/`paddle_subscription_id`
editabili in `/admin/user/` — vedi `app/admin/views.py::UserAdminView`.
