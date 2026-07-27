# LinkBay Admin

Base tecnica pulita per un SaaS: Flask, Postgres, login, e una struttura pronta a crescere per blueprint. Questo README è pensato per te tra una settimana, quando non ricorderai più i dettagli: leggilo dall'inizio, non serve altro.

> Nota: le versioni precedenti di questo README descrivevano un prodotto diverso (un monitor SEO). Quella visione di business resta in [BUSINESS_PLAN.md](BUSINESS_PLAN.md) se vuoi recuperarla; questo file descrive lo stato **tecnico attuale** del codice.

---

## Cosa è stato impostato

- **Flask application factory** (`app/__init__.py`) invece di un unico `app.py` monolitico.
- **Auth completa**: registrazione, login, logout, con Flask-Login + Flask-WTF (CSRF incluso).
- **Un solo modello**: `User`. Chi si registra dalla landing è un cliente che usa il software — tutto lo storico dell'app va agganciato a lui (`user_id`), non esiste un concetto separato di "tenant/agenzia".
- **Dashboard protetta** minimale, ispirata nello stile a Shopify Polaris (non copiata: solo la stessa filosofia — superfici neutre, gerarchia chiara).
- **Flask-Admin** con vista su `User`, riservato al team (`User.is_admin`) — mai ai clienti normali.
- **Landing page** (quella che avevi già, in Tailwind/daisyUI) integrata con Jinja2 e collegata alle pagine di login/registrazione vere.
- **Postgres via Docker**, configurazione da variabili d'ambiente.
- **Struttura a blueprint**, pronta per aggiungerne altri senza toccare quello che c'è.

Tutto il resto (RBAC vero, billing, marketplace, Celery, API REST...) **non c'è ancora, di proposito**. Vedi l'ultima sezione per l'ordine in cui aggiungerlo.

---

## Struttura delle cartelle

```
config.py              # Configurazione letta da variabili d'ambiente
run.py                 # Entry point: crea l'app e la avvia

app/
  __init__.py           # Application factory: create_app()
  extensions.py          # Istanze condivise: db, login_manager, csrf, admin

  models/
    user.py               # User (login, password hash, is_admin)

  auth/
    forms.py               # LoginForm, RegisterForm (Flask-WTF)
    routes.py               # /auth/register, /auth/login, /auth/logout

  main/
    routes.py               # "/" -> landing page

  dashboard/
    routes.py               # "/dashboard/" (protetta da login)

  admin/
    views.py                # Viste Flask-Admin (UserAdminView)
    __init__.py              # init_admin(): le registra su /admin

  templates/
    base.html                # Guscio HTML condiviso da auth + dashboard (flash messages)
    auth/                     # login.html, register.html
    dashboard/                 # layout.html (sidebar+topbar), overview.html
    admin/base.html            # Tema custom sobrio per Flask-Admin
    landing/                   # index.html + partials/ (la landing che avevi già)

  static/
    css/                      # tokens.css + dashboard.css (dashboard/auth), landing.css/daisyui.css (landing)
    js/                        # landing.js
    img/landing/                # immagini della landing page
    shared/                     # logo.png + favicon.png, usati in landing/dashboard/auth/admin
```

**Perché un blueprint `dashboard` in più rispetto a quanto avevi abbozzato tu**: la dashboard protetta ha un layout e delle regole di accesso diverse dalla landing pubblica, quindi ha senso tenerla separata da `main`. Se preferisci accorpare, è una modifica piccola (sposta le rotte, aggiorna gli `url_for`).

---

## Come avviare in locale

### 1. Ambiente Python

```bash
python3 -m venv venv
source venv/bin/activate          # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. File `.env`

```bash
cp .env.example .env
```

Il valore di default in `.env.example` punta già al Postgres che avvii con Docker al passo successivo, quindi in locale di solito non devi cambiare nulla.

### 3. Postgres con Docker

```bash
docker compose up -d db
```

Questo avvia **solo** il database (consigliato per lo sviluppo quotidiano: modifichi il codice e riavvii `python run.py` all'istante, senza rebuild di immagini). Se invece vuoi tutto containerizzato:

```bash
docker compose up --build
```

(in questo caso Flask gira anche lui in un container, raggiungibile comunque su `http://localhost:3000`)

### 4. Avviare l'app

```bash
python run.py
```

La tabella `users` viene creata automaticamente all'avvio se non esiste già (`db.create_all()` dentro `create_app()`, vedi `_ensure_tables` in `app/__init__.py`) — non serve un passo manuale a parte. Se preferisci crearla esplicitamente (es. in uno script, senza avviare il server):

```bash
export FLASK_APP=run.py     # su Windows (PowerShell): $env:FLASK_APP = "run.py"
flask init-db
```

Va rilanciato solo se cambi database o lo svuoti da zero — non è una vera migration (vedi sezione dedicata più sotto).

Apri `http://localhost:3000`.

---

## Come registrare un utente ed entrare nella dashboard

