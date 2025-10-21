# LinkBay CMS - Backend API

Backend API scalabile e modulare per LinkBay CMS, costruito seguendo i principi **SOLID**, **DRY** e **KISS**.

## 🏗️ Architettura

```
backend/
├── prisma/
│   └── schema.prisma          # Schema database PostgreSQL
├── src/
│   ├── config/                # Configurazioni (database, JWT)
│   │   ├── database.ts
│   │   └── jwt.ts
│   ├── controllers/           # Request handlers
│   │   ├── auth.controller.ts
│   │   └── user.controller.ts
│   ├── middlewares/           # Middleware Express
│   │   ├── auth.middleware.ts
│   │   ├── error.middleware.ts
│   │   └── validate.middleware.ts
│   ├── routes/                # Definizione routes
│   │   ├── auth.routes.ts
│   │   ├── user.routes.ts
│   │   └── index.ts
│   ├── services/              # Business logic
│   │   ├── auth.service.ts
│   │   └── user.service.ts
│   ├── types/                 # TypeScript types
│   │   └── index.ts
│   ├── validators/            # Zod schemas
│   │   └── schemas.ts
│   └── server.ts              # Entry point
├── .env.example
├── package.json
└── tsconfig.json
```

## 🛠️ Stack Tecnologico

- **Runtime**: Node.js + TypeScript
- **Framework**: Express.js
- **Database**: PostgreSQL + Prisma ORM
- **Autenticazione**: JWT + bcrypt
- **Validazione**: Zod
- **CORS**: cors middleware

## 🚀 Quick Start

### 1. Installazione dipendenze

```bash
npm install
```

### 2. Setup database

Copia `.env.example` in `.env` e configura:

```env
DATABASE_URL="postgresql://user:password@localhost:5432/linkbaycms"
JWT_SECRET="your-secret-key"
```

### 3. Genera Prisma Client e migra database

```bash
npm run prisma:generate
npm run prisma:migrate
```

### 4. Avvia server

```bash
# Development con hot reload
npm run dev

# Production build
npm run build
npm start
```

## 📡 API Endpoints

### Autenticazione

- `POST /api/v1/auth/register` - Registrazione utente
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Utenti (protetti)

- `GET /api/v1/users/me` - Profilo corrente
- `PUT /api/v1/users/me` - Aggiorna profilo
- `GET /api/v1/users` - Lista utenti (admin)
- `GET /api/v1/users/:id` - Dettaglio utente (admin)

### Health Check

- `GET /api/v1/health` - Status server

## 🎨 Principi di Design

### SOLID

- **Single Responsibility**: Ogni classe/modulo ha una sola responsabilità
- **Open/Closed**: Estensibile senza modificare codice esistente
- **Liskov Substitution**: Service implementano contratti chiari
- **Interface Segregation**: Interfacce piccole e specifiche
- **Dependency Inversion**: Dipendenze attraverso astrazioni

### DRY (Don't Repeat Yourself)

- Service layer condiviso
- Middleware riutilizzabili
- Validazione centralizzata con Zod
- Gestione errori unificata

### KISS (Keep It Simple, Stupid)

- Struttura cartelle intuitiva
- Naming chiaro e consistente
- Logica business separata da HTTP
- Commenti esplicativi dove necessario

## 📦 Database Schema

```prisma
User
├── id
├── email
├── password (hashed)
├── name
├── role (AGENCY | ADMIN)
└── agencies[]

Agency
├── id
├── name
├── description
├── userId
├── websites[]
└── customers[]

Website
├── id
├── name
├── domain
├── status
├── agencyId
└── customerId

Customer
├── id
├── name
├── email
├── agencyId
└── websites[]
```

## 🔐 Sicurezza

- Password hashingate con bcrypt (10 rounds)
- JWT con refresh token rotation
- Validazione input con Zod
- CORS configurabile
- Error sanitization in production

## 📝 Scripts

```bash
npm run dev              # Dev server con hot reload
npm run build            # Build TypeScript
npm start                # Start production server
npm run prisma:generate  # Genera Prisma Client
npm run prisma:migrate   # Migra database
npm run prisma:studio    # UI database
npm run prisma:push      # Push schema (no migration)
```

## 🌍 Environment Variables

```env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d
JWT_REFRESH_EXPIRES_IN=30d
CORS_ORIGIN=http://localhost:3001,http://localhost:3002
```

## 🤝 Contribuire

1. Mantieni la struttura modulare
2. Segui principi SOLID, DRY, KISS
3. Aggiungi validazione Zod per nuove routes
4. Documenta le API endpoints
5. Testa con Prisma Studio

## 📄 License

CUSTOM
