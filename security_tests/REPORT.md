# Audit di sicurezza LinkBay-CMS — 2026-10-15

> **Aggiornamento (stesso giorno): F-01…F-05 corretti** (modifiche non committate). I relativi
> test `FINDING` sono stati invertiti in test di regressione: `tests/` 198 passed / 1 skipped
> (preesistente), `security_tests/` 84 passed, PoC in browser →
> `injected_attribute_present:false, handler_executed:false`.
>
> | ID | Correzione | File |
> |---|---|---|
> | F-01 | Rimossa la porta `5432` del servizio `db`; password da `${POSTGRES_PASSWORD:?}` in `.env`, anche in `DATABASE_URL` | `compose.prod.yml`, `.env.example` |
> | F-02 | Niente default per `SECRET_KEY`; `create_app` rifiuta di partire con chiave assente, vuota o uguale ai due valori pubblici (vecchio default e placeholder di `.env.example`, ora vuoto) | `config.py`, `app/__init__.py`, `.env.example` |
> | F-03 | `esc()` fa l'escape di `& < > " '` | `app/static/js/common.js`, `app/static/js/chat-widget.js` |
> | F-04 | Il login non emette un nuovo OTP durante il cooldown; rate limit su POST di login (10/min, 50/h), verify (10/min, 60/h), resend e forgot-password (5/min, 20/h) | `app/auth/routes.py` |
> | F-05 | `meta={"user_id": …}` all'enqueue; `job_status_payload(job_id, user_id)` restituisce `not_found` se l'owner non coincide | `app/jobs/queue.py`, `app/ai/routes.py`, `app/audits/routes.py`, `tests/test_jobs.py` |
>
> Passi manuali di deploy ancora necessari: vedi la risposta in chat oppure i commenti in `.env.example`.
> Le sezioni seguenti descrivono lo stato **prima** delle correzioni.

## 1. Perimetro

| Voce | Valore |
|---|---|
| Branch / commit | `main` @ `81c145eb` |
| Modifiche locali | solo file non tracciati preesistenti (`.agents/`, `.claude/skills/`, `skills-lock.json`), non toccati |
| Codice analizzato | `app/`, `config.py`, `run.py`, `gunicorn.conf.py`, `Dockerfile`, `compose.yml`, `compose.prod.yml`, `crontab`, `requirements*.txt`, `tests/`, `app/static/js/` |
| Ambiente di test | copia pulita del repo nello scratchpad **senza** `.env*` e `client_secret*`, `PYTHON_DOTENV_DISABLED=1`, ambiente vuoto (`env -i`), SQLite in memoria, fakeredis, rete in uscita bloccata a livello di socket, stub per Google OAuth / Search Console / Resend / DeepSeek |
| Fuori perimetro | produzione, domini reali, Google, Paddle, Resend, Cloudflare, server di deploy |
| Segreti | `.env`, `.env.try`, `client_secret.json` **non letti**. Sono in `.gitignore` e assenti dalla storia git (`git log --all -- …` vuoto) |

**Nota funzionale:** i *magic-link* non esistono nel codice. L'autenticazione è email + password, seguita da un OTP a 6 cifre via email. Il recupero password usa un token-link monouso.

## 2. Strumenti e comandi realmente eseguiti

| Comando | Esito |
|---|---|
| `docker info`, `strix --version`, verifica `STRIX_LLM`/`LLM_API_KEY` | Docker spento, Strix assente, nessuna chiave. **Strix NON eseguito** (non autorizzato: richiede l'invio di codice/risposte a un LLM o al cloud Strix) |
| Analisi statica manuale + `grep` (route, decorator, sink HTML, SQL testuale, richieste in uscita, exec/pickle/file) | vedi §4 |
| `env -i PATH=… PYTHON_DOTENV_DISABLED=1 venv/bin/python -m pytest security_tests -v -p no:cacheprovider` (sulla copia pulita) | **77 passed** (63 controlli superati + 14 test `FINDING` che dimostrano un difetto). Output salvato nello scratchpad (`pytest_output.txt`) |
| Chrome headless con profilo isolato, `--host-resolver-rules="MAP * ~NOTFOUND"`, `--dump-dom file://…/security_tests/js/esc_attribute_injection.html` | `{"injected_attribute_present":true,"handler_executed":true}` |
| `pip-audit 2.10.1 -r requirements.txt --no-deps --disable-pip` (venv temporaneo nello scratchpad) | 10 advisory in 5 pacchetti, vedi §6 |

