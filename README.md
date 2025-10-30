# 🌊 LinkBay CMS# 🌊 LinkBay CMS



**Ciao! Sono LinkBay, il tuo compagno per gestire siti web e clienti in modo semplice e professionale.****Ciao! Sono LinkBay, il tuo compagno per gestire siti web e clienti in modo semplice e professionale.**



LinkBay CMS è una piattaforma pensata per le agenzie di marketing che vogliono offrire ai propri clienti un servizio completo di gestione siti web. Immagina di avere tutto sotto controllo: dai clienti ai siti, dalla fatturazione alle statistiche, tutto in un unico posto facile da usare.LinkBay CMS è una piattaforma pensata per le agenzie di marketing che vogliono offrire ai propri clienti un servizio completo di gestione siti web. Immagina di avere tutto sotto controllo: dai clienti ai siti, dalla fatturazione alle statistiche, tutto in un unico posto facile da usare.



------



## ✨ Cosa fa LinkBay?## ✨ Cosa fa LinkBay?



### Per le Agenzie### Per le Agenzie

- **Gestisci i tuoi clienti** in un'interfaccia dedicata- **Gestisci i tuoi clienti** in un'interfaccia dedicata

- **Crea e modifica siti web** velocemente- **Crea e modifica siti web** velocemente

- **Tieni traccia delle fatture** e dei pagamenti- **Tieni traccia delle fatture** e dei pagamenti

- **Lavora in team** con colleghi e collaboratori- **Lavora in team** con colleghi e collaboratori



### Per i Clienti### Per i Clienti

- **Accedi al tuo portale personale** per vedere i tuoi siti- **Accedi al tuo portale personale** per vedere i tuoi siti

- **Richiedi modifiche** o nuovi contenuti- **Richiedi modifiche** o nuovi contenuti

- **Controlla lo stato** dei tuoi progetti- **Controlla lo stato** dei tuoi progetti



### Per Tutti### Per Tutti

- **Siti web pubblicati** automaticamente- **Siti web pubblicati** automaticamente

- **Sicurezza garantita** con isolamento dei dati- **Sicurezza garantita** con isolamento dei dati

- **Velocità e affidabilità** grazie a tecnologie moderne- **Velocità e affidabilità** grazie a tecnologie moderne



------



## 🚀 Come iniziare## 🚀 Come iniziare



### Prerequisiti### Prerequisiti

- **Node.js** versione 20 o superiore- **Node.js** versione 20 o superiore

- **PostgreSQL** versione 17 o superiore- **PostgreSQL** versione 15 o superiore

- **Yarn** per gestire i pacchetti- **Yarn** per gestire i pacchetti



### Installazione Rapida### Installazione Rapida



1. **Clona il progetto**1. **Clona il progetto**

   ```bash   ```bash

   git clone https://github.com/AlessioQuagliara/LinkBay-CMS.git   git clone https://github.com/AlessioQuagliara/LinkBay-CMS.git

   cd LinkBay-CMS   cd LinkBay-CMS

   ```   ```



2. **Installa le dipendenze**2. **Installa le dipendenze**

   ```bash   ```bash

   # Backend   # Backend

   cd backend && yarn install   cd backend && yarn install



   # Frontend Landing   # Frontend Landing

   cd ../landing && yarn install   cd ../landing && yarn install



   # Frontend Management   # Frontend Management

   cd ../management && yarn install   cd ../management && yarn install

   ```   ```



3. **Configura il database**3. **Configura il database**

   ```bash   ```bash

   # Crea database PostgreSQL   # Crea database PostgreSQL

   createdb linkbaycms   createdb linkbaycms



   # Esegui migrazioni   # Esegui migrazioni

   cd backend && node ace migration:run   cd backend && node ace migration:run

   ```   ```



4. **Avvia i servizi**4. **Avvia i servizi**

   ```bash   ```bash

   # Terminale 1: Backend   # Terminale 1: Backend

   cd backend && node ace serve   cd backend && node ace serve



   # Terminale 2: Landing page   # Terminale 2: Landing page

   cd landing && yarn dev   cd landing && yarn dev



   # Terminale 3: Dashboard agenzia   # Terminale 3: Dashboard agenzia

   cd management && yarn dev   cd management && yarn dev

   ```   ```



