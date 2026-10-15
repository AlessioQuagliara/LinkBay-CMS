# LinkBayCMS

LinkBayCMS legge i dati di Google Search Console e ti dice quali pagine del tuo sito stanno perdendo traffico organico in modo continuo, in ordine di priorità.

Il nome viene da un progetto precedente, un CMS. Oggi il codice in questo repository fa un'altra cosa: monitora le pagine in calo.

## Perché esiste

Una pagina che portava visite da Google comincia a perderne. Piano piano, senza far rumore. Te ne accorgi?

Search Console i dati li ha tutti, ma non ti avvisa. Devi confrontare periodi, filtrare pagina per pagina e capire da solo se il calo è reale o è stagionalità, un mese storto, un calo di tutto il sito.

Su poche pagine si fa. Su qualche centinaio, o su più siti, diventa un lavoro che nessuno fa con regolarità.

Il percorso che voglio è semplice: collego Search Console, scelgo i siti, e ogni settimana ricevo una lista corta di pagine da guardare, con il motivo per cui sono finite lì. Poi decido io cosa fare.

È pensato soprattutto per siti editoriali che vivono di traffico organico, e per chi ci lavora sopra: un SEO interno, chi gestisce i contenuti, un'agenzia che segue più siti.

## Cosa permette di fare oggi

- Registrarsi e accedere con email e password, con un codice di verifica via email (OTP) e il recupero password.
- Collegare il proprio account Google Search Console in sola lettura e scegliere quali proprietà monitorare, nei limiti del piano.
- Consultare una vista Insights per sito: clic, impressioni, CTR, posizione, pagine e query, con il confronto con il periodo precedente.
- Vedere la lista delle pagine in calo, ordinata per priorità, con il trend della singola pagina e le query che hanno perso di più. Ogni pagina si può segnare come gestita; dopo 30 e 60 giorni un controllo verifica se il traffico è tornato.
- Esportare la lista in CSV o PDF, con l'opzione di togliere il marchio LinkBayCMS sui piani che lo prevedono.
- Ricevere un'email settimanale con le pagine principali in calo (disattivabile dalle impostazioni).
- Usare l'interfaccia in italiano o in inglese.

Ci sono poi alcune funzioni opzionali, che si attivano solo se configuri un fornitore AI (DeepSeek):

- un'analisi delle pagine monitorate, con un punteggio e qualche suggerimento per pagina;
- una "audit presentation", cioè una presentazione a slide costruita sugli alert già calcolati, senza inventare numeri;
- una piccola chat sulla landing che risponde a domande su piani e funzionalità.

## Come funziona

1. Ti registri e confermi il codice ricevuto via email. Parte un periodo di prova.
2. Colleghi Search Console con OAuth. I token restano nel database cifrati.
3. Scegli i siti da monitorare tra quelli verificati nel tuo account Google.
4. L'app salva lo storico giornaliero del sito e quello mensile per pagina. Gli aggiornamenti richiesti dalla dashboard vanno in una coda e li esegue un processo separato, così la pagina non resta bloccata.
5. Ogni settimana un job applica le regole a ogni pagina. Una pagina diventa un alert solo se supera tutti i filtri:
   - aveva un traffico minimo nel suo mese migliore;
   - ha perso almeno una certa percentuale e un certo numero di clic, confrontando gli ultimi mesi con quelli precedenti;
   - il calo dura da almeno due mesi;
   - non si spiega con la stagionalità;
   - è peggiore dell'andamento generale del sito.
6. Le pagine che passano ricevono un punteggio (gravità, valore, possibilità di recupero) e una spiegazione in chiaro. Le trovi nella dashboard, negli export e nell'email del lunedì.

Le soglie predefinite sono in `app/rules/types.py`. Sono un punto di partenza, non verità assolute.

## Scelte tecniche

