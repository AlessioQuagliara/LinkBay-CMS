Server folder (TypeScript)

Contiene il server Express minimale, controller e middleware di esempio.

- `app.ts` - entry point Express (exporta `app` per i test e avvia il server se eseguito direttamente)
- `controllers/` - controllers esempio
- `middleware/` - middleware esempio (tenant resolver)
- `migrations/` - cartella per migrazioni Knex

Prossimi passi:
- spostare i controller esistenti da `src/` a `server/controllers/`
- adattare imports ed eseguire build/test