5. **Apri nel browser**5. **Apri nel browser**

   - Landing: http://localhost:3001   - Landing: http://localhost:3001

   - Dashboard: http://localhost:3003   - Dashboard: http://localhost:3003

   - API: http://localhost:3000   - API: http://localhost:3000



------



## 🏗️ Come funziona dentro## 🏗️ Come funziona dentro



LinkBay è costruito con un'architettura moderna e scalabile:LinkBay è costruito con un'architettura moderna e scalabile:



### Il Cervello (Backend)### Il Cervello (Backend)

- **AdonisJS**: Framework Node.js potente e sicuro- **AdonisJS**: Framework Node.js potente e sicuro

- **PostgreSQL**: Database affidabile per i tuoi dati- **PostgreSQL**: Database affidabile per i tuoi dati

- **API REST**: Interfacce pulite per comunicare con i frontend- **API REST**: Interfacce pulite per comunicare con i frontend



### Le Interfacce (Frontend)### Le Interfacce (Frontend)

- **Landing Page**: Il volto pubblico del tuo business- **Landing Page**: Il volto pubblico del tuo business

- **Dashboard Agenzie**: Dove gestisci tutto- **Dashboard Agenzie**: Dove gestisci tutto

- **Portale Clienti**: Per i tuoi clienti finali- **Portale Clienti**: Per i tuoi clienti finali

- **Siti Pubblicati**: I siti web dei tuoi clienti- **Siti Pubblicati**: I siti web dei tuoi clienti



### La Sicurezza### La Sicurezza

- **Isolamento completo**: Ogni agenzia ha i suoi dati separati- **Isolamento completo**: Ogni agenzia ha i suoi dati separati

- **Autenticazione sicura**: Login protetto con token- **Autenticazione sicura**: Login protetto con token

- **Controllo accessi**: Solo chi deve vedere, vede- **Controllo accessi**: Solo chi deve vedere, vede



------



## 📊 Stato del Progetto## 📊 Stato del Progetto



Ecco dove siamo con lo sviluppo:Ecco dove siamo con lo sviluppo:



### ✅ Completato al 100%### ✅ Completato al 100%

- **🌐 Landing Page**: Sito pubblico bello e funzionale- **🌐 Landing Page**: Sito pubblico bello e funzionale

- **🔧 Backend Core**: API solide e sicure- **🔧 Backend Core**: API solide e sicure



### 🚧 In Sviluppo (~49%)### 🚧 In Sviluppo (49%)

- **🎛️ Dashboard Agenzie**: Gestione clienti e siti- **🎛️ Dashboard Agenzie**: Gestione clienti e siti

- **👥 Portale Clienti**: Area riservata per i clienti- **👥 Portale Clienti**: Area riservata per i clienti

- **🌍 Siti Pubblicati**: Generatore automatico di siti- **🌍 Siti Pubblicati**: Generatore automatico di siti

- **📱 App Mobile**: Versione mobile (futuro)- **📱 App Mobile**: Versione mobile (futuro)



### 🎯 Prossimi Passi### 🎯 Prossimi Passi

- Completare le dashboard mancanti- Completare le dashboard mancanti

- Aggiungere pagamenti automatici- Aggiungere pagamenti automatici

- Migliorare l'esperienza utente- Migliorare l'esperienza utente

- Preparare per il lancio pubblico- Preparare per il lancio pubblico



------



## 🛠️ Tecnologie Usate## 🛠️ Tecnologie Usate



- **Frontend**: React, TypeScript, Tailwind CSS- **Frontend**: React, TypeScript, Tailwind CSS

- **Backend**: AdonisJS, Node.js, PostgreSQL- **Backend**: AdonisJS, Node.js, PostgreSQL

- **Deployment**: Docker, Nginx, CI/CD- **Deployment**: Docker, Nginx, CI/CD

- **Testing**: Jest, Cypress per qualità garantita- **Testing**: Jest, Cypress per qualità garantita



------



## 🤝 Vuoi Contribuire?## 🤝 Vuoi Contribuire?



LinkBay cresce grazie alla comunità! Se vuoi aiutare:LinkBay cresce grazie alla comunità! Se vuoi aiutare:



1. **Segnala bug** o **idee** nelle Issues1. **Segnala bug** o **idee** nelle Issues

2. **Proponi modifiche** con Pull Request2. **Proponi modifiche** con Pull Request

