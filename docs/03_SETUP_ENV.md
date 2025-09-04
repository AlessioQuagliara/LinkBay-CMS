# Setup e ambiente di sviluppo

I passi tipici per avviare il progetto in locale:

1. Installa dipendenze

   npm install

2. Compila gli asset CSS (se necessario)

   npm run build:css

3. Avvia il server in sviluppo

   npm run dev

Note su variabili d'ambiente: il progetto può usare `.env` o un sistemi di secrets. Controllare `server/README.md` per dettagli sul DB e le migrazioni.
