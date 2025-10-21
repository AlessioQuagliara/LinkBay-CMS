# LinkBay CMS - Management Frontend

Gestionale per le agenzie - Pannello di controllo per gestire clienti, siti web e fatturazione.

## 🚀 Avvio Rapido

```bash
# Installa dipendenze
npm install

# Avvia in modalità sviluppo
npm run dev

# Build per produzione
npm run build
```

## 📁 Struttura

```
management/
├── src/
│   ├── components/     # Componenti riutilizzabili
│   ├── pages/          # Pagine dell'applicazione
│   │   ├── auth/       # Login e registrazione
│   │   ├── dashboard/  # Dashboard principale
│   │   ├── clients/    # Gestione clienti
│   │   ├── websites/   # Gestione siti web
│   │   └── billing/    # Fatturazione
│   ├── hooks/          # Custom hooks
│   ├── utils/          # Utility functions
│   └── types/          # TypeScript types
├── public/             # Asset statici
├── nginx.conf          # Configurazione reverse proxy
└── package.json
```

## 🔧 Tecnologie

- **React 18** - UI Library
- **TypeScript** - Type safety
- **React Router** - Routing
- **Tailwind CSS** - Styling
- **Vite** - Build tool

## 🌐 Pagine Disponibili

- `/login` - Accesso agenzia
- `/register` - Registrazione nuova agenzia
- `/` - Dashboard (richiede autenticazione)
- `/clients` - Gestione clienti
- `/websites` - Gestione siti web
- `/billing` - Fatturazione

## 🔌 API Integration

Il frontend si collega al backend LinkBay CMS tramite endpoint REST:

- `GET /api/clients` - Lista clienti
- `POST /api/clients` - Nuovo cliente
- `GET /api/websites` - Lista siti web
- `POST /api/websites` - Nuovo sito web
- `GET /api/billing` - Fatture e pagamenti

## 📦 Deployment

Usa il file `nginx.conf` per configurare il reverse proxy in produzione.

## 🤝 Contributi

Progetto mantenuto da **Alessio Quagliara** - LinkBay CMS