3. **Condividi** il progetto con amici3. **Condividi** il progetto con amici



### Come contribuire al codice### Come contribuire al codice

1. Fork del repository1. Fork del repository

2. Crea un branch per la tua feature2. Crea un branch per la tua feature

3. Scrivi test per le tue modifiche3. Scrivi test per le tue modifiche

4. Fai commit e push4. Fai commit e push

5. Apri una Pull Request5. Apri una Pull Request



------



## 📄 Licenza## 📄 Licenza



Questo progetto è **privato** e protetto da copyright. Tutti i diritti riservati a **Alessio Quagliara**.Questo progetto è **privato** e protetto da copyright. Tutti i diritti riservati a **Alessio Quagliara**.



Per informazioni commerciali o partnership, contatta l'autore.Per informazioni commerciali o partnership, contatta l'autore.



------



## 🙋‍♂️ Chi c'è dietro?## 🙋‍♂️ Chi c'è dietro?



**Alessio Quagliara** - Sviluppatore full-stack appassionato di web e tecnologia. LinkBay è il mio progetto per dimostrare come la tecnologia può semplificare la vita delle agenzie di marketing.**Alessio Quagliara** - Sviluppatore full-stack appassionato di web e tecnologia. LinkBay è il mio progetto per dimostrare come la tecnologia può semplificare la vita delle agenzie di marketing.



*Con ❤️ e tanto ☕ per rendere il web un posto migliore.**Con ❤️ e tanto ☕ per rendere il web un posto migliore.*



------



*LinkBay CMS - Il tuo ponte verso il successo digitale* 🌉*LinkBay CMS - Il tuo ponte verso il successo digitale* 🌉

### 🎪 Architettura Multi-Frontend

La piattaforma è strutturata con frontend specializzati e un backend scalabile:

1. **Landing** (`landing/`) → Sito marketing e presentazione
2. **Agency** (`agency/`) → Dashboard per agenzie e team
3. **Management** (`management/`) → Gestionale agenzie (login/register)
4. **Customer** (`customer/`) → Portale clienti e gestione servizi
5. **Websites** (`websites/`) → Gestione siti web e contenuti
6. **Backend** (`backend/`) → API RESTful con architettura SOLID

### 📦 Repository Contents

Questo repository contiene il **sistema completo LinkBay CMS**:

- **Frontend Landing** (`landing/`): Sito marketing ottimizzato SEO
- **Frontend Agency** (`agency/`): Dashboard amministrativa con Shopify-style UI
- **Frontend Management** (`management/`): Gestionale agenzie con autenticazione
- **Frontend Customer** (`customer/`): Portale self-service per clienti
- **Frontend Websites** (`websites/`): Gestione siti web e contenuti
- **Backend Services** (`backend/`): API scalabile con PostgreSQL + Lucid ORM
- **Shared Libraries** (`shared/`): Componenti e configurazioni condivise

---

## ⚡ Quick Start

### Prerequisites

- Node.js 20+
- PostgreSQL 15+
- npm or yarn
- Git

### 🚀 Launch Development Environment

```bash
# Clone repository
git clone https://github.com/AlessioQuagliara/LinkBay-CMS.git
cd LinkBay-CMS

# Setup Backend (Database + API)
cd backend
npm install
# Configura .env con DATABASE_URL
node ace migration:run
node ace db:seed  # (opzionale) dati demo
npm run dev      # Backend su http://localhost:3000

# In terminali separate - Frontend
cd ../landing && npm install && npm run dev    # Landing su http://localhost:3001
cd ../agency && npm install && npm run dev     # Agency su http://localhost:3002
cd ../management && npm install && npm run dev # Management su http://localhost:3003
cd ../customer && npm install && npm run dev   # Customer su http://localhost:3004
cd ../websites && npm install && npm run dev   # Websites su http://localhost:3005
```

### 🌐 Access Points

Once running, access:

- **Backend API**: http://localhost:3000
- **Landing**: http://localhost:3001
- **Agency Dashboard**: http://localhost:3002
- **Management Portal**: http://localhost:3003
- **Customer Portal**: http://localhost:3004
- **Website Manager**: http://localhost:3005

### 🔐 Credenziali Demo

```
Admin: admin@linkbay-cms.com / admin123
Agency: demo@agency.com / demo123
```

---

## 🏗️ Architettura

