# Architettura e struttura del progetto

Cartelle principali:

- `server/` — codice TypeScript per il server Express, controller, middleware, e routing.
- `views/` — template EJS per le pagine front-end.
- `public/` — asset statici (CSS compilato, immagini, js cliente).
- `docs/` — documentazione e indice generato `documentation_index.json`.

Dettagli sull'integrazione: il server usa `express-ejs-layouts` e serve `public/` e `docs/` come static.