Convenzione dei test: un test `test_FINDING_*` **passa quando il difetto è presente**. Dopo la correzione va invertito e diventa il test di regressione. Tutti gli altri test passano quando il controllo regge.

**Correzione dell'harness (nessuna modifica all'app):** le richieste del test client girano dentro l'app context della fixture, quindi `flask.g` (utente di Flask-Login, token CSRF di Flask-WTF) sopravviveva tra richieste e tra client diversi. Questo falsava i test con due client. `security_tests/conftest.py` svuota `g` all'inizio di ogni richiesta, ripristinando la semantica di produzione, dove ogni richiesta ha il suo app context. I risultati riportati sono quelli dopo la correzione.

## 3. Sintesi

L'isolamento dei dati tra utenti **regge** su tutti gli endpoint con identificativi di risorse: alert, trend, query-losses, audit, export, siti monitorati. Reggono anche CSRF, accessi anonimi, mass assignment, `state`/PKCE di OAuth, la cifratura dei token Google e la firma dei webhook Paddle (coperta dai test esistenti).

I rischi principali sono altrove:

1. **Configurazione di deploy:** porta Postgres pubblicata con credenziali scritte nel compose di produzione.
2. **Configurazione dell'app:** un `SECRET_KEY` di fallback presente nel repository consente di forgiare la sessione di qualsiasi utente se la variabile manca in produzione.
3. **XSS persistente lato client:** l'helper `esc()` non fa l'escape delle virgolette e viene usato dentro attributi HTML con dati di Search Console.
4. **Brute force dell'OTP:** il limite di 5 tentativi si azzera a ogni login e il login non ha rate limit.
5. **Ownership dei job asincroni assente** su due endpoint di polling.

## 4. Tabella dei risultati