### Frontend Specializzati + Backend Scalabile

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LinkBay CMS Platform                           │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
┌─────────▼──┐ ┌─────▼─────┐ ┌───▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Landing  │ │   Agency  │ │Management │ │ Customer  │ │  Websites  │
│   (SEO)    │ │ (Dashboard)│ │  (Auth)   │ │ (Portal)  │ │  (CMS)     │
│ • Marketing│ │ • Admin    │ │ • Login    │ │ • Client  │ │ • Content  │
│ • Contact  │ │ • Stats    │ │ • Register │ │ • Orders  │ │ • Editor   │
│ • SEO Opt. │ │ • Users    │ │ • Portal   │ │ • Support │ │ • Media    │
└────────────┘ └────────────┘ └───────────┘ └───────────┘ └────────────┘
      │            │            │            │            │
      └────────────┼────────────┼────────────┼────────────┘
                   │            │            │
         ┌─────────▼────────────▼────────────▼────────────┐
         │        Shared Components           │
         │  • UI Components (DRY)            │
         │  • TypeScript Types               │
         │  • Utility Functions              │
         │  • Design System                  │
         └───────────────────────────────────┘
                        │
         ┌───────────────▼───────────────┐
         │       Backend API (SOLID)     │
         │  ┌─────────────────────────┐  │
         │  │   Controllers (HTTP)    │  │
         │  │ • Auth • User • Agency  │  │
         │  └─────────────────────────┘  │
         │  ┌─────────────────────────┐  │
         │  │   Services (Business)  │  │
         │  │ • Auth • User • CRUD    │  │
         │  └─────────────────────────┘  │
         │  ┌─────────────────────────┐  │
         │  │   Database (Lucid ORM) │  │
         │  │ • PostgreSQL • ORM     │  │
         │  └─────────────────────────┘  │
         └───────────────────────────────┘
