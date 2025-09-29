# 🐳 LinkBay CMS Docker Configuration

Configurazione Docker completa per LinkBay CMS con supporto multi-ambiente (sviluppo e produzione).

## 🏗️ Architettura Docker

### Sviluppo (docker-compose.dev.yml)
```
┌─────────────────────────────────────────┐
│               Development               │
├─────────────────────────────────────────┤
│ PostgreSQL    │ Port 5432               │
│ Redis         │ Port 6379               │
│ Backend       │ Port 3000 (Node.js)    │
│ Landing       │ Port 3001 (Vite)       │
│ Agency        │ Port 3002 (Vite)       │
│ Customer      │ Port 3003 (Vite)       │
│ Websites      │ Port 3004 (Vite)       │
└─────────────────────────────────────────┘
```

### Produzione (docker-compose.prod.yml)
```
┌─────────────────────────────────────────┐
│              Production                 │
├─────────────────────────────────────────┤
│ Nginx         │ Port 80/443 (SSL)      │
│ Backend       │ Internal (Node.js)      │
│ Frontend Apps │ Internal (Static)       │
│ PostgreSQL    │ Internal Only           │
│ Redis         │ Internal Only           │
│ Watchtower    │ Auto-updates            │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Iniziale
```bash
# Rendi eseguibile lo script
chmod +x docker.sh

# Setup iniziale (crea directories, copia file)
./docker.sh setup
```

### 2. Ambiente Sviluppo
```bash
# Avvia tutti i servizi
./docker.sh dev:up

# Controlla status
./docker.sh status

# Visualizza logs
./docker.sh dev:logs

# Arresta tutto
./docker.sh dev:down
```

### 3. Ambiente Produzione
```bash
# Build immagini produzione
./docker.sh prod:build

# Avvia produzione
./docker.sh prod:up

# Controlla health
./docker.sh health
```

## 📋 Comandi Disponibili

### 🔧 Sviluppo
- `./docker.sh dev:up` - Avvia ambiente sviluppo
- `./docker.sh dev:down` - Ferma ambiente sviluppo
- `./docker.sh dev:restart` - Riavvia servizi
- `./docker.sh dev:logs` - Mostra logs
- `./docker.sh dev:build` - Ricostruisci immagini

### 🏭 Produzione
- `./docker.sh prod:up` - Avvia produzione
- `./docker.sh prod:down` - Ferma produzione
- `./docker.sh prod:restart` - Riavvia produzione
- `./docker.sh prod:logs` - Logs produzione
- `./docker.sh prod:build` - Build produzione

### 🛠️ Utility
- `./docker.sh setup` - Setup iniziale
- `./docker.sh status` - Status container
- `./docker.sh health` - Health check
- `./docker.sh cleanup` - Pulizia Docker

### 🗄️ Database
- `./docker.sh db:migrate` - Esegui migrazioni
- `./docker.sh db:seed` - Popola database
- `./docker.sh db:reset` - Reset database

## 🌐 URLs Ambiente Sviluppo

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| Landing | http://localhost:3001 | Homepage principale |
| Agency | http://localhost:3002 | Dashboard agenzia |
| Customer | http://localhost:3003 | Portale clienti |
| Websites | http://localhost:3004 | Website builder |
| Backend API | http://localhost:3000 | API REST |
| Database | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | Cache |

## 🌍 URLs Ambiente Produzione

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| Landing | https://linkbay-cms.com | Homepage principale |
| Agency | https://app.linkbay-cms.com | Dashboard agenzia |
| Customer | https://manage.linkbay-cms.com | Portale clienti |
| Websites | https://sites.linkbay-cms.com | Website builder |

## 🔧 Configurazione

### File Principali
- `.env.docker` - Variabili ambiente Docker
- `docker-compose.dev.yml` - Configurazione sviluppo
- `docker-compose.prod.yml` - Configurazione produzione
- `docker.sh` - Script gestione
- `nginx/` - Configurazioni Nginx produzione

### Variabili Ambiente
Le variabili sono configurate in `.env.docker` basato sul tuo `.env`:

```env
# Database
DATABASE_URL=postgres://root:root@postgres:5432/linkbaycms
DB_HOST=postgres