| ID | Titolo | Severità | Confidenza | Stato |
|---|---|---|---|---|
| F-01 | Porta Postgres esposta e credenziali hardcoded in `compose.prod.yml` | **Alta** (critica se raggiungibile) | Alta (configurazione) | Esposizione di porta e credenziali hardcoded nella configurazione. **Raggiungibilità esterna non verificata** |
| F-02 | `SECRET_KEY` con fallback pubblico: forgiatura della sessione | **Alta** (condizionata) | Alta | Vulnerabilità confermata, condizionata all'assenza di `SECRET_KEY` nell'ambiente di prod (non verificato) |
| F-03 | `esc()` non fa l'escape di `"`/`'`: XSS in attributi con dati GSC | **Media-Alta** | Alta (difetto) / Media (sfruttabilità via GSC) | Debolezza confermata in browser. Iniezione tramite query GSC reali: plausibile |
| F-04 | Limite tentativi OTP aggirabile rifacendo il login; login senza rate limit; flood di email OTP | **Media** | Alta | Vulnerabilità confermata (richiede la password) |
| F-05 | `/ai/analyze-status/<job_id>` e `/dashboard/audits/generate-status/<job_id>` senza controllo di ownership | **Media** | Alta | Vulnerabilità confermata |
| F-06 | Il sito monitorato non viene verificato server-side contro le property GSC; `/gsc/api/insights` accoda scan oltre il limite del piano | **Bassa-Media** | Alta | Vulnerabilità confermata (abuso di risorse; i dati di Google restano protetti dal token dell'utente) |
| F-07 | Rate limit di `/chat/ask` (endpoint pubblico che consuma DeepSeek) basato su `X-Forwarded-For` | **Media** (costo) | Media | Rischio plausibile: confermato a livello di app, dipende da Traefik/Cloudflare (non verificato) |
| F-08 | Reset e cambio password non invalidano le sessioni esistenti | **Bassa-Media** | Alta | Confermato (hardening) |
| F-09 | Open redirect tramite header `Referer` su `/lang/<code>` | Bassa | Alta | Confermato |
| F-10 | Logout tramite GET (CSRF logout) | Bassa | Alta | Confermato |
| F-11 | Enumerazione degli account in registrazione | Bassa | Alta | Confermato (mitigato da 5 richieste/min) |
| F-12 | Nessun header di sicurezza (CSP, X-Frame-Options, nosniff, HSTS, Referrer-Policy) | Bassa (hardening; la CSP mitigherebbe F-03) | Alta | Confermato |
| F-13 | Riscatto AppSumo: niente rate limit, niente lock sulla riga (doppio riscatto concorrente) | Bassa-Media | Media | Rischio plausibile, **non testato dinamicamente** |
| F-14 | `compose.yml` (dev): Redis `6379` e Postgres `5432` pubblicati su tutte le interfacce, senza auth/con password nota. RQ deserializza i job con pickle | Media (rete locale/dev) | Media | Rischio plausibile (non provato) |
| F-15 | Container eseguiti come root; `.:/app` montato in prod (incluso `.env`); `docker.sock` montato in Traefik | Hardening | Alta | Raccomandazione |
| F-16 | Dipendenze con advisory (cryptography, oauthlib, urllib3, weasyprint, werkzeug) | Bassa (nessuna raggiungibile dimostrata) | Media | Presenza confermata; raggiungibilità analizzata in §6 |

## 5. Dettaglio delle vulnerabilità

### F-01 — Porta Postgres esposta e credenziali hardcoded (prod)
- **File:** `compose.prod.yml:36` (`POSTGRES_PASSWORD: linkbay`), `compose.prod.yml:39` (`"5432:5432"`). Lo stesso schema si ripete in `web`/`cron`/`worker` dentro `DATABASE_URL`.
- **Prerequisiti:** che la porta 5432 dell'host sia raggiungibile. Le porte pubblicate da Docker inseriscono proprie regole iptables e notoriamente **scavalcano UFW**: un firewall dell'host non basta a escluderlo.
- **Riproduzione:** `security_tests/test_misc.py::test_FINDING_prod_compose_publishes_postgres_with_hardcoded_credentials` (verifica statica). La raggiungibilità dall'esterno **non è stata verificata**: fuori perimetro.
- **Impatto se raggiungibile:** lettura e scrittura completa del DB (utenti, hash delle password, token GSC cifrati, stato di billing).
- **Correzione minima:** rimuovere `ports: - "5432:5432"` dal servizio `db` in `compose.prod.yml` (l'app lo raggiunge via rete Docker interna su `db:5432`). Spostare la password in `.env` (`POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}`, `DATABASE_URL` costruito da quella), poi ruotarla, perché quella attuale è pubblica nel repository. Per l'accesso amministrativo usare `docker compose exec db psql` o un tunnel SSH.
- **Regressione:** invertire il test (assert che `5432` non sia pubblicato e che la password non compaia in chiaro).

### F-02 — `SECRET_KEY` con fallback pubblico
- **File:** `config.py:10` (`os.environ.get("SECRET_KEY", "dev-secret-key-change-me")`).
- **Prerequisiti:** processo di produzione avviato senza `SECRET_KEY` (ad esempio `.env` incompleto). Non verificato: il `.env` non è stato letto, per istruzione.
- **Riproduzione:** `test_misc.py::test_FINDING_secret_key_fallback_allows_session_forgery`. In un sottoprocesso senza `SECRET_KEY`, l'app parte senza errori. Un cookie `session` firmato con la stringa pubblica `{"_user_id": "<id>", "_fresh": true}` restituisce **200** su `/settings/`.
- **Atteso / osservato:** atteso il rifiuto all'avvio; osservati avvio e takeover dell'account.
- **Impatto:** accesso come qualsiasi utente, incluso un `is_admin` (Flask-Admin). Il secondo fattore OTP viene saltato del tutto.
- **Correzione minima:** in `Config`, `SECRET_KEY = os.environ["SECRET_KEY"]`, oppure in `create_app` un `raise RuntimeError` se la chiave manca o vale il default e `not app.debug and not app.testing`.
- **Regressione:** il test inverso, cioè che l'avvio senza `SECRET_KEY` fallisca.

### F-03 — `esc()` non fa l'escape delle virgolette (XSS in attributi)
- **File:** `app/static/js/common.js:11`. È usato in contesto di attributo in `insights.js:147,164,165,193`, `declining.js:98,144,146,166`, `overview.js:67,68`, `sites.js:57,75` e `common.js:144`.
- **Sorgenti dei dati:** le query di ricerca e gli URL di pagina restituiti da Search Console (`q.query`, `p.url`, `a.url`). Le query sono **testo digitato da terzi** su Google.
- **Riproduzione:** aprire `security_tests/js/esc_attribute_injection.html` in un browser (eseguito in Chrome headless isolato). La query `x" onmouseover="window.__xss=1" data-x="` produce `esc()` = invariato, l'attributo `onmouseover` viene creato e l'**handler viene eseguito**.
- **Prerequisiti di sfruttamento:** che GSC riporti per il sito della vittima una query contenente `"` (le query rare sono anonimizzate da Google). Questa parte è plausibile ma **non verificata**.
- **Impatto:** esecuzione di JS nella sessione della vittima: lettura dei dati del dashboard, azioni con il token CSRF letto dal `<meta>`, disconnessione di GSC, consumo di crediti AI. Il cookie di sessione è `HttpOnly`, quindi non è leggibile.
- **Correzione minima (una riga):**
  ```js
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  ```
  Allineare anche la copia in `chat-widget.js:39`. Per gli `href` valutare un controllo `^https?://`.