```

### Principi Architetturali

- ✅ **SOLID Backend**: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- ✅ **DRY Frontend**: Componenti condivisi, utility riutilizzabili, tipi unificati
- ✅ **KISS Design**: Interfacce semplici, logica chiara, manutenzione facile
- ✅ **Multi-Frontend**: Interfacce specializzate per diversi use case
- ✅ **Type-Safe**: TypeScript end-to-end per sicurezza del codice
- ✅ **Scalable**: Architettura modulare che cresce con il progetto
- ✅ **SEO-Optimized**: Landing page con sitemap, meta tags, performance

---

## 🛠️ Stack Tecnologico

### Frontend

| Tecnologia | Uso | Versione |
|------------|-----|----------|
| **React** | UI Library | 18.3+ |
| **TypeScript** | Linguaggio | 5.9+ |
| **Vite** | Build Tool | 7.1+ |
| **Tailwind CSS** | Styling | 3.4+ |
| **React Router DOM** | Routing | 7.9+ |
| **Lucide React** | Icons | Latest |

#### 🎨 Frontend Management (Porta 3003)
- **React Hook Form** - Form validation avanzata
- **Zod** - Schema validation TypeScript-first
- **SEO Hooks** - Gestione meta tags e noindex per privacy

### Backend (✅ Complete)

| Tecnologia | Uso | Versione |
|------------|-----|----------|
| **Node.js** | Runtime | 20+ |
| **AdonisJS** | Web Framework | 6.0+ |
| **Lucid ORM** | Database ORM | Latest |
| **PostgreSQL** | Database | 17+ |
| **JWT** | Authentication | 9.0+ |
| **bcrypt** | Password Hashing | 5.1+ |
| **VineJS** | Validation | Latest |
| **CORS** | Cross-Origin | 2.8+ |

### Development Tools

| Tecnologia | Uso |
|------------|-----|
| **Ace** | AdonisJS Command Runner |
| **ESLint** | Code Linting |
| **Prettier** | Code Formatting |
| **Lucid Studio** | Database UI (opzionale) |
| **Husky** | Git Hooks |

---

## 📁 Struttura del Progetto

```
LinkBay-CMS/
│
├── 📦 shared/                      # ⭐ COMPONENTI CONDIVISI (DRY)
│   ├── components/                 # UI Components riutilizzabili
│   ├── utils/                      # Utility functions
│   ├── types/                      # TypeScript interfaces
│   └── styles/                     # Stili globali e temi
│
├── 🏠 landing/                     # Landing Page & Marketing (SEO)
│   ├── src/
│   │   ├── components/            # Componenti specifici landing
│   │   ├── pages/                 # Pagine del sito
│   │   ├── hooks/                 # SEO hooks ottimizzati
│   │   └── assets/                # Immagini e risorse
│   ├── package.json
│   └── vite.config.ts
│
├── 🏢 agency/                      # Dashboard Agenzie (Shopify-style)
│   ├── src/
│   │   ├── components/            # Componenti dashboard
│   │   │   ├── Layout/           # Layout e navigazione
│   │   │   ├── Header.tsx        # Header moderno
│   │   │   └── Footer.tsx        # Footer semplice
│   │   ├── pages/                # Pagine dashboard
│   │   └── hooks/                # Custom React hooks
│   ├── package.json
│   └── vite.config.ts
│
├── � management/                  # Gestionale Agenzie (Auth Portal)
│   ├── src/
│   │   ├── components/            # Componenti auth riutilizzabili
│   │   ├── pages/
│   │   │   ├── auth/             # Login e registrazione
│   │   │   │   ├── LoginPage.tsx # Form login professionale
│   │   │   │   └── RegisterPage.tsx # Registrazione agenzia
│   │   │   ├── dashboard/        # Dashboard post-login
│   │   │   ├── clients/          # Gestione clienti
│   │   │   ├── websites/         # Gestione siti web
│   │   │   └── billing/          # Fatturazione
│   │   ├── hooks/                # SEO hooks e utilities
│   │   └── utils/                # Helper functions
│   ├── public/                   # Logo e assets
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf                # Reverse proxy config
│   └── README.md                 # Documentazione specifica
│
├── �👥 customer/                    # Portale Clienti (WIP)
│   ├── src/
│   │   ├── components/            # Componenti portale cliente
│   │   ├── pages/                # Pagine cliente
│   │   └── services/             # API services
│   ├── package.json
│   └── vite.config.ts
│
├── 🌐 websites/                    # Gestione Siti Web (WIP)
│   ├── src/
│   │   ├── components/            # CMS components
│   │   ├── editor/               # Content editor
│   │   └── templates/            # Template siti
│   ├── package.json
│   └── vite.config.ts
│
├── 🔗 backend/                     # ⭐ BACKEND API (SOLID Complete)
│   ├── app/
│   │   ├── controllers/           # HTTP request handlers
│   │   │   ├── auth_controller.ts # Auth endpoints
│   │   │   └── user_controller.ts # User management
│   │   ├── models/                # Lucid ORM models
│   │   │   ├── user.ts            # User model
│   │   │   └── agency.ts          # Agency model
│   │   ├── services/              # Business logic (SOLID)
│   │   │   ├── auth_service.ts    # Authentication logic
│   │   │   └── user_service.ts    # User CRUD operations
│   │   ├── validators/            # VineJS schemas
│   │   │   └── auth_validator.ts  # Input validation
│   │   └── middleware/            # AdonisJS middlewares
│   ├── database/
│   │   └── migrations/            # Lucid migrations
│   ├── config/                    # AdonisJS configuration
│   ├── start/                     # Application bootstrap
│   ├── tests/                     # Test suite
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   ├── ace.js                     # Ace command runner
│   └── server.ts                  # AdonisJS server setup
│
├── 📄 LICENSE                      # Licenza del progetto
├── 📖 README.md                    # Questo file
└── 🔧 package.json                 # Monorepo root
```

### 🌟 Shared Package - Il Cuore della Riutilizzabilità (DRY)

Il package `shared/` contiene:

- ✅ **Components**: UI components utilizzabili da tutti i frontend
- ✅ **Types**: Interfacce TypeScript condivise
- ✅ **Utils**: Funzioni helper riutilizzabili
- ✅ **Styles**: Temi e stili base

### 🔗 Backend Architecture - SOLID Principles

Il backend segue i principi **SOLID** con **AdonisJS + Lucid ORM**:

- ✅ **Single Responsibility**: Ogni service/modulo ha una sola responsabilità
- ✅ **Open/Closed**: Estensibile senza modificare codice esistente
- ✅ **Liskov Substitution**: Services implementano contratti chiari
- ✅ **Interface Segregation**: Interfacce piccole e specifiche
- ✅ **Dependency Inversion**: Dipendenze attraverso astrazioni

---

## 🔌 Backend API

### Database Schema


// Modelli principali
User (Agency/Admin)
├── id, email, password (hashed), name, role
└── agencies[], tokens[]

Agency
├── id, name, description, logo
└── websites[], customers[]

Website
├── id, name, domain, status
└── agency, customer

Customer
├── id, name, email, phone, company
└── agency, websites[]

RefreshToken
├── id, token, expiresAt
└── user
```

