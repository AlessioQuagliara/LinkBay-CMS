import React from "react";
import { Link } from "react-router-dom";
import { useSEO } from "../hooks/useSimpleSEO";

const features = [
  {
    title: "Multitenancy Nativa",
    desc: "Architettura schema-per-tenant con isolamento totale dei dati. Gestione centralizzata di agenzie e clienti con workspace separati, domini dedicati e branding indipendente.",
    icon: "🌐",
    benefits: ["Isolamento dati garantito", "Gestione centralizzata", "Branding indipendente"]
  },
  {
    title: "Automazione Dominio & SSL",
    desc: "Provisioning automatico di domini, sottodomini, DNS e certificati SSL Let's Encrypt. Zero configurazione manuale, massima sicurezza out-of-the-box.",
    icon: "🔒",
    benefits: ["Configurazione automatica", "SSL gratuito", "Zero downtime"]
  },
  {
    title: "Marketplace Estensioni",
    desc: "Ecosistema completo di plugin, temi e componenti. Marketplace interno per monetizzare e distribuire estensioni con versioning e aggiornamenti automatici.",
    icon: "🧩",
    benefits: ["Monetizzazione extra", "Aggiornamenti automatici", "Community driven"]
  },
  {
    title: "Editor Drag&Drop Avanzato",
    desc: "GrapesJS integrato con editing visuale avanzato. Supporto per blocchi personalizzati, CSS custom e preview in tempo reale senza limiti creativi.",
    icon: "🧑‍💻",
    benefits: ["Zero coding required", "Template personalizzabili", "Preview live"]
  },
  {
    title: "API REST/GraphQL",
    desc: "Endpoint sicuri e documentati per integrazioni avanzate. Supporto per webhook, automazioni e sincronizzazione con sistemi esterni.",
    icon: "🔗",
    benefits: ["Integrazioni illimitate", "Documentazione completa", "Webhook real-time"]
  },
  {
    title: "Sicurezza Enterprise",
    desc: "Row Level Security PostgreSQL, RBAC granulare, audit log completo, backup automatici, 2FA e compliance GDPR nativa con hosting EU.",
    icon: "🔐",
    benefits: ["GDPR compliant", "Backup automatici", "Audit completo"]
  },
  {
    title: "Revenue Sharing Integrato",
    desc: "Stripe Connect nativo per commissioni multi-livello. Split pagamenti automatico, fee configurabili e reporting dettagliato per marketplace.",
    icon: "💸",
    benefits: ["Commissioni multi-livello", "Reporting avanzato", "Payout automatici"]
  },
  {
    title: "White-label Completo",
    desc: "Branding 100% personalizzabile: loghi, colori, domini, email template. Il cliente finale vede solo il tuo brand, non il nostro.",
    icon: "🎨",
    benefits: ["Branding totale", "Email personalizzate", "Dashboard white-label"]
  },
  {
    title: "Deployment Automatizzato",
    desc: "CI/CD integrata con GitHub Actions. Deployment one-click, rollback automatico e environment multipli (dev, staging, production).",
    icon: "🚀",
    benefits: ["Deploy one-click", "Rollback automatico", "Multi-environment"]
  },
  {
    title: "Analytics Avanzate",
    desc: "Dashboard analitiche integrate per performance e-commerce. Tracking conversioni, analisi comportamento utente e report personalizzabili.",
    icon: "📊",
    benefits: ["Conversion tracking", "Analytics real-time", "Report custom"]
  },
  {
    title: "Supporto Multi-lingua",
    desc: "Internazionalizzazione nativa per negozi multilingua. Gestione contenuti localizzati e supporto per valute multiple.",
    icon: "🌍",
    benefits: ["Localizzazione avanzata", "Multi-currency", "Contenuti locali"]
  }
];

const techStack = [
  { name: "TypeScript Full-Stack", category: "Linguaggio" },
  { name: "Node.js + Express", category: "Backend" },
  { name: "PostgreSQL RLS", category: "Database" },
  { name: "React + Vite", category: "Frontend" },
  { name: "Tailwind CSS 3.4", category: "Styling" },
  { name: "Docker Containers", category: "Infrastruttura" },
  { name: "Redis Cache", category: "Performance" },
  { name: "Stripe Connect", category: "Pagamenti" },
  { name: "Nginx + Certbot", category: "Web Server" },
  { name: "GitHub Actions", category: "CI/CD" },
  { name: "JWT Authentication", category: "Sicurezza" },
  { name: "Socket.IO", category: "Real-time" }
];