- **Regressione:** la stessa pagina PoC deve restituire `injected_attribute_present: false`.

### F-04 — OTP: il limite tentativi si azzera a ogni login; login senza rate limit
- **File:** `app/auth/routes.py:77-91` (nessun `@limiter.limit`), `app/auth/routes.py:88`, `app/auth/otp.py:54-59` (`issue_code` cancella l'OTP precedente, quindi azzera `attempts`, e non applica il cooldown al login).
- **Prerequisiti:** conoscere la password della vittima (password riusata, leak).
- **Riproduzione:**
  - `test_auth.py::test_FINDING_otp_attempt_limit_resets_on_every_login`: 3 login e 15 codici errati sullo stesso account. Il codice corretto resta accettato e partono 4 email OTP senza cooldown.
  - `test_FINDING_login_has_no_rate_limit`: 30 login errati, nessun 429.
  - Controllo: `/auth/verify/resend` rispetta il cooldown e `/auth/register` è limitato.
- **Impatto:** il secondo fattore si riduce a circa 200k login in media per un brute force a 6 cifre, una soglia raggiungibile senza rate limit. Le email OTP partono illimitate verso la vittima (costo Resend e reputazione del dominio). Il brute force della password è libero.
- **Correzione minima:**
  1. `@limiter.limit("10 per minute;50 per hour")` su `login`, `verify` e `forgot_password`.
  2. In `_start_otp_flow` per il login, se esiste un OTP non scaduto e il cooldown non è passato, non emetterne uno nuovo (riusare `can_resend`).
- **Regressione:** invertire i due test `FINDING`.

### F-05 — Polling dei job senza controllo di ownership
- **File:** `app/jobs/queue.py:30` (`job_status_payload` fa `Job.fetch(job_id)` senza utente), `app/ai/routes.py:75`, `app/audits/routes.py:63`. In `generate_status` il `presentation_id` "pulito" viene filtrato, ma `job_result` viene restituito integralmente.
- **Riproduzione:** `test_authz.py::test_FINDING_ai_analyze_status_returns_other_users_job_result` e `::test_FINDING_audit_generate_status_returns_other_users_job_result`. A ottiene `job_result` (messaggio d'errore, `presentation_id`) di un job di B.
- **Impatto:** lettura dell'esito dei job di altri utenti (messaggi d'errore del provider AI, ID delle presentation). È un difetto di autorizzazione, indipendentemente dalla difficoltà di indovinare gli UUID.
- **Correzione minima:** in `enqueue(..., meta={"user_id": current_user.id})`. In `job_status_payload(job_id, user_id)`, se `job.meta.get("user_id") != user_id` restituire `{"status": "not_found"}`.
- **Regressione:** invertire i due test (atteso `not_found`).

### F-06 — Sito non verificato contro GSC; scan oltre il limite del piano
- **File:** `app/gsc/gsc.py:206` (`api_monitored_site` accetta qualunque stringa), `app/gsc/gsc.py:309,339` (`api_insights` accoda `run_gsc_scan_job` per qualsiasi `site`, anche non monitorato). Lo stesso schema vale per `POST /ai/analyze` e `POST /dashboard/audits/generate`.
- **Riproduzione:** `test_misc.py::test_FINDING_monitored_site_not_verified_against_gsc` (accettato `https://not-my-property.example/`) e `::test_FINDING_insights_enqueues_scan_for_site_beyond_plan_limit`: con il limite raggiunto, l'aggiunta esplicita dà 403 (controllo), ma `/gsc/api/insights?site=<extra>` accoda comunque lo scan.
- **Impatto:** aggiramento del `site_limit` del piano e consumo di worker e quota API. Non permette di leggere dati altrui: le chiamate a Google usano il token dell'utente e Google rifiuta le property non sue.
- **Correzione minima:** in `api_insights`, `/ai/analyze` e `/audits/generate` richiedere `get_monitored_site_row(user.id, site)` attivo, altrimenti 404. In `api_monitored_site`, se `service` è disponibile, verificare che `site` sia in `service.sites().list()`.
- **Regressione:** invertire i due test.

### F-07 — Rate limit di `/chat/ask` dipendente da `X-Forwarded-For`
- **File:** `app/chat/routes.py:42-43` (pubblico, `csrf.exempt`, limite per IP), `app/__init__.py:21` (`ProxyFix(x_for=1, …)`).
- **Riproduzione:** `test_misc.py::test_FINDING_chat_rate_limit_keyed_on_forwarded_for`. Con IP fisso scatta il 429 (controllo); ruotando l'header `X-Forwarded-For` nessun 429 su 20 richieste.
- **Da verificare (non eseguito, fuori perimetro):** cosa arriva davvero all'app dietro Traefik (e Cloudflare, se in modalità proxy). Se Traefik sovrascrive l'header, l'IP visto potrebbe essere quello dell'edge Cloudflare (limite condiviso da tutti) oppure il client potrebbe controllarlo.
- **Impatto:** chiamate DeepSeek a pagamento senza autenticazione e senza un tetto globale.
- **Correzione minima:** verificare la catena di proxy in staging e impostare `x_for` sul numero reale di hop fidati. Aggiungere un limite globale, ad esempio `@limiter.limit("500 per day", key_func=lambda: "chat-global")`.

### F-08 — Le sessioni sopravvivono a reset/cambio password
- **File:** `app/auth/password_reset.py:97` (`consume`), `app/settings/routes.py` (cambio password), `user_loader` in `app/__init__.py`.
- **Riproduzione:** `test_auth.py::test_FINDING_password_reset_does_not_invalidate_existing_sessions`. La sessione già aperta resta valida (200) dopo il reset.
- **Impatto:** chi ha rubato una sessione la conserva anche dopo che la vittima ha cambiato password.
- **Correzione minima:** salvare in sessione, al login, un'impronta (ad esempio i primi 16 caratteri dell'hash password) e confrontarla nel `user_loader`. Se non coincide, restituire `None`.