- Flask con blueprint e template Jinja2 renderizzati lato server. Niente frontend separato: le pagine sono poche e così resta tutto in un'unica app.
- PostgreSQL con SQLAlchemy. Le tabelle si creano all'avvio con `create_all()`, senza un sistema di migration.
- Redis con RQ per i lavori in background (aggiornamento dati e analisi AI), con code a priorità diverse in base al piano. Redis serve anche per il rate limiting.
- Cron dentro un container (supercronic) per i job ricorrenti: storico, regole, email settimanale, controllo recupero, crediti AI. Gli orari sono in `crontab`.
- Tailwind e daisyUI da CDN, senza build step. Flask-Admin, riservato agli amministratori, usa un suo tema separato.
- Servizi esterni: Google Search Console API, Resend per le email, DeepSeek per l'AI, Cloudflare Turnstile come captcha, Paddle per i pagamenti, WeasyPrint per i PDF.

## Avvio in locale

Ti servono Python 3.12 e Docker. WeasyPrint, usato per gli export PDF, richiede alcune librerie di sistema (Pango, Cairo): il `Dockerfile` mostra quali.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

In `.env` imposta almeno:

- `SECRET_KEY`: senza un valore proprio l'app non parte;
- `TOKEN_ENCRYPTION_KEY`: chiave Fernet per cifrare i token Google, il comando per generarla è in `.env.example`;
- `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET`: credenziali OAuth di tipo "Web application" create in Google Cloud Console, con l'API Search Console abilitata e `{APP_BASE_URL}/gsc/callback` tra i redirect URI autorizzati.

Senza le credenziali Google l'app si avvia, ma non puoi collegare Search Console.

Poi avvia database e Redis, e l'app:

```bash
docker compose up -d db redis
python run.py
```

L'app risponde su `http://localhost:3000`. In alternativa `docker compose up --build` avvia tutto in container: app, worker, cron, database e Redis.

Se avvii solo l'app con `python run.py`, gli aggiornamenti in coda restano lì finché non gira un worker. Per smaltirli una volta:

```bash
docker compose run --rm worker rq worker --burst high default low
```

Integrazioni opzionali, tutte descritte in `.env.example`:

- `RESEND_API` e `RESEND_FROM`: invio delle email. In modalità debug, senza Resend, il codice OTP compare a schermo.
- `DEEPSEEK_API`: funzioni AI. Se manca, rispondono "non configurata".
- `TURNSTILE_SITE_KEY` e `TURNSTILE_SECRET_KEY`: captcha sulla registrazione. Se mancano, il controllo viene saltato.
- Variabili `PADDLE_*`: abbonamenti e crediti AI. I dettagli sono in [docs/paddle-billing.md](docs/paddle-billing.md).

Qualche comando utile (con il venv attivo):

```bash
python -m flask --app run.py make-admin <email-utente-registrato>
python -m flask --app run.py seed-demo-account --email <indirizzo-di-test>
python -m flask --app run.py run-decay-rules
```

Il primo dà accesso a `/admin/` a un utente già registrato. Il secondo crea un account demo con dati Search Console sintetici, utile per provare la dashboard senza collegare Google. Il terzo esegue a mano le regole settimanali.

I test usano SQLite in memoria e non richiedono Postgres:

```bash
pip install -r requirements-dev.txt
pytest
```

## Stato e limiti

Il flusso principale funziona: registrazione, collegamento a Search Console, selezione dei siti, storico, regole, lista delle pagine in calo, export ed email settimanale.

Alcune cose sono ancora da sistemare:

- non ci sono migration: modificare un modello su un database con dati richiede interventi manuali;
- la dashboard non mostra ancora quando un aggiornamento è in corso in background;
- le soglie delle regole sono uguali per tutti i siti e non si possono modificare dall'interfaccia;
- nel codice e nel database restano campi legati a canali di pagamento dismessi (Revolut, Lemon Squeezy), mantenuti solo per gli utenti che li avevano già;
- `ARCHITECTURE.md` e `BUSINESS_PLAN.md` descrivono il progetto e le scelte iniziali, ma non sono aggiornati in ogni dettaglio: dove non coincidono, fa fede il codice.

## Licenza

Il file `LICENSE` non contiene una licenza open source, ma un contratto di licenza del marchio LinkBayCMS. Il codice è consultabile, ma nessuna licenza ne autorizza il riuso, la modifica o la redistribuzione: se ti interessa usarlo, chiedimelo prima.