### API Endpoints

#### 🔐 Authentication

```http
POST   /api/v1/auth/register      # Registrazione utente
POST   /api/v1/auth/login         # Login
POST   /api/v1/auth/refresh       # Refresh access token
POST   /api/v1/auth/logout        # Logout
```

#### 👤 Users (Protected)

```http
GET    /api/v1/users/me           # Profilo corrente
PUT    /api/v1/users/me           # Aggiorna profilo
GET    /api/v1/users              # Lista utenti (admin)
GET    /api/v1/users/:id          # Dettaglio utente (admin)
```

#### 🏥 Health Check

```http
GET    /api/v1/health             # Status server
```

### Request/Response Examples

#### Register
```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agency@example.com",
    "password": "password123",
    "name": "My Agency"
  }'
```

#### Login
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agency@example.com",
    "password": "password123"
  }'
```

#### Get Profile (Authenticated)
```bash
curl http://localhost:3000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Security Features

- ✅ **JWT Authentication** con refresh token rotation
- ✅ **Password Hashing** con bcrypt (10 rounds)
- ✅ **Input Validation** con VineJS schemas
- ✅ **CORS Protection** configurabile
- ✅ **Error Sanitization** in produzione
- ✅ **SQL Injection Protection** via Lucid ORM
- ✅ **Type Safety** end-to-end con TypeScript

---

## 🎨 Principi di Design

### 1. SOLID (Backend Architecture)

**Single Responsibility Principle**
```typescript
// ❌ WRONG: Controller fa tutto
class UserController {
  async createUser(req, res) {
    // Validazione, business logic, database, response
  }
}

// ✅ CORRECT: Separazione chiara
class AuthController { /* Solo HTTP handling */ }
class AuthService { /* Solo business logic */ }
class UserModel { /* Solo database operations */ }
```

**Dependency Inversion**
```typescript
// ✅ CORRECT: Dipendenze attraverso interfacce
interface IAuthService {
  register(email: string, password: string): Promise<User>;
}

class AuthController {
  constructor(private authService: IAuthService) {}
}
```

### 2. DRY (Don't Repeat Yourself)

**Problema**: Componenti duplicati tra frontend diversi.

**Soluzione**:
- Componenti UI nel package `shared/components`
- Utility functions condivise in `shared/utils`
- Tipi TypeScript unificati in `shared/types`

**Esempio pratico:**

```typescript
// shared/components/Button.tsx
export const Button: React.FC<ButtonProps> = ({ children, variant, ...props }) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      {...props}
    >
      {children}
    </button>
  );
};

// Utilizzato in agency/src/components/Dashboard.tsx
import { Button } from '@shared/components';

// Utilizzato in customer/src/components/Profile.tsx  
import { Button } from '@shared/components';
```

### 3. KISS (Keep It Simple, Stupid)

**Prima**: Codice complesso e difficile da mantenere
```typescript
// Codice JavaScript/TypeScript non ottimizzato
const useSEO = (config) => {
  // 97 righe di logica duplicata
  // Meta tags ripetuti
  // Open Graph duplicato
  // Codice non modulare
}
```

**Dopo**: Codice pulito e semplice
```typescript
// Codice ottimizzato con helper functions
const updateMeta = (name: string, content: string) => {
  // Helper riutilizzabile
};

const useSEO = (config) => {
  // 55 righe invece di 97
  // Logica chiara e modulare
  // Mantenibile e scalabile
};
```

### 4. Frontend Specializzati

**Ogni frontend serve un use case specifico**:

- 🏠 **Landing**: Marketing, presentazione, conversione (SEO ottimizzato)
- 🏢 **Agency**: Gestione operativa, statistiche, amministrazione (Shopify-style)
- 👥 **Customer**: Self-service, supporto, fatturazione
- 🌐 **Websites**: Content management, editing, pubblicazione

### Risultati Ottenuti

- ✅ **Backend**: Da 0 a 100% completo con architettura SOLID
- ✅ **Landing**: Da 40% a 85% con SEO ottimizzato
- ✅ **Agency**: Da 40% a 85% con UI professionale
- ✅ **Codice**: Ridotto del 30-50% mantenendo funzionalità
- ✅ **Performance**: Migliorata con lazy loading e ottimizzazioni
- ✅ **Manutenibilità**: Codice modulare e testabile

---

## ⚡ Funzionalità

### 🏠 Landing Frontend (85% Complete)

- ✅ **Homepage responsive** con hero section animata
- ✅ **Pagine About, Services, Contact** ottimizzate SEO
- ✅ **Form di contatto integrato** con validazione
- ✅ **Design mobile-first** e accessibile
- ✅ **SEO ottimizzato**: Meta tags, sitemap, Open Graph
- ✅ **Cookie consent** GDPR compliant
- ✅ **Performance ottimizzata** con lazy loading

### 🏢 Agency Dashboard (35% Complete)

- ✅ **Dashboard con statistiche** e metriche in tempo reale
- ✅ **Shopify-style UI** con sidebar fissa e header moderno
- ✅ **Sistema di notifiche** integrato
- ✅ **Layout responsive** con navigazione mobile
- ✅ **Gestione clienti** e progetti
- ✅ **Componenti riutilizzabili** (DRY principle)
- ✅ **TypeScript strict** per type safety

### � Management Frontend (100% Complete)

- ✅ **Login professionale** con form validazione avanzata
- ✅ **Registrazione agenzia** con campi specifici (nome, descrizione, logo)
- ✅ **SEO configurato** con noindex per privacy delle pagine auth
- ✅ **UI moderna** con Tailwind CSS e Lucide React icons
- ✅ **Form validation** con React Hook Form + Zod schemas
- ✅ **Responsive design** ottimizzato per desktop e mobile
- ✅ **TypeScript strict** per massima type safety
- ✅ **Integrazione pronta** con backend API per autenticazione

### �👥 Customer Portal (40% In Progress)

- 🚧 **Profilo cliente personalizzabile**
- 🚧 **Gestione ordini e servizi**
- 🚧 **Sistema di supporto integrato**
- 🚧 **Dashboard self-service**
- 🚧 **Fatturazione e pagamenti**

### 🌐 Website Manager (40% In Progress)

- 🚧 **Editor di contenuti WYSIWYG**
- 🚧 **Gestione media e risorse**
- 🚧 **Template e temi personalizzabili**
- 🚧 **Pubblicazione e deployment**
- 🚧 **Content management system**

### 🔗 Backend API (100% Complete)

- ✅ **Architettura SOLID** completamente implementata con AdonisJS
- ✅ **Autenticazione JWT** con refresh token
- ✅ **Database PostgreSQL** con Lucid ORM
- ✅ **API RESTful** con validazione VineJS
- ✅ **Gestione errori centralizzata**
- ✅ **Middleware sicuri** (CORS, auth, validation)
- ✅ **Database migrations** con Ace
- ✅ **TypeScript end-to-end** per type safety

### 🔗 Management Frontend Integration

**API Endpoints utilizzati dal Management Frontend:**

```typescript
// Auth endpoints (già implementati nel backend)
POST /api/v1/auth/register  // Registrazione nuova agenzia
POST /api/v1/auth/login     // Login agenzia esistente
POST /api/v1/auth/refresh   // Refresh access token
POST /api/v1/auth/logout    // Logout sicuro

// User endpoints (per profilo agenzia)
GET  /api/v1/users/me       // Recupera dati agenzia corrente
PUT  /api/v1/users/me       // Aggiorna profilo agenzia
```

**Flusso di autenticazione:**
1. **Registrazione**: Form → API register → JWT token → Dashboard
2. **Login**: Form → API login → JWT token → Dashboard  
3. **Sessione**: Token salvato in localStorage → Auto-login
4. **Logout**: Clear localStorage → Redirect to login

**Sicurezza implementata:**
- ✅ **Token rotation** per refresh automatico
- ✅ **Password hashing** con bcrypt nel backend
- ✅ **Input validation** con VineJS schemas
- ✅ **Error handling** user-friendly
- ✅ **No sensitive data** esposto nel frontend

---

## 🚢 Deployment