# Redis
REDIS_URL=redis://redis:6379

# Porte
PORT_BACKEND=3000
PORT_LANDING=3001
PORT_AGENCY=3002
PORT_CUSTOMER=3003
PORT_WEBSITE=3004

# OAuth (configurato)
GOOGLE_CLIENT_ID=723887697815-k8nn0buqt24m24qmp036rv7oo928gph4.apps.googleusercontent.com
GITHUB_CLIENT_ID=Ov23lifj3WlS1oCtw4xE

# SMTP (configurato)
SMTP_HOST=smtps.aruba.it
SMTP_USER=piattaforma@spotexsrl.com
```

## 🛡️ Security Features

### Sviluppo
- Container non-root users
- Health checks per tutti i servizi
- Network isolation
- Volume mount per hot reload

### Produzione
- SSL/TLS termination con Nginx
- Rate limiting per API
- Security headers
- Database interno (no external ports)
- Auto-updates con Watchtower
- Multi-stage builds per immagini ottimizzate

## 📊 Monitoring & Health

### Health Checks
Ogni servizio ha health checks configurati:
- **Backend**: HTTP check su `/api/health`
- **Frontend**: HTTP check su root path
- **Database**: `pg_isready` command
- **Redis**: `redis-cli ping`

### Logs
```bash
# Logs di tutti i servizi
./docker.sh dev:logs

# Logs specifico servizio
docker-compose -f docker-compose.dev.yml logs -f backend

# Logs produzione
./docker.sh prod:logs
```

## 🔄 Hot Reload

In sviluppo tutti i servizi supportano hot reload:
- **Backend**: Nodemon per restart automatico
- **Frontend**: Vite HMR per aggiornamenti istantanei
- **File mounting**: Codice locale sincronizzato con container

## 📦 Build Ottimizzati

### Multi-stage Builds
- **Frontend Prod**: Node build → Nginx static serving
- **Backend Prod**: Deps → Build → Runtime
- **Layer caching**: Dipendenze separate per build veloci

### Image Sizes
- **Development**: ~400MB per servizio
- **Production**: ~50MB frontend, ~200MB backend

## 🚨 Troubleshooting

### Problemi Comuni

**Container non si avvia:**
```bash
./docker.sh status
./docker.sh dev:logs
```

**Database connection error:**
```bash
docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U root
```

**Port already in use:**
```bash
sudo lsof -ti:3000
docker-compose -f docker-compose.dev.yml down
```

**Build fallisce:**
```bash
./docker.sh cleanup
./docker.sh dev:build
```

## 🔄 Deployment

### Production Setup
1. **SSL Certificates**: Posiziona in `nginx/ssl/`
2. **Environment**: Configura `.env.docker`
3. **Build**: `./docker.sh prod:build`
4. **Deploy**: `./docker.sh prod:up`

### CI/CD Ready
La configurazione è pronta per:
- GitHub Actions
- GitLab CI
- Jenkins
- Docker Hub/Registry

## 📈 Scalabilità

### Horizontal Scaling
```yaml
# docker-compose.prod.yml
backend:
  replicas: 3
  deploy:
    resources:
      limits:
        memory: 512M
```

### Load Balancing
Nginx configurato per:
- Rate limiting
- Connection pooling  
- Health check backends
- SSL termination

## 🎯 Next Steps

1. **SSL Setup**: Aggiungi certificati in `nginx/ssl/`
2. **Database Migration**: Implementa script in `database/`
3. **Monitoring**: Aggiungi Prometheus/Grafana
4. **Backup**: Script automatici database
5. **CI/CD**: Pipeline deployment automatico