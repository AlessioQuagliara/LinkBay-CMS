import React, { useState } from "react";

type JobPosition = {
  id: number;
  title: string;
  type: string;
  location: string;
  department: string;
  description: string;
  requirements: string[];
  benefits: string[];
  featured?: boolean;
};

const jobPositions: JobPosition[] = [
  {
    id: 1,
    title: "Senior Backend Developer",
    type: "Full-time",
    location: "Remoto",
    department: "Sviluppo",
    description: "Cerchiamo un esperto Node.js/TypeScript per evolvere la nostra architettura multitenant e scalare la piattaforma verso migliaia di agency partner.",
    requirements: [
      "5+ anni esperienza con Node.js e TypeScript",
      "Competenze solide in PostgreSQL e architetture multitenant",
      "Esperienza con Docker, CI/CD e cloud infrastructure",
      "Conoscenza di Stripe Connect e API di pagamento",
      "Mentalità product-oriented e attenzione alla sicurezza"
    ],
    benefits: [
      "RAL 50-70K + equity",
      "Workation 1 mese/anno",
      "Budget formazione annuale",
      "Hardware top di gamma",
      "Flessibilità oraria completa"
    ],
    featured: true
  },
  {
    id: 2,
    title: "Account Manager B2B",
    type: "Full-time",
    location: "Milano/Ibrido",
    department: "Vendite",
    description: "Gestisci il rapporto con le agency partner, aiuta nella crescita e fai da ponte tra i clienti e il team di sviluppo.",
    requirements: [
      "3+ anni esperienza in vendite B2B SaaS",
      "Capacità di gestire clienti enterprise",
      "Ottime doti comunicative e relazionali",
      "Conoscenza del mondo e-commerce/digital agency",
      "Inglese fluente"
    ],
    benefits: [
      "RAL 40-55K + commissioni",
      "Bonus performance trimestrali",
      "Budget benessere e formazione",
      "Smart working flessibile",
      "Partecipazione a fiere internazionali"
    ]
  },
  {
    id: 3,
    title: "DevOps Engineer",
    type: "Full-time",
    location: "Remoto",
    department: "Infrastruttura",
    description: "Gestisci e ottimizza la nostra infrastruttura cloud, automazione e monitoring per garantire massima affidabilità.",
    requirements: [
      "Esperienza con Docker, Kubernetes, Nginx",
      "Competenze in monitoring e alerting",
      "Conoscenza di Kamatera/AWS/GCP",
      "Scripting avanzato (Bash, Python)",
      "Mentalità security-first"
    ],
    benefits: [
      "RAL 45-65K + equity",
      "Certificazioni pagate",
      "Laboratorio hardware personale",
      "Conference budget illimitato",
      "Orario flessibile"
    ]
  },
  {
    id: 4,
    title: "Frontend Developer",
    type: "Full-time",
    location: "Remoto",
    department: "Sviluppo",
    description: "Sviluppa interfacce utente moderne e reattive per le dashboard multitenant di LinkBay-CMS.",
    requirements: [
      "3+ anni con React/TypeScript",
      "Esperienza con GraphQL/REST API",
      "Conoscenza di UI/UX principles",
      "Testing (Jest, Cypress)",
      "Passione per le performance"
    ],
    benefits: [
      "RAL 40-55K + equity",
      "Setup workstation personalizzato",
      "Flexible PTO",
      "Mental health days",
      "Growth path chiaro"
    ]
  },
  {
    id: 5,
    title: "Customer Success Specialist",
    type: "Full-time",
    location: "Ibrido",
    department: "Supporto",
    description: "Assisti le agency partner nell'onboarding e utilizzo avanzato della piattaforma.",
    requirements: [
      "2+ anni in customer success B2B",
      "Competenze tecniche di base",
      "Empatia e problem-solving",
      "Italiano e inglese fluenti",
      "Passione per l'e-commerce"
    ],
    benefits: [
      "RAL 35-45K + bonus",
      "Piano di crescita professionale",
      "Workshop continui",
      "Ambiente dinamico e young",
      "Responsabilità crescenti"
    ]
  }
];

const departments = ["Tutti", "Sviluppo", "Vendite", "Infrastruttura", "Supporto", "Marketing"];

