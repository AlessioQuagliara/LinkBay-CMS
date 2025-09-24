**Architettura LinkBay-CMS containerizzata**

## 🐳 Architettura Docker Multi-Container

### **1. Container in Esecuzione**
Quando esegui `./docker.sh dev:up`, hai **7 container** che lavorano insieme:

```
📦 linkbay-postgres-dev    → PostgreSQL Database (porta 5432)
📦 linkbay-redis-dev       → Redis Cache (porta 6379)  
📦 linkbay-backend-dev     → Node.js API (porta 3000)
📦 linkbay-landing-dev     → React Landing (porta 3001)
📦 linkbay-agency-dev      → React Agency (porta 3002)
📦 linkbay-customer-dev    → React Customer (porta 3003)
📦 linkbay-websites-dev    → React Websites (porta 3004)
```

### **2. Network Isolation e Comunicazione**

**Rete Docker `linkbay-network`:**
- I container comunicano tra loro tramite **nomi DNS interni**
- Backend accede a PostgreSQL via `postgres:5432` (non localhost)
- Frontend accede a Backend via `http://backend:3000` internamente
- **Port mapping** espone servizi verso l'host macOS

## 🌐 Flusso di Comunicazione

### **Sviluppo (docker-compose.dev.yml):**

```
Browser → localhost:3001 → Landing Container (React)
Browser → localhost:3002 → Agency Container (React)  
Browser → localhost:3003 → Customer Container (React)
Browser → localhost:3004 → Websites Container (React)

Frontend → localhost:3000 → Backend Container (Node.js)
Backend → postgres:5432 → PostgreSQL Container
Backend → redis:6379 → Redis Container
```

### **Produzione (docker-compose.prod.yml):**

```
Internet → Nginx Container (80/443) → Reverse Proxy
Nginx → backend:3000 → Backend API
Nginx → landing:80 → Landing Static Files
Nginx → agency:80 → Agency Static Files
Nginx → customer:80 → Customer Static Files  
Nginx → websites:80 → Website Static Files
```

## 🏗️ Breakdown per Container

### **📦 Backend Container (porta 3000)**
- **Cosa fa**: API REST per tutte le applicazioni frontend
- **Framework**: Node.js + Express + Knex + PostgreSQL
- **Funzioni**:
  - Autenticazione JWT + OAuth (Google, GitHub)
  - Multi-tenancy con Row-Level Security
  - Payment processing (Stripe Connect)
  - Plugin system e marketplace
  - Email service (SMTP Aruba)
  - File upload gestione
- **Database**: Si connette a `postgres:5432` via network Docker
- **Cache**: Usa `redis:6379` per sessioni e caching

### **📦 Landing Container (porta 3001)**
- **Cosa fa**: Sito pubblico marketing di LinkBay-CMS
- **Framework**: React + Vite + Tailwind CSS
- **Funzioni**:
  - Homepage con pricing e features
  - Registrazione agenzie
  - Login/OAuth integration
  - SEO ottimizzato per acquisition
- **API**: Chiama `localhost:3000` (backend) via fetch/axios

### **📦 Agency Container (porta 3002)**
- **Cosa fa**: Dashboard completo per web agencies
- **Framework**: React + Vite + Tailwind CSS  
- **Funzioni**:
  - Workspace management per progetti clienti
  - Website builder drag & drop
  - Customer CRM integrato
  - Plugin store e installazioni
  - Billing e analytics revenue
  - Team management e permissions
- **API**: Authenticated requests a `localhost:3000`

### **📦 Customer Container (porta 3003)**
- **Cosa fa**: Pannello gestione per clienti finali delle agenzie
- **Framework**: React + Vite + Tailwind CSS
- **Funzioni**:
  - Content editor per pagine sito
  - Media library gestione
  - Theme customizer e personalizzazione
  - Plugin management per sito
  - Analytics traffico e conversioni
  - Subscription e billing management
- **API**: Scoped requests al backend per dati specifici cliente

### **📦 Websites Container (porta 3004)**
- **Cosa fa**: Rendering engine per siti web pubblici dei clienti
- **Framework**: React + Vite (potenzialmente SSR)
- **Funzioni**:
  - Dynamic page rendering da database
  - Theme system applicazione
  - Content blocks rendering
  - SEO optimization automatica  
  - Analytics tracking (GA, Facebook Pixel)
  - E-commerce frontend (carrello, checkout)
- **API**: Fetch contenuti da backend via subdomain routing

## 🔧 Docker Volumes e Persistenza

### **Volume Mapping Sviluppo:**
```yaml
volumes:
  - ./backend:/app          # Hot reload backend
  - ./agency:/app           # Hot reload React
  - /app/node_modules       # Preserve container node_modules
```

### **Data Persistence:**
```yaml
volumes:
  postgres_            # Database persistente
  redis_               # Cache persistente  
```

## 🌍 Routing e Domain Management

### **Sviluppo Locale:**
- **Landing**: http://localhost:3001 → Marketing site
- **Agency**: http://localhost:3002 → Dashboard agenzie  
- **Customer**: http://localhost:3003 → Pannello clienti
- **Websites**: http://localhost:3004 → Siti web dinamici
- **Backend**: http://localhost:3000 → API endpoints

### **Produzione con Nginx:**
```
linkbay-cms.com           → Landing Container
app.linkbay-cms.com       → Agency Container  
manage.linkbay-cms.com    → Customer Container
*.linkbay-sites.com       → Websites Container (wildcard)
api.linkbay-cms.com       → Backend Container
```

## ⚡ Hot Reload e Sviluppo

### **Frontend Hot Reload:**
- **Volume mount** del codice sorgente
- **Vite dev server** rileva cambiamenti file
- **Browser auto-refresh** quando salvi modifiche
- **Tailwind CSS** compilation automatica

### **Backend Hot Reload:**  
- **Nodemon** watching file changes
- **Container restart** automatico su modifiche
- **Database connections** persistent via network

## 🔒 Sicurezza e Isolamento

### **Network Isolation:**
- Database **non esposto** externally in produzione
- Redis **accessible solo** da backend
- **Frontend isolation** per security

### **Environment Variables:**
```yaml
environment:
  - NODE_ENV=development
  - DATABASE_URL=postgres://root:root@postgres:5432/linkbaycms
  - REDIS_URL=redis://redis:6379
  - JWT_SECRET=your-secret
```

## 📊 Monitoraggio e Logs

### **Visualizzare Logs:**
```bash
./docker.sh dev:logs              # Tutti i container
docker logs linkbay-backend-dev  # Solo backend
docker logs linkbay-agency-dev   # Solo agency
```

### **Health Checks:**
- Backend ha **health check** su `/api/health`
- Database **connection monitoring**
- **Container restart** automatico su failure

## 🚀 Deployment Flow

### **Sviluppo → Produzione:**
1. **Build TypeScript**: `tsc` compilation
2. **React Build**: `vite build` per static assets
3. **Multi-stage Docker**: Optimized production images
4. **Nginx serving**: Static files + reverse proxy
5. **SSL termination**: HTTPS certificati automatici