### F-09 / F-10 / F-11 / F-12 — Problemi minori confermati
- **F-09:** `app/main/routes.py:53` `redirect(request.referrer …)`. Test `test_FINDING_open_redirect_via_referer`. Correzione: redirect solo se `urlparse(ref).netloc` coincide con `request.host`, altrimenti `url_for("main.index")`.
- **F-10:** `app/auth/routes.py:214` logout via GET. Test `test_FINDING_logout_via_get`. Correzione: `methods=["POST"]` più un form con `csrf_token`.
- **F-11:** `app/auth/routes.py` register, messaggio "There is already an account…". Test `test_FINDING_register_enumerates_existing_email`. Mitigato dal limite di 5 richieste/min. Correzione facoltativa: messaggio neutro più email all'indirizzo esistente.
- **F-12:** test `test_FINDING_no_security_headers`. Correzione: un `@app.after_request` con `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` e HSTS (o via middleware Traefik). Una CSP richiede di censire gli script inline e i CDN usati: da fare dopo F-03.

### F-13 — Riscatto AppSumo (non testato dinamicamente)
- **File:** `app/billing/routes.py:65-89`: legge `is_redeemed` e poi scrive, senza `with_for_update()` né rate limit. Il blueprint `billing` non è tra quelli con limite per piano.
- **Motivo per cui non è stato testato:** con SQLite in memoria e una singola connessione la race non è riproducibile in modo affidabile. Servirebbe un Postgres di test dedicato.
- **Correzione minima:** `AppSumoCode.query.filter_by(code=…).with_for_update().first()` (oppure `UPDATE … WHERE redeemed_at IS NULL` controllando il rowcount) più `@limiter.limit("10 per hour")`.