export const FeaturesPage: React.FC = () => {
  // SEO dinamica per la pagina Features
  useSEO({
    title: "Funzionalità",
    description: "Scopri tutte le funzionalità avanzate di LinkBay CMS: gestione multi-tenant, dashboard centralizzata, editor drag-and-drop e molto altro.",
    keywords: "funzionalità cms, multi-tenant, dashboard, editor, gestione siti"
  });

  return (
  <main className=" min-h-screen overflow-hidden">
    
      {/* Onde decorative */}
      <div className="left-0 w-full overflow-hidden" id="top">
        <svg 
          viewBox="0 0 1200 120" 
          preserveAspectRatio="none" 
          className="relative w-full h-16 md:h-24"
        >
          <path 
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" 
            opacity=".25" 
            className="fill-red-500"
          ></path>
          <path 
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" 
            opacity=".5" 
            className="fill-red-500"
          ></path>
          <path 
            d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" 
            className="fill-red-600"
          ></path>
        </svg>
      </div>


    <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-16">

      <div className="max-w-6xl mx-auto px-4 text-center relative z-10">
        <div className="mb-6">
          <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
            Tecnologia Enterprise
          </span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Funzionalità Senza Compromessi
        </h1>
        
        <p className="text-xl text-gray-700 leading-relaxed max-w-4xl mx-auto">
          <b>Automatizza, personalizza, monetizza.</b> Con LinkBay-CMS, hai non un semplice site builder, 
          ma <span className="text-red-600 font-semibold">un'infrastruttura enterprise pensata per agenzie che vogliono scalare</span> 
          senza limiti tecnici, gestendo decine, centinaia o migliaia di e-commerce.
        </p>
      </div>
    </section>

    {/* Features Grid */}
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Tutto ciò che ti serve per dominare il mercato
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Feature progettate specificamente per le esigenze delle agenzie digitali e software house
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={feature.title}
              className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 border border-gray-200 hover:border-red-200 hover:shadow-xl transition-all duration-300 group"
            >
              <div className="flex items-start space-x-4">
                <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <span className="text-3xl">{feature.icon}</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed mb-4">{feature.desc}</p>
                  
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, idx) => (
                      <li key={idx} className="flex items-center text-sm text-gray-500">
                        <div className="w-2 h-2 bg-red-400 rounded-full mr-3"></div>
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Tech Stack Section */}
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Tech Stack di Nuova Generazione
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Costruito con le tecnologie più moderne e performanti del mercato
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {techStack.map((tech, index) => (
            <div 
              key={tech.name}
              className="bg-white rounded-xl p-6 text-center border border-gray-200 hover:shadow-lg transition-all duration-300"
            >
              <div className="mb-3">
                <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                  {tech.category}
                </span>
              </div>
              <h4 className="font-bold text-gray-900 text-lg">{tech.name}</h4>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <div className="bg-white rounded-2xl p-8 border border-gray-200 max-w-2xl mx-auto">
            <div className="text-6xl mb-4">⚡</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Performance Ottimizzate</h3>
            <p className="text-gray-600 mb-6">
              Architettura microservices, caching avanzato e load balancing per garantire 
              performance enterprise anche sotto carichi elevati.
            </p>
            <div className="flex justify-center space-x-4 text-sm text-gray-500">
              <span>✅ Response time {'<'} 200ms</span>
              <span>✅ Uptime 99.9%</span>
              <span>✅ Scalabilità orizzontale</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* Architecture Overview */}
    <section className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Architettura Multitenant Nativa
            </h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Il cuore di LinkBay-CMS: un'architettura "schema-per-tenant" che garantisce 
              isolamento totale dei dati, sicurezza enterprise e scalabilità illimitata.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>Isolamento dati:</b> Ogni tenant ha il proprio schema PostgreSQL</span>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>White-label nativo:</b> Branding completo per ogni agenzia</span>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>Scalabilità verticale:</b> Aggiungi moduli enterprise quando serve</span>
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-red-50 to-white rounded-2xl p-8 border border-red-100">
            <div className="text-center">
              <div className="text-6xl mb-4">🏗️</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Design Pattern Solidi</h3>
              <p className="text-gray-700 mb-6">
                Basato su best practices enterprise: microservices, event-driven architecture 
                e separazione chiara dei concern.
              </p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-white rounded-lg p-3 border">Middleware Layer</div>
                <div className="bg-white rounded-lg p-3 border">Service Layer</div>
                <div className="bg-white rounded-lg p-3 border">Data Access Layer</div>
                <div className="bg-white rounded-lg p-3 border">API Gateway</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* CTA Finale con Onde */}

    <section className="relative bg-gradient-to-r from-gray-900 to-red-900 text-white py-20">
      {/* Onde in alto */}
      <div className="absolute top-0 left-0 w-full overflow-hidden">
        <svg 
          viewBox="0 0 1200 120" 
          preserveAspectRatio="none" 
          className="relative w-full h-16 md:h-24"
        >
          <path 
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" 
            opacity=".25" 
            className="fill-white"
          ></path>
          <path 
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" 
            opacity=".5" 
            className="fill-white"
          ></path>
          <path 
            d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" 
            className="fill-white"
          ></path>
        </svg>
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <h2 className="text-3xl md:text-4xl font-bold mb-6">
          Pronto a Rivoluzionare il Tuo Business?
        </h2>
        <p className="text-xl mb-8 opacity-90">
          Unisciti alle agenzie che stanno già scalando con LinkBay-CMS
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/pricing"
            className="px-8 py-4 text-lg font-bold rounded-xl bg-white text-red-600 hover:bg-gray-100 shadow-lg transition-all duration-300"
          >
            Scopri i Piani Agency
          </Link>
          <Link
            to="/contact"
            className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-white text-white hover:bg-white hover:text-red-600 transition-all duration-300"
          >
            Contattaci
          </Link>
        </div>
        
        <div className="mt-8 text-sm opacity-75">
          <em>Il moltiplicatore di forza per i creatori di e-commerce</em>
        </div>
      </div>

      {/* Onde in basso */}
      <div className="absolute bottom-0 left-0 w-full overflow-hidden rotate-180">
        <svg 
          viewBox="0 0 1200 120" 
          preserveAspectRatio="none" 
          className="relative w-full h-16 md:h-24"
        >
          <path 
            d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" 
            opacity=".25" 
            className="fill-[#343a4D]"
          ></path>
          <path 
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" 
            opacity=".5" 
            className="fill-[#343a4D]"
          ></path>
          <path 
            d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" 
            className="fill-[#343a4D]"
          ></path>
        </svg>
      </div>

    </section>
  </main>
  );
};

export default FeaturesPage;