1. Vai su `http://localhost:3000/auth/register` (oppure clicca "Sign up" nella landing).
2. Compila nome, email, password (minimo 8 caratteri). Al submit vieni loggato automaticamente e finisci su `/dashboard/`.
3. Per uscire: link "Logout" nella sidebar della dashboard, oppure `http://localhost:3000/auth/logout`.

Questo è il flusso dei tuoi **clienti**. `/admin/` (Flask-Admin) è un'altra cosa, per il team — vedi sotto.

---

## Come funziona Flask-Login in questo progetto

- `login_manager` (in `app/extensions.py`) è collegato all'app in `create_app()`.
- `User` eredita da `UserMixin` (`app/models/user.py`): questo gli dà gratis `is_authenticated`, `get_id()`, ecc.
- La funzione `load_user(user_id)` (dentro `app/__init__.py`, `_register_extensions`) dice a Flask-Login come recuperare uno `User` dal suo id, ad ogni richiesta.
- `login_user(user)` (in `app/auth/routes.py`) crea la sessione dopo login/registrazione riusciti.
- `@login_required` (import da `flask_login`) protegge una rotta: se non sei loggato, vieni rimandato a `login_manager.login_view` (`"auth.login"`), configurato in `_register_extensions`.
- Le password non sono mai salvate in chiaro: `User.set_password()` / `User.check_password()` usano `werkzeug.security` (hash + salt).

## Come funziona l'accesso a Flask-Admin (team vs clienti)

`/admin/` **non** è raggiungibile da un cliente normale, nemmeno se è loggato. `AdminAuthMixin` (in `app/extensions.py`) richiede `current_user.is_authenticated and current_user.is_admin` — e `is_admin` è `False` di default per chiunque si registri dalla landing. Il link "Flask-Admin" nella sidebar della dashboard compare solo se `current_user.is_admin` è vero; se un cliente prova comunque ad aprire `/admin/` a mano, viene rimandato al login (o, se è già loggato, alla propria dashboard — non vede mai nulla del pannello).

Per darti accesso la prima volta (o a un collega):

```bash
export FLASK_APP=run.py
flask make-admin tuaemail@esempio.it
```

L'utente deve essersi già registrato normalmente da `/auth/register`; il comando alza solo il flag `is_admin` sul suo record.

Questo **non è RBAC**: è un solo booleano, "fa parte del team" sì/no. Va bene finché il team è piccolo e fidato — vedi roadmap per quando introdurre ruoli veri.

---

## Dove mettere le cose nuove

| Voglio... | Vai in... |
|---|---|
| Un nuovo template | `app/templates/<area>/nome.html` (crea la cartella se serve) |
| Una nuova rotta in un blueprint esistente | `app/<blueprint>/routes.py` |
| Un nuovo modello | `app/models/nome.py` + aggiungilo a `app/models/__init__.py` |
| Un nuovo form | `app/<blueprint>/forms.py` (se non esiste, crealo sul modello di `app/auth/forms.py`) |
| Nuovo CSS/JS per la dashboard | `app/static/css/dashboard.css` (riusa le classi `lb-*` e i token in `tokens.css`) |
| Immagini della landing | `app/static/img/landing/` (`hero.jpg`, `feature-*.jpg`, `logo/*.svg`) |
| Logo o favicon | `app/static/shared/logo.png` e `favicon.png` — sostituisci i file, i template li usano già ovunque (landing, dashboard, auth, Flask-Admin) senza altre modifiche |

---

## Come aggiungere un nuovo blueprint

Esempio: vuoi un'area "Billing".

1. Crea la cartella `app/billing/` con `__init__.py` (vuoto) e `routes.py`:

   ```python
   from flask import Blueprint, render_template
   from flask_login import login_required

   billing_bp = Blueprint("billing", __name__, url_prefix="/billing")

   @billing_bp.route("/")
   @login_required
   def overview():
       return render_template("billing/overview.html")
   ```

2. Crea `app/templates/billing/overview.html` (estendi `dashboard/layout.html` se vuoi la stessa sidebar/topbar, oppure `base.html` se ti serve un layout diverso).

3. Registralo in `app/__init__.py`, dentro `_register_blueprints`:

   ```python
   from app.billing.routes import billing_bp
   app.register_blueprint(billing_bp)
   ```

