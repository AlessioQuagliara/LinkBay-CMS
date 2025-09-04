# Database

Se il progetto usa un database relazionale, le migrazioni e il codice di accesso sono organizzati sotto `server/migrations` e nello strato modello/controller.

Per inizializzare il DB (esempio con Knex + PostgreSQL):

1. Configura `.env` con connection string
2. Esegui le migrazioni

   npx knex migrate:latest

Se non hai bisogno di un DB per demo locali, puoi usare un mock o SQLite in memoria per i test E2E.
