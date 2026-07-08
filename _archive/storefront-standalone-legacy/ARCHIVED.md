# Archiviato — 2026-07-08

Questo era un terzo tentativo di storefront, standalone Next.js app con proprio
`package.json`/`middleware.ts`, sviluppato in parallelo a `frontend/app/storefront`
+ `frontend/storefront`.

## Perché è stato archiviato

La storefront definitiva è **`frontend/`** (vedi `frontend/README.md`). Questa
codebase non è mai stata la base attiva:

- non ha logica di risoluzione tenant (il suo `middleware.ts` fa solo auth-guard
  su `/account`, non risolve subdomain/custom domain come
  `frontend/middleware.ts`)
- non ha nessuna pagina di catalogo (niente shop, categorie, PDP, ricerca) — la
  home è uno stub statico ("Benvenuto")
- non è mai stata installata (nessun `node_modules`), non è nella CI
  (`.github/workflows/ci.yml` filtra solo `frontend/**`) e non è nel
  `compose.yaml`/Traefik: non è mai stata deployata da nessuna parte

## Cosa vale la pena recuperare da qui

Ha alcuni flussi più maturi di quelli in `frontend/app/storefront`, utili come
riferimento quando si implementano i TODO elencati in `frontend/README.md`:

- `app/(store)/account/register`, `forgot-password`, `reset-password`,
  `verify-email`, `wishlist`, `addresses` — pagine che oggi non esistono nella
  storefront definitiva
- `app/(store)/checkout/shipping`, `checkout/payment`,
  `checkout/confirmation/[orderId]` — checkout diviso in route separate,
  invece dell'unica pagina a step interni di `frontend/app/storefront/checkout`
- `lib/api/client.ts` — un client `accountApi`/`storeApi` più completo
  (password reset, wishlist, indirizzi) da confrontare con
  `frontend/storefront/lib/api/*`

Non reintrodurre questa cartella nella build: è tenuta solo come reference,
non è coperta da CI e non compila contro le env vars attuali.
