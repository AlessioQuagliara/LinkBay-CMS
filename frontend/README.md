# frontend — marketing site + storefront (definitivo)

Questa è l'unica codebase frontend da portare avanti. Contiene sia il sito
marketing (`/`, `/pricing`, `/features`, `/blog`, ...) sia la storefront
multi-tenant, servite dalla stessa app Next.js tramite rewrite di
`middleware.ts`.

> Se stai cercando "la storefront giusta": è questa. Le altre due varianti che
> esistevano nel repo (una app standalone Next.js a `storefront/` in root) sono
> state consolidate/archiviate — vedi
> [Perché questa e non le altre](#perché-questa-e-non-le-altre).

## Architettura

```
frontend/
├── middleware.ts              # risolve il tenant dall'host e fa il rewrite
├── app/
│   ├── (marketing pages)      # /, /pricing, /features, /blog, /docs, ...
│   └── storefront/            # route storefront (servite via rewrite, vedi sotto)
│       ├── page.tsx                       home tenant
│       ├── shop/, shop/[category]/        catalogo
│       ├── collections/[slug]/            collezioni
│       ├── products/[slug]/               PDP
│       ├── search/                        ricerca
│       ├── checkout/, checkout/success/   checkout (Stripe Elements, step interni)
│       └── account/                       area cliente (login, ordini, profilo)
└── storefront/                # libreria condivisa dalle route storefront sopra
    ├── components/             blocks (BlockRenderer/HeroBlock/...), layout, prodotti, filtri
    └── lib/
        ├── api/                client fetch verso il backend Laravel (/api/store/*, /api/account/*)
        ├── store/              zustand: cartStore, brandStore, authStore
        ├── types/              tipi condivisi (Product, Cart, Order, Brand, Customer)
        └── utils/               tenant.ts (subdomain→slug), brand-css.ts (CSS vars), currency.ts
```

`app/storefront/*` e `storefront/*` non sono due codebase diverse: sono la
stessa implementazione, divisa secondo la convenzione Next.js App Router (pagine
in `app/`, libreria condivisa fuori da `app/` per restare fuori dal routing).
Le pagine importano la libreria con l'alias `@/storefront/*` (vedi
`tsconfig.json`, `paths: { "@/*": ["./*"] }`).

## Come si avvia

```bash
cd frontend
npm install
cp .env.local.example .env.local   # poi valorizza le variabili, vedi sotto
npm run dev
```

Build/lint/type-check (gli stessi passi eseguiti in CI):

```bash
npm run lint
npx tsc --noEmit
npm run build
```

Con Docker: il servizio `frontend` in `compose.yaml` builda questa cartella e
la espone su Traefik per `linkbay-cms.com` / `www.linkbay-cms.com`.

## Routing tenant

`middleware.ts` decide, per ogni richiesta, se è marketing site o storefront
di un tenant:

1. Estrae l'host dalla richiesta.
2. Se l'host è in `CUSTOM_DOMAIN_MAP` → risolve lo slug del tenant da lì.
3. Altrimenti, se l'host è `NEXT_PUBLIC_MAIN_DOMAIN` (o `www.`) → è il sito
   marketing; richieste dirette a `/storefront/*` vengono bloccate (redirect a `/`).
4. Altrimenti, se l'host è un subdomain di `NEXT_PUBLIC_MAIN_DOMAIN`
   (`{slug}.linkbay-cms.com`) → quello slug è il tenant.
5. Per le richieste tenant: aggiunge l'header `x-tenant-slug` e fa un
   **rewrite** (non redirect) verso `/storefront/*`, così l'URL pubblico resta
   pulito (`{slug}.linkbay-cms.com/shop`, non
   `{slug}.linkbay-cms.com/storefront/shop`).

Lato libreria, `storefront/lib/utils/tenant.ts` replica la stessa estrazione
slug per uso client-side, e le chiamate API (`storefront/lib/api/*`) usano
`NEXT_PUBLIC_API_BASE_URL` con placeholder `{slug}` per costruire l'host del
tenant — il backend Laravel usa tenancy domain-based (stancl/tenancy): ogni
tenant ha il proprio dominio registrato via
`TenantProvisioningService::registerDomain`, e le rotte tenant (`routes/tenant.php`)
sono protette da `PreventAccessFromCentralDomains`, quindi un dominio
centrale/condiviso nell'URL API **non funziona** per queste chiamate.

**Rischio noto / da verificare prima della demo pubblica:** in `compose.yaml` e
`docker/nginx/default.conf`, i subdomain wildcard (`*.linkbay-cms.com`) sono
instradati da Traefik a `nginx-svc` → `php-fpm` (Laravel), mentre solo l'host
esatto `linkbay-cms.com`/`www.` è instradato al container `frontend`
(Next.js). Questo è corretto per le chiamate `api/v1/*` e `api/store/*` (che
devono arrivare a Laravel per la risoluzione tenant-by-domain), ma va
verificato end-to-end che la *pagina* storefront su un vero subdomain tenant
pubblico arrivi effettivamente al container `frontend` e non resti intrappolata
in Laravel (che non ha viste storefront proprie, solo API + redirect
`app.frontend_url` per la root `/`). In locale/staging su host fissi
(`app.linkbay-cms.test`) il problema non si presenta perché non si passa da un
vero subdomain wildcard.

