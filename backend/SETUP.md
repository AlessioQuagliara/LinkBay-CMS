# 🚀 Guida Rapida - Backend Setup

## Setup Iniziale (Prima Volta)

### 1. Installa PostgreSQL

```bash
# macOS con Homebrew
brew install postgresql@16
brew services start postgresql@16

# Oppure usa Docker
docker run --name linkbay-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:16
```

### 2. Crea Database

```bash
# Accedi a PostgreSQL
psql postgres

# Crea database e utente
CREATE DATABASE linkbaycms;
CREATE USER alessio WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE linkbaycms TO alessio;
\q
```

### 3. Configura Environment

```bash
# Copia .env.example
cp .env.example .env

# Modifica DATABASE_URL nel file .env
DATABASE_URL="postgresql://alessio:password@localhost:5432/linkbaycms?schema=public"
```

### 4. Migra Database

```bash
# Genera Prisma Client
npm run prisma:generate

# Crea tabelle nel database
npm run prisma:migrate

# (Opzionale) Popola con dati demo
npm run db:seed
```

### 5. Avvia Server

```bash
# Development con hot reload
npm run dev

# Server partirà su http://localhost:3000
```

## Test API

### Registrazione

```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### Login

```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get Profile (con token)

```bash
curl http://localhost:3000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Comandi Utili

```bash
# Database
npm run prisma:studio      # Apre UI per visualizzare database
npm run prisma:migrate     # Crea nuova migration
npm run prisma:push        # Push schema senza migration

# Development
npm run dev                # Hot reload development
npm run build              # Build TypeScript
npm start                  # Start production

# Seed
npm run db:seed            # Popola database con dati demo
```

## Credenziali Demo (dopo seed)

```
Admin:  admin@linkbaycms.com / admin123
Agency: demo@agency.com / demo123
```

## Struttura Progetto

```
src/
├── config/         # Database e JWT config
├── controllers/    # HTTP request handlers
├── middlewares/    # Express middlewares
├── routes/         # API routes
├── services/       # Business logic
├── types/          # TypeScript types
├── validators/     # Zod schemas
└── server.ts       # Entry point
```

## Troubleshooting

### Database connection error

```bash
# Verifica che PostgreSQL sia in esecuzione
brew services list  # macOS
docker ps           # Docker

# Testa connessione
psql postgresql://alessio:password@localhost:5432/linkbaycms
```

### Port già in uso

```bash
# Cambia porta nel .env
PORT=3001
```

### Prisma errors

```bash
# Rigenera Prisma Client
npm run prisma:generate

# Reset database (cancella tutti i dati!)
npx prisma migrate reset
```