### F-14 / F-15 — Compose dev e container
- `compose.yml:10,53`: Postgres e Redis pubblicati su `0.0.0.0` della macchina di sviluppo. Redis è senza password e RQ deserializza i job con pickle, quindi chi raggiunge la porta 6379 dalla LAN può far eseguire codice al worker. Correzione: `"127.0.0.1:5432:5432"` e `"127.0.0.1:6379:6379"`. **Non provato.**
- `Dockerfile`: nessun `USER` non-root. `compose.prod.yml` monta `.:/app` (incluso `.env`) in `web`/`cron`/`worker`. Traefik monta `docker.sock`. Hardening: `USER` dedicato nel Dockerfile, nessun bind-mount del sorgente in prod (l'immagine contiene già il codice, i segreti arrivano solo da `env_file`).

## 6. Dipendenze (`pip-audit`, servizio PyPI)

| Pacchetto | Versione | Advisory | Fix | Raggiungibilità nell'app |
|---|---|---|---|---|
| cryptography | 49.0.0 | PYSEC-2026-3552 / CVE-2026-69247 / GHSA-g6cj-pr64-35w5 (PKCS7 decrypt) | 50.0.0 | **Non raggiungibile**: l'app usa solo Fernet |
| oauthlib | 3.3.1 | PYSEC-2026-4114 / CVE-2026-49265 / GHSA-xpv3-w29h-x7cv (timing PKCE lato server) | 4.0.0 | **Non raggiungibile**: l'app è client OAuth, non authorization server. Verificare la compatibilità di `requests-oauthlib`/`google-auth-oauthlib` prima di passare alla 4.x |
| urllib3 | 2.7.0 | PYSEC-2026-4175/4176/4177 (TLS verso proxy HTTPS; decompressione in streaming) | 2.8.0 | Bassa: richieste solo verso host fissi (Google, Paddle, DeepSeek, Cloudflare), nessun proxy configurato |
| weasyprint | 69.0 | PYSEC-2026-3940 (bypass di `url_fetcher`), PYSEC-2026-4311 (immagini via Pillow/Ghostscript) | 70.0 | **Non raggiungibile allo stato attuale**: `exports/declining_report.html` è autoescaped, senza `<img>`/`<link>`, e non usa `url_fetcher` |
| werkzeug | 3.1.8 | PYSEC-2026-4312 (`safe_join` su Windows) | 3.1.9 | **Non raggiungibile**: deploy Linux, nessun `send_from_directory` nell'app |

Gli aggiornamenti restano consigliati ma nessuno è urgente.

## 7. Controlli superati

- **Isolamento A/B:** `alerts/api/list`, `api/trend`, `api/query-losses`, `api/status` (scrittura), `audits/<id>` e `/download`, `exports/declining.csv`, `gsc/api/monitored-site/remove`. Tutti filtrano per `current_user.id`; nessuna risorsa di B è letta o modificata.
- **Accesso anonimo:** 24 endpoint GET protetti restituiscono redirect al login.
- **CSRF:** 12 POST che modificano stato restituiscono 400 senza token. Le esenzioni presenti sono motivate: webhook Paddle (firma HMAC) e `/chat/ask` (senza stato).
- **Mass assignment:** `/settings/` ignora `is_admin`, `plan_type`, `subscription_status`, `ai_credit_balance` e `white_label_enabled` (non consentito dal piano).
- **OTP:** il codice è monouso, scade, il resend rispetta il cooldown e viene salvato hashato (da codice).
- **Reset password:** il token è monouso, scade ed è salvato come hash; la risposta di forgot-password non permette l'enumerazione. Il login ha un messaggio d'errore unico.
- **OAuth GSC:**
  - scope `webmasters.readonly`;
  - `state` legato alla sessione (rifiutati mancante, errato e quello di un'altra sessione) e replay rifiutato;
  - PKCE attivo;
  - callback anonima rifiutata;
  - token cifrati con Fernet in DB;
  - nessun token in HTML, log o `/gsc/api/sites`;
  - nessuna chiave di cifratura di fallback.
- **Rendering:** nessun `|safe` su dati utente (unico uso: il footer statico). Le audit presentation passano per `markupsafe.escape`. L'export PDF è autoescaped. Le pagine 404 non mostrano traceback.
- **Cookie:** `HttpOnly`, `SameSite=Lax` e `Secure` attivo quando `APP_BASE_URL` è https.
- **SQL:** l'unico SQL testuale (`_ensure_columns`) usa solo costanti del codice.
- **SSRF / exec / file:** le richieste in uscita vanno solo verso URL fissi; non ci sono `subprocess`, `eval`, upload, `send_file` o deserializzazione di input utente nel codice web.
- **Segreti nel repo:** nessun file di segreti tracciato né presente nella storia.

## 8. Limitazioni e controlli non eseguiti

- **Strix:** non eseguito (non autorizzato l'invio di dati a provider LLM o al cloud; inoltre Docker era spento, Strix non installato e nessuna chiave disponibile).
- **Raggiungibilità reale di Postgres** (F-01), **catena Traefik/Cloudflare e header proxy** (F-07), **presenza di `SECRET_KEY` in prod** (F-02): richiedono l'accesso al deployment, fuori perimetro.
- **Race AppSumo** (F-13) e **concorrenza degli slot di scan**: servono un Postgres e un Redis reali dedicati ai test; non eseguito.
- **Sfruttamento di F-03 tramite dati GSC reali:** non verificabile senza Google.
- **Non testati dinamicamente:** Flask-Admin (solo `is_admin`, analizzato staticamente), endpoint di checkout/portal Paddle (coperti dai test esistenti in `tests/`), digest email, prompt injection verso DeepSeek tramite dati GSC (l'output viene comunque escapato in UI), formula injection nel CSV.
- I test girano su SQLite: i comportamenti specifici di Postgres non sono coperti.

## 9. Interventi raccomandati

### 1. Da correggere prima del deploy
1. **F-01:** rimuovere `5432:5432` da `compose.prod.yml`, spostare la password del DB in `.env` e **ruotarla**.
2. **F-02:** far fallire l'avvio se `SECRET_KEY` manca o è il default; verificare che sia impostata in prod.
3. **F-03:** correggere `esc()` (una funzione in `common.js` e la copia in `chat-widget.js`).
4. **F-04:** rate limit su `login`/`verify`/`forgot-password` e nessun nuovo OTP al login durante il cooldown.
5. **F-05:** `meta={"user_id": …}` sui job e controllo in `job_status_payload`.

### 2. Da correggere a breve
6. **F-06:** richiedere un sito monitorato attivo in `api_insights`, `/ai/analyze` e `/audits/generate`; verificare la property contro GSC all'aggiunta.
7. **F-07:** verificare in staging la catena di proxy, poi correggere `x_for` e aggiungere un tetto globale a `/chat/ask`.
8. **F-08:** invalidare le sessioni al cambio o reset della password.
9. **F-13:** lock sulla riga e rate limit sul riscatto AppSumo.
10. **F-14:** legare Postgres e Redis a `127.0.0.1` in `compose.yml`.

### 3. Hardening opzionale
11. **F-12:** header di sicurezza, poi una CSP.
12. **F-09, F-10, F-11:** redirect solo verso lo stesso host, logout via POST, messaggio di registrazione neutro.
13. **F-15:** utente non-root nel Dockerfile, nessun bind-mount del sorgente in prod.
14. **F-16:** aggiornare cryptography, urllib3, weasyprint e werkzeug alle versioni con fix (oauthlib 4.x dopo un controllo di compatibilità).

## 10. File creati

- `security_tests/__init__.py`, `conftest.py`, `test_authz.py`, `test_auth.py`, `test_oauth.py`, `test_misc.py`
- `security_tests/js/esc_attribute_injection.html`
- `security_tests/REPORT.md` (questo file)
- Nello scratchpad di sessione (temporanei): copia pulita del repo, `audit-venv`, `pip-audit.json`, `pytest_output.txt`, profilo Chrome isolato.

Nessun file applicativo modificato, nessun commit.

Comando di riesecuzione (dalla root del repo):
```bash
env -i PATH="$PATH" HOME="$HOME" PYTHON_DOTENV_DISABLED=1 venv/bin/python -m pytest security_tests -v -p no:cacheprovider
```