## Integrazione API

Le chiamate storefront colpiscono il backend Laravel reale
(`backend/routes/tenant.php`, prefisso `api/store/*` per il catalogo pubblico e
`api/account/*` per l'area cliente autenticata). Non ci sono mock:
`storefront/lib/api/*` fa `fetch` diretti con `NEXT_PUBLIC_API_BASE_URL`.

## Variabili d'ambiente

Vedi `frontend/.env.example` per l'elenco completo con commenti (include
`NEXT_PUBLIC_API_BASE_URL` con placeholder `{slug}`, `NEXT_PUBLIC_MAIN_DOMAIN`,
`CUSTOM_DOMAIN_MAP`, le URL Agency, `NEXT_PUBLIC_SITE_URL`,
`NEXT_PUBLIC_STRIPE_KEY`). `.env.local.example` contiene gli equivalenti per
sviluppo locale via Traefik (`*.linkbay-cms.test`).

## CI

`.github/workflows/ci.yml` builda/lint/type-checka **solo** questa cartella
(filtro `frontend/**`). Nessun'altra codebase storefront è coperta da CI — non
lo era già prima di questo consolidamento, perché l'altra variante non è mai
stata la base attiva (vedi sotto).

## Perché questa e non le altre

Al momento del consolidamento (2026-07-08) esisteva anche una terza variante
storefront, standalone Next.js app in root (`storefront/`), sviluppata in
parallelo:

| | `frontend/` (questa) | `storefront/` (root, ora archiviata) |
|---|---|---|
| Routing multi-tenant | ✅ `middleware.ts` risolve subdomain/custom domain | ❌ `middleware.ts` fa solo auth-guard su `/account` |
| Catalogo (shop/categorie/PDP/ricerca) | ✅ completo | ❌ assente, home è uno stub statico |
| Checkout | ✅ singola pagina, step interni, Stripe Elements | ✅ route separate (address/shipping/payment/confirmation) — più granulare ma mai collegata a un carrello/catalogo reale |
| Area account | ✅ login, ordini, profilo | ✅ anche register, forgot/reset password, verify-email, wishlist, indirizzi — più completa |
| Branding/temi | ✅ CSS vars applicate da fetch reale (`brand-css.ts`) | ⚠️ store zustand presente ma senza fetch/applicazione |
| Build/CI/deploy | ✅ in CI, in `compose.yaml`, `next build`/`tsc` puliti oggi | ❌ mai `npm install`-ata, non in CI, non in `compose.yaml` |

`storefront/` (root) è stata archiviata in
`_archive/storefront-standalone-legacy/` (non cancellata: i suoi flussi di
account self-service e checkout multi-step sono più maturi e vale la pena
riprenderli — vedi `ARCHIVED.md` lì dentro).

## TODO non bloccanti per la demo

- [x] ~~Verificare end-to-end il routing Traefik/nginx dei subdomain wildcard
      verso il container `frontend`~~ — risolto: `compose.yaml` e
      `compose.override.local.yml` ora instradano esplicitamente
      app./admin./api.CENTRAL_DOMAIN a Laravel (priorità alta) e qualsiasi
      altro subdomain di CENTRAL_DOMAIN al container `frontend` (priorità
      bassa). Richiede comunque `NEXT_PUBLIC_MAIN_DOMAIN` impostato in
      `.env.local` — vedi `.env.local.example`. Non ancora verificato con uno
      stack Docker realmente avviato (nessun daemon Docker disponibile nella
      sessione in cui è stato scritto questo fix) — verificalo con
      `docker compose up` prima di una demo su subdomain pubblico reale.
- [ ] Portare da `_archive/storefront-standalone-legacy/` le pagine account
      ancora mancanti: `forgot-password`, `reset-password`, `verify-email`,
      `wishlist` (UI — le funzioni API esistono già in `lib/api/account.ts`
      ma non sono richiamate da nessun componente). `register` e `addresses`
      sono già implementate qui (tab dentro `/account/login`, sezione dentro
      `/account/profile`) — non serve portarle dall'archivio.
- [ ] Valutare se separare il checkout in route distinte
      (address/shipping/payment/confirmation) prendendo spunto dallo stesso
      archivio, o se restare con l'attuale pagina a step interni.
- [ ] `ValidationError`/`MaintenanceError` (`lib/api/client.ts`) sono definite
      ma nessun call site le usa — ogni form (login, register, checkout,
      profilo) mostra un messaggio di errore generico fisso invece degli
      errori di validazione reali del backend (422) o di un avviso di
      manutenzione (503).