export const WorkWithUsPage: React.FC = () => {
  const [selectedDepartment, setSelectedDepartment] = useState("Tutti");
  const [activeJob, setActiveJob] = useState<number | null>(null);

  const filteredJobs = jobPositions.filter(job => 
    selectedDepartment === "Tutti" || job.department === selectedDepartment
  );

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">
      {/* Hero Section */}
      <div className="relative bg-[#343a4D] text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,0 V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
            <path d="M0,0 V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" fill="currentColor"></path>
          </svg>
        </div>
        
        <section className="relative py-20 max-w-4xl mx-auto text-center px-4">
          <div className="inline-flex items-center mb-4 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold">
            <span className="mr-2">⚓</span> CAREERS AT LINKBAY-CMS
          </div>
          
          <h1 className="text-4xl md:text-5xl font-extrabold mb-6">
            Costruisci il <span className="text-[#ff5758]">Futuro</span> dell'E-commerce B2B
          </h1>
          
          <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-8">
            Unisciti alla nostra missione: democratizzare la potenza dell'e-commerce enterprise per agenzie e creator in tutto il mondo.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#open-positions" className="bg-[#ff5758] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors">
              🚀 Vedi le Posizioni Aperte
            </a>
            <a href="#why-join-us" className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
              ⚓ Perché Sceglierci
            </a>
          </div>
        </section>
      </div>

      {/* Why Join Us Section */}
      <section id="why-join-us" className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[#343a4D] mb-4">Perché Unirti alla Nostra Ciurma?</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Non siamo l'ennesima startup. Siamo i fornitori di arsenali tecnologici per chi conquista mercati.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="text-xl font-semibold text-[#343a4D] mb-3">Impatto Reale</h3>
            <p className="text-gray-600">
              Ogni feature che sviluppi aiuta centinaia di agenzie a crescere il loro business. Vedi il risultato del tuo lavoro moltiplicarsi.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-16 h-16 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🚀</span>
            </div>
            <h3 className="text-xl font-semibold text-[#343a4D] mb-3">Crescita Esponenziale</h3>
            <p className="text-gray-600">
              Equity per i primi membri del team. Siamo in fase early-stage con traction reale e ambizioni globali.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-16 h-16 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🌍</span>
            </div>
            <h3 className="text-xl font-semibold text-[#343a4D] mb-3">Work-Life Integration</h3>
            <p className="text-gray-600">
              Remoto first, orari flessibili, workation. Crediamo che il talento non abbia confini geografici.
            </p>
          </div>
        </div>
      </section>

      {/* Culture Values */}
      <section className="bg-[#343a4D] text-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">La Nostra Cultura</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-6">
              <span className="text-4xl mb-4 block">🏴‍☠️</span>
              <h3 className="text-lg font-semibold mb-2">Spirito Pionieristico</h3>
              <p className="text-blue-100 text-sm">Esploriamo territori inesplorati dell'e-commerce B2B</p>
            </div>
            
            <div className="text-center p-6">
              <span className="text-4xl mb-4 block">🤝</span>
              <h3 className="text-lg font-semibold mb-2">Trasparenza Radicale</h3>
              <p className="text-blue-100 text-sm">Condividiamo successi, fallimenti e metriche in tempo reale</p>
            </div>
            
            <div className="text-center p-6">
              <span className="text-4xl mb-4 block">🎨</span>
              <h3 className="text-lg font-semibold mb-2">Creatività Pragmatica</h3>
              <p className="text-blue-100 text-sm">Risolviamo problemi complessi con soluzioni eleganti</p>
            </div>
            
            <div className="text-center p-6">
              <span className="text-4xl mb-4 block">⚡</span>
              <h3 className="text-lg font-semibold mb-2">Velocità e Qualità</h3>
              <p className="text-blue-100 text-sm">Ship fast, ma mai a scapito della stabilità</p>
            </div>
          </div>
        </div>
      </section>

      {/* Open Positions */}
      <section id="open-positions" className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[#343a4D] mb-4">Posizioni Aperte</h2>
          <p className="text-lg text-gray-600">Unisciti al nostro equipaggio in crescita</p>
        </div>

        {/* Department Filters */}
        <div className="flex flex-wrap gap-2 justify-center mb-8">
          {departments.map(dept => (
            <button
              key={dept}
              onClick={() => setSelectedDepartment(dept)}
              className={`px-4 py-2 rounded-full font-semibold transition-colors ${
                selectedDepartment === dept
                  ? "bg-[#ff5758] text-white"
                  : "bg-white text-gray-700 border border-gray-300 hover:border-[#ff5758]"
              }`}
            >
              {dept}
            </button>
          ))}
        </div>

        {/* Jobs Grid */}
        <div className="space-y-6">
          {filteredJobs.map(job => (
            <div key={job.id} className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="p-6 cursor-pointer" onClick={() => setActiveJob(activeJob === job.id ? null : job.id)}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-[#343a4D]">{job.title}</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">{job.type}</span>
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">{job.location}</span>
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">{job.department}</span>
                      {job.featured && (
                        <span className="bg-[#ff5758] text-white px-2 py-1 rounded text-sm">✨ Featured</span>
                      )}
                    </div>
                  </div>
                  <span className={`transform transition-transform ${activeJob === job.id ? 'rotate-180' : ''}`}>
                    ▼
                  </span>
                </div>
                <p className="text-gray-600">{job.description}</p>
              </div>

              {/* Expanded Job Details */}
              {activeJob === job.id && (
                <div className="px-6 pb-6 border-t border-gray-200">
                  <div className="grid md:grid-cols-2 gap-8 mt-6">
                    <div>
                      <h4 className="font-semibold text-[#343a4D] mb-3">📋 Requisiti</h4>
                      <ul className="space-y-2">
                        {job.requirements.map((req, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-[#ff5758] mr-2 mt-1">•</span>
                            <span className="text-gray-700">{req}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-[#343a4D] mb-3">🎁 Benefit</h4>
                      <ul className="space-y-2">
                        {job.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-[#ff5758] mr-2 mt-1">•</span>
                            <span className="text-gray-700">{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex gap-4">
                    <a 
                      href={`mailto:careers@linkbay-cms.com?subject=Candidatura per ${job.title}`}
                      className="bg-[#ff5758] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors"
                    >
                      🚀 Candidati Ora
                    </a>
                    <button className="border border-[#343a4D] text-[#343a4D] px-6 py-2 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                      💾 Salva Posizione
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block">🔍</span>
            <h3 className="text-xl font-bold text-gray-700 mb-2">Nessuna posizione trovata</h3>
            <p className="text-gray-600 mb-6">Non ci sono posizioni aperte in questo dipartimento al momento</p>
            <a 
              href="mailto:careers@linkbay-cms.com"
              className="bg-[#343a4D] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#ff5758] transition-colors"
            >
              ✉️ Candidatura Spontanea
            </a>
          </div>
        )}
      </section>

      {/* Application Process */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-[#343a4D] text-center mb-12">Processo di Selezione</h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold">1</span>
              </div>
              <h3 className="font-semibold text-[#343a4D] mb-2">Application</h3>
              <p className="text-gray-600 text-sm">Invio CV e breve presentazione</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold">2</span>
              </div>
              <h3 className="font-semibold text-[#343a4D] mb-2">Screening</h3>
              <p className="text-gray-600 text-sm">Call conoscitiva di 30 minuti</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold">3</span>
              </div>
              <h3 className="font-semibold text-[#343a4D] mb-2">Technical Interview</h3>
              <p className="text-gray-600 text-sm">Challenge o pair programming</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold">4</span>
              </div>
              <h3 className="font-semibold text-[#343a4D] mb-2">Final Round</h3>
              <p className="text-gray-600 text-sm">Incontro con il fondatore</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Pronto a Salpare con Noi?</h2>
          <p className="mb-6 text-blue-100">Anche se non vedi la posizione perfetta, siamo sempre aperti a conoscere talenti eccezionali</p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="mailto:careers@linkbay-cms.com"
              className="px-6 py-3 bg-white text-[#343a4D] font-bold rounded-lg hover:bg-gray-100 transition-colors"
            >
              📨 Candidatura Spontanea
            </a>
            <a 
              href="mailto:alessio@linkbay-cms.com"
              className="px-6 py-3 border-2 border-white text-white font-bold rounded-lg hover:bg-white/10 transition-colors"
            >
              💬 Chatta con il Founder
            </a>
          </div>
        </div>
      </section>
    </main>
  );
};

export default WorkWithUsPage;