### Development Environment

```bash
# 1. Backend Setup
cd backend
npm install
cp .env.example .env  # Configura DATABASE_URL
node ace migration:run
node ace db:seed       # (opzionale) dati demo
npm run dev          # Backend su http://localhost:3000

# 2. Frontend Setup (terminali separate)
cd ../landing && npm install && npm run dev    # http://localhost:3001
cd ../agency && npm install && npm run dev     # http://localhost:3002
cd ../management && npm install && npm run dev # http://localhost:3003
cd ../customer && npm install && npm run dev   # http://localhost:3004
cd ../websites && npm install && npm run dev   # http://localhost:3005
```

### Production Build

```bash
# Backend
cd backend
npm run build
npm start

# Frontend specifici
cd ../agency && npm run build
cd ../landing && npm run build
```

### Environment Variables

#### Backend (.env)
```env
NODE_ENV=production
PORT=3000
DATABASE_URL="postgresql://user:password:host:port/database"
JWT_SECRET=your-production-secret-key
JWT_EXPIRES_IN=7d
JWT_REFRESH_EXPIRES_IN=30d
CORS_ORIGIN=https://yourdomain.com,https://www.yourdomain.com
```

#### Frontend (.env)
```env
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=LinkBay CMS
```

---

## 🧪 Testing

```bash
# Test specifico frontend
cd agency && npm run test

# Lint code
cd agency && npm run lint

# Type checking
cd agency && npm run type-check
```

---

## ⚠️ Note Importanti

### 🔐 Management Frontend
- **Pagine Auth Private**: Login e registrazione hanno `noindex` per privacy SEO
- **Token Storage**: JWT salvati in localStorage (considerare httpOnly cookies per produzione)
- **Form Validation**: Utilizza React Hook Form + Zod per validazione robusta
- **UI Consistency**: Design system condiviso con altri frontend per coerenza
- **API Integration**: Pronto per connessione con backend - attualmente mock data

### 🔧 Troubleshooting

**Errore "lucide-react not found"**
```bash
cd management
npm install lucide-react
npm run dev
```

**Porta 3003 occupata**
```bash
# Cambia porta in vite.config.ts
export default defineConfig({
  server: { port: 3006 }
})
```

**API Connection Issues**
- Verifica che backend sia attivo su porta 3000
- Controlla `VITE_API_URL` nel file `.env`
- Verifica CORS settings nel backend

---

## 📝 Licenza e Copyright

### Licenza
Questo progetto è rilasciato sotto **[LICENZA CUSTOM]** (vedi file `LICENSE`).

### Avviso Importante
- **Il codice è di proprietà personale di Alessio Quagliara** e non è proprietà di altri
- **Ogni uso commerciale richiede consenso scritto esplicito**
- **Non è permesso a terzi registrare marchi o brevetti derivati da questo progetto**
- **Non è permesso modificare il codice senza consenso, poiché tutto il progetto è protetto da registrazione di marchio**
- **Non è consentito copiare il codice senza consenso - il codice è protetto e la violazione può comportare azioni legali**

### Copyright
© 2024 Alessio Quagliara. Tutti i diritti riservati.

---

## 🤝 Contribuire

### Workflow

1. Crea branch feature: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Apri Pull Request

### Coding Standards

- ✅ Segui principi **DRY & KISS**
- ✅ TypeScript strict mode
- ✅ Test per nuove features
- ✅ Componenti riutilizzabili in `shared/`
- ✅ Design responsive e accessibile

---

## 👥 Team

- **Alessio Quagliara** - Full Stack Developer & Project Owner

---

## 📞 Supporto

- 📧 Email: quagliara.alessio@outlook.com
- 🌐 Website: https://www.linkbay-cms.com
- 📱 LinkedIn: [Alessio Quagliara](https://www.linkedin.com/in/alessio-quagliara-a1a91b1a8/)

---

<div align="center">

**Fatto con ❤️ da Alessio Quagliara**

[![Made with TypeScript](https://img.shields.io/badge/Made%20with-TypeScript-blue)](https://www.typescriptlang.org/)
[![Made with React](https://img.shields.io/badge/Made%20with-React-blue)](https://reactjs.org/)
[![Made with Tailwind](https://img.shields.io/badge/Made%20with-Tailwind-blue)](https://tailwindcss.com/)

</div>  