4. Se ti serve un modello nuovo, seguilo lo stesso schema di `app/models/user.py` (mettilo in relazione a `User` con una `user_id`, non inventare un'altra entità "cliente" parallela). La tabella viene creata da sola al prossimo avvio (o subito con `flask init-db`).

Nient'altro va toccato: niente file di configurazione centrale da aggiornare oltre a questo.

---

## Database: perché `create_all()` e non le migration

Per restare semplici, la creazione delle tabelle usa `db.create_all()` — eseguito automaticamente ad ogni avvio dell'app (`_ensure_tables` in `app/__init__.py`), oppure a mano con `flask init-db` — non Flask-Migrate/Alembic. Va benissimo finché:

- sei l'unico sviluppatore,
- non hai ancora dati reali da preservare tra una modifica di schema e l'altra.

**Il giorno in cui cambi un modello esistente** (aggiungi/rimuovi una colonna) su un database che ha già dati che ti servono, `create_all()` non basta più: crea tabelle mancanti ma non altera quelle esistenti. A quel punto introduci Flask-Migrate — è un passo naturale, non un rifacimento (vedi roadmap sotto).

---

## Come continuare da solo senza AI

Questa è la parte più importante del documento. Leggila per intero prima di scrivere altro codice.

### Principi da rispettare

1. **`User` è il cliente. Punto.** Chi si registra dalla landing è l'unica entità "account" del sistema. Ogni nuova funzionalità che riguarda un cliente (ordini, progetti, preferenze, storico) si collega a lui con una `user_id` — non inventare un'entità intermedia "tenant/agenzia/workspace" a meno che il prodotto non cambi davvero forma (es. un cliente che deve gestire più sotto-account: a quel punto è una decisione di prodotto consapevole, non un default architetturale).
2. **Un blueprint, una responsabilità.** Se una nuova funzionalità non c'entra chiaramente con auth/main/dashboard/admin, è un nuovo blueprint — non infilarla in uno esistente "tanto è piccola".
3. **I modelli restano in `app/models/`, sempre.** Non definire classi `db.Model` altrove, nemmeno "temporaneamente".
4. **Ogni form con input utente passa da Flask-WTF.** Non scrivere validazione manuale di `request.form` a mano: è la fonte più comune di bug e buchi di sicurezza in Flask.
5. **Prima di aggiungere una libreria, chiediti se serve davvero ora.** Questo progetto è deliberatamente senza Celery, Redis, code, API REST separate, RBAC granulare, repository pattern. Se pensi di averne bisogno, probabilmente non è ancora il momento (vedi lista sotto).
6. **Il design system della dashboard vive in `tokens.css` + `dashboard.css`.** Nuovi componenti vanno aggiunti lì, con lo stesso prefisso `lb-` e le stesse variabili — non introdurre un secondo sistema di classi.
7. **La landing e la dashboard restano due mondi separati** (Tailwind/daisyUI da una parte, `lb-*` dall'altra). Non provare a farle condividere un `base.html`: sono stati scelti deliberatamente disaccoppiati.
8. **Ogni nuova pagina/vista che espone dati va pensata da subito "chi può vederla?"** — è il tipo di errore più facile da introdurre senza accorgersene (vedi il caso `is_admin` sopra: prima che esistesse, qualunque cliente loggato poteva aprire `/admin/` e vedere tutti gli altri utenti).

### Cosa NON aggiungere subito

Anche se ti verrà voglia, in quest'ordine di tentazione:
- RBAC granulare (ruoli, permessi per risorsa) — il flag `is_admin` basta finché il team è piccolo e fidato.
- API REST separata — se ti serve solo la dashboard server-rendered, non aggiungere un layer JSON parallelo "per sicurezza".
- Celery/task in background — introducilo solo quando hai un'operazione che *deve* girare fuori dalla request (invio email massivo, elaborazioni lunghe). Non prima.
- Un'entità "tenant/workspace" separata da `User` — solo se e quando un cliente deve davvero gestire più account/utenti sotto di sé.
- Un frontend JS separato (React/Vue) — finché Jinja2 + un po' di JS vanilla bastano, cambiare stack è puro costo.

### Roadmap pratica, in ordine

1. ~~Immagini vere nella landing~~, ~~logo/favicon ovunque~~, ~~registrazione minimale~~ — fatto.
2. **Ripulisci il testo placeholder della landing** (sezioni Features/Pricing/FAQ sono ancora quelle del template originale).
3. **Storico/dati del cliente**, agganciati a `User` via `user_id`, man mano che il prodotto lo richiede — segui il pattern della sezione "Come aggiungere un nuovo blueprint".
4. **Ruoli più fini di `is_admin`**, solo quando "team sì/no" non basta più (es. serve distinguere supporto da founder). Valuta prima un secondo campo semplice prima di una libreria RBAC.
5. **Billing**, come nuovo blueprint (`app/billing/`), quando hai davvero un piano da far pagare — non prima.
6. **Migration vere (Flask-Migrate)**, nel momento in cui hai dati reali da non perdere tra una modifica di schema e l'altra.
7. **Marketplace/funzionalità premium**, solo dopo che billing e ruoli esistono — dipendono da entrambi.

### Suggerimenti per non incasinare l'architettura

- Se un file supera le ~150-200 righe e fai fatica a scorrerlo, è probabile che stia facendo più di una cosa: dividilo (es. `routes.py` troppo lungo → estrai `services.py` con la logica, tieni le view sottili).
- Non importare `db` o modelli specifici dentro `app/extensions.py`: quel file deve restare senza dipendenze verso il resto dell'app, altrimenti rischi import circolari.
- Quando aggiungi un campo a `User`, aggiorna anche `form_columns`/`column_list` in `app/admin/views.py`, altrimenti resta invisibile lì.
- Tieni questo README aggiornato **tu**, quando cambi qualcosa di strutturale — è il documento che ti eviterà di dover rileggere tutto il codice tra sei mesi.
