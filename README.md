# 🚀 LinkBay CMS - Multi-Frontend Web Management Platform

<div align="center">

**Piattaforma Multi-Frontend per la Gestione Completa di Siti Web e Clienti**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/AlessioQuagliara/LinkBay-CMS)
[![Built with DRY](https://img.shields.io/badge/Built%20with-DRY-blue)](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
[![Follows KISS](https://img.shields.io/badge/Follows-KISS-green)](https://en.wikipedia.org/wiki/KISS_principle)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-green)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18.3-blue)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/Status-Development-orange)](#status)

</div>

---

## 📋 Indice

- [Panoramica](#-panoramica)
- [Quick Start](#-quick-start)
- [Architettura](#-architettura)
- [Stack Tecnologico](#-stack-tecnologico)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Licenza e Copyright](#-licenza-e-copyright)
- [Principi di Design](#-principi-di-design)
- [Deployment](#-deployment)

---

## 🎯 Panoramica

**LinkBay CMS** è una piattaforma moderna multi-frontend che offre soluzioni complete per la gestione di siti web, clienti e contenuti attraverso interfacce dedicate per diverse tipologie di utenti.

### 📊 Status di Sviluppo

```
🚧 Frontend Landing:    ████████░░░░░░░░░░░░  40% In Progress
🚧 Frontend Agency:     ████████░░░░░░░░░░░░  40% In Progress 
🚧 Frontend Customer:   ████████░░░░░░░░░░░░  40% In Progress
🚧 Backend Services:    ████████░░░░░░░░░░░░  40% In Progress
🚧 Shared Components:   ████████░░░░░░░░░░░░  40% In Progress
🎯 Overall:             ████████░░░░░░░░░░░░  70% IN DEVELOPMENT
```

### 🎪 Architettura Multi-Frontend

La piattaforma è strutturata con frontend specializzati:

1. **Landing** (`landing/`) → Sito marketing e presentazione
2. **Agency** (`agency/`) → Dashboard per agenzie e team
3. **Customer** (`customer/`) → Portale clienti e gestione servizi
4. **Websites** (`websites/`) → Gestione siti web e contenuti

### 📦 Repository Contents

Questo repository contiene il **sistema completo LinkBay CMS**:

- **Frontend Landing** (`landing/`): Sito marketing e homepage
- **Frontend Agency** (`agency/`): Dashboard amministrativa per agenzie
- **Frontend Customer** (`customer/`): Portale self-service per clienti
- **Frontend Websites** (`websites/`): Gestione siti web e contenuti
- **Backend Services** (`backend/`): API e servizi backend
- **Shared Libraries** (`shared/`): Componenti e configurazioni condivise

---

## ⚡ Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### 🚀 Launch Development Environment

```bash
# Clone repository
git clone https://github.com/AlessioQuagliara/LinkBay-CMS.git
cd LinkBay-CMS

# Install dependencies for all frontends
npm install

# Start specific frontend
cd landing && npm run dev    # Landing page
cd agency && npm run dev     # Agency dashboard
cd customer && npm run dev   # Customer portal
cd websites && npm run dev   # Website manager
```

### 🌐 Access Points

Once running, access:

- **Landing**: http://localhost:3000
- **Agency Dashboard**: http://localhost:3001
- **Customer Portal**: http://localhost:3002
- **Website Manager**: http://localhost:3003

---

## 🏗️ Architettura

### Frontend Specializzati

```
┌─────────────────────────────────────────────────────────────┐
│                    LinkBay CMS Platform                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼───┐ ┌────▼────┐ ┌───▼──────┐ ┌────▼─────┐
│  Landing  │ │ Agency  │ │Customer  │ │Websites  │
│           │ │Dashboard│ │ Portal   │ │ Manager  │
│ • Home    │ │ • Stats │ │ • Profile│ │ • CMS    │
│ • About   │ │ • Users │ │ • Orders │ │ • Pages  │
│ • Contact │ │ • Sites │ │ • Support│ │ • Media  │
└───────────┘ └─────────┘ └──────────┘ └──────────┘
        │           │           │           │
        └───────────┼───────────┼───────────┘
                    │           │
              ┌─────▼───────────▼─────┐
              │   Shared Components   │
              │  • UI Components      │
              │  • Utilities          │
              │  • Types & Interfaces │
              └───────────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Backend Services │
              │  • API Gateway    │
              │  • Authentication │
              │  • Database       │
              └───────────────────┘
```

### Principi Architetturali

- ✅ **Multi-Frontend**: Interfacce specializzate per diversi use case
- ✅ **Shared Components**: Componenti UI riutilizzabili tra frontend
- ✅ **Type-Safe**: TypeScript end-to-end per sicurezza del codice
- ✅ **Modular**: Ogni frontend è indipendente ma condivide risorse comuni
- ✅ **Responsive**: Design mobile-first su tutti i frontend

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

### Backend (Coming Soon)

| Tecnologia | Uso | Versione |
|------------|-----|----------|
| **Node.js** | Runtime | 20+ |
| **TypeScript** | Linguaggio | 5.9+ |
| **Express** | Web Framework | Latest |
| **Prisma** | ORM | Latest |
| **PostgreSQL** | Database | 15+ |

### Development Tools

| Tecnologia | Uso |
|------------|-----|
| **ESLint** | Code Linting |
| **Prettier** | Code Formatting |
| **Husky** | Git Hooks |
| **Commitlint** | Commit Standards |

---

## 📁 Struttura del Progetto

```
LinkBay-CMS/
│
├── 📦 shared/                      # ⭐ COMPONENTI CONDIVISI
│   ├── components/                 # UI Components riutilizzabili
│   ├── utils/                      # Utility functions
│   ├── types/                      # TypeScript interfaces
│   └── styles/                     # Stili globali e temi
│
├── 🏠 landing/                     # Landing Page & Marketing
│   ├── src/
│   │   ├── components/            # Componenti specifici landing
│   │   ├── pages/                 # Pagine del sito
│   │   └── assets/                # Immagini e risorse
│   ├── package.json
│   └── vite.config.ts
│
├── 🏢 agency/                      # Dashboard Agenzie
│   ├── src/
│   │   ├── components/            # Componenti dashboard
│   │   │   ├── Layout/           # Layout e navigazione
│   │   │   └── UI/               # Componenti UI specifici
│   │   ├── pages/                # Pagine dashboard
│   │   └── hooks/                # Custom React hooks
│   ├── package.json
│   └── vite.config.ts
│
├── 👥 customer/                    # Portale Clienti
│   ├── src/
│   │   ├── components/            # Componenti portale cliente
│   │   ├── pages/                # Pagine cliente
│   │   └── services/             # API services
│   ├── package.json
│   └── vite.config.ts
│
├── 🌐 websites/                    # Gestione Siti Web
│   ├── src/
│   │   ├── components/            # CMS components
│   │   ├── editor/               # Content editor
│   │   └── templates/            # Template siti
│   ├── package.json
│   └── vite.config.ts
│
├── 🔗 backend/                     # Backend Services (WIP)
│   ├── src/
│   │   ├── api/                  # API routes
│   │   ├── services/             # Business logic
│   │   └── models/               # Data models
│   └── package.json
│
├── 📄 LICENSE                      # Licenza del progetto
├── 📖 README.md                    # Questo file
└── 🔧 package.json                 # Monorepo root
```

### 🌟 Shared Package - Il Cuore della Riutilizzabilità

Il package `shared/` contiene:

- ✅ **Components**: UI components utilizzabili da tutti i frontend
- ✅ **Types**: Interfacce TypeScript condivise
- ✅ **Utils**: Funzioni helper riutilizzabili
- ✅ **Styles**: Temi e stili base

---

## 🎨 Principi di Design

### 1. DRY (Don't Repeat Yourself)

**Problema**: Componenti duplicati tra frontend diversi.

**Soluzione**: 
- Componenti UI nel package `shared/components`
- Utility functions condivise in `shared/utils`
- Tipi TypeScript unificati in `shared/types`

**Esempio:**

```typescript
// ✅ CORRETTO: Componente condiviso
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

### 2. KISS (Keep It Simple, Stupid)

**Problema**: Interfacce complesse e difficili da usare.

**Soluzione**:
- Ogni frontend ha uno scopo specifico e chiaro
- Navigazione intuitiva
- Design minimale e pulito

### 3. Frontend Specializzati

**Ogni frontend serve un use case specifico**:

- 🏠 **Landing**: Marketing, presentazione, conversione
- 🏢 **Agency**: Gestione operativa, statistiche, amministrazione  
- 👥 **Customer**: Self-service, supporto, fatturazione
- 🌐 **Websites**: Content management, editing, pubblicazione

---

## ⚡ Funzionalità

### 🏠 Landing Frontend

- ✅ Homepage responsive con hero section
- ✅ Pagine About, Services, Contact
- ✅ Form di contatto integrato
- ✅ Design mobile-first

### 🏢 Agency Dashboard

- ✅ Dashboard con statistiche e metriche
- ✅ Gestione clienti e progetti
- ✅ Sistema di notifiche
- ✅ Layout sidebar responsive

### 👥 Customer Portal (WIP)

- 🚧 Profilo cliente personalizzabile
- 🚧 Gestione ordini e servizi
- 🚧 Sistema di supporto integrato
- 🚧 Fatturazione e pagamenti

### 🌐 Website Manager (WIP)

- 🚧 Editor di contenuti WYSIWYG
- 🚧 Gestione media e risorse
- 🚧 Template e temi personalizzabili
- 🚧 Pubblicazione e deployment

---

## 🚢 Deployment

### Development

```bash
# Start landing
cd landing && npm run dev

# Start agency dashboard  
cd agency && npm run dev

# Start customer portal
cd customer && npm run dev

# Start website manager
cd websites && npm run dev
```

### Production Build

```bash
# Build all frontends
npm run build:all

# Build specific frontend
cd agency && npm run build
cd landing && npm run build
```

### Environment Variables

Ogni frontend può avere le proprie variabili d'ambiente:

```bash
# agency/.env
VITE_API_URL=https://api.linkbay.com
VITE_APP_NAME=LinkBay Agency

# customer/.env  
VITE_API_URL=https://api.linkbay.com
VITE_APP_NAME=LinkBay Customer Portal
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

- 📧 Email: alessio@linkbay.com
- 🌐 Website: https://www.linkbay.com
- 📱 LinkedIn: [Alessio Quagliara](https://linkedin.com/in/alessio-quagliara)

---

<div align="center">

**Fatto con ❤️ da Alessio Quagliara**

[![Made with TypeScript](https://img.shields.io/badge/Made%20with-TypeScript-blue)](https://www.typescriptlang.org/)
[![Made with React](https://img.shields.io/badge/Made%20with-React-blue)](https://reactjs.org/)
[![Made with Tailwind](https://img.shields.io/badge/Made%20with-Tailwind-blue)](https://tailwindcss.com/)

</div>  
