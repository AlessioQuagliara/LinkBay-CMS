import React from "react";
import { Link } from "react-router-dom";
import { useSEO } from "../hooks/useSimpleSEO";

type PricingPlan = {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  commission: string;
  cta: string;
  popular?: boolean;
  custom?: boolean;
  stores: string;
};

const plans: PricingPlan[] = [
  {
    name: "Agency Pro",
    price: "€299",
    period: "/mese",
    stores: "fino a 10 negozi white-label",
    description: "Perfetto per agenzie digitali che vogliono offrire e-commerce white-label senza lo sforzo tecnico.",
    features: [
      "Gestione fino a 10 negozi white-label",
      "Dashboard centrale multitenant",
      "Supporto prioritario",
      "White-labeling integrato completo",
      "Marketplace base incluso",
      "Setup domini e SSL automatico"
    ],
    commission: "Commissioni ridotte sul marketplace interno",
    cta: "Prova gratis 14 giorni"
  },
  {
    name: "Agency Scale",
    price: "€999",
    period: "/mese",
    stores: "fino a 50 negozi white-label",
    description: "Per agenzie strutturate che gestiscono portfolio clienti ampio con funzionalità enterprise.",
    features: [
      "Gestione fino a 50 negozi white-label",
      "Funzionalità avanzate WMS e marketplace",
      "Supporto dedicato e SLA",
      "Commissioni ridotte sul marketplace interno",
      "RBAC avanzato e audit logging",
      "Backup automatizzati e monitoring"
    ],
    commission: "Commissioni ulteriormente ridotte + marketplace fee minime",
    cta: "Demo personalizzata",
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    stores: "negozi illimitati",
    description: "Soluzione su misura per software house e brand multi-nazionale con esigenze specifiche.",
    features: [
      "Negozi illimitati white-label",
      "Data residency EU/US/Svizzera",
      "Account manager dedicato",
      "SLA 99.9% garantito",
      "Marketplace privato custom",
      "Integrazioni personalizzate e compliance"
    ],
    commission: "Revenue sharing personalizzato",
    cta: "Contatta sales",
    custom: true
  }
];

export const PricingPage: React.FC = () => {
  // SEO per la pagina dei prezzi
  useSEO({
    title: "Prezzi",
    description: "Scegli il piano LinkBay CMS perfetto per la tua agenzia. Piani scalabili da startup a enterprise con commissioni trasparenti.",
    keywords: "prezzi cms, piani agenzia, costi gestione siti, tariffe multi-tenant, commissioni"
  });

  return (
  <main className="min-h-screen bg-gradient-to-b from-white to-blue-50 pb-8">
    {/* Wave Header Section */}
    <div className="relative bg-[#343a4D] text-white overflow-hidden">
      <div className="absolute inset-0 opacity-10">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
          <path d="M0,0 V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
          <path d="M0,0 V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" fill="currentColor"></path>
          <path d="M0,0 V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" fill="currentColor"></path>
        </svg>
      </div>
      
      <section className="relative py-16 max-w-4xl mx-auto text-center px-4">
        <div className="inline-flex items-center mb-4 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold">
          <span className="mr-2">⚓</span> PIATTAFORMA B2B PER AGENZIE
        </div>
        
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
          L'<span className="text-[#ff5758]">Arsenale</span> Tecnologico per le Tue Navi E-commerce
        </h1>
        
        <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-6">
          "Attracco il tuo sogno, poi lo faccio salpare" - Forniamo l'infrastruttura, tu conquisti il mercato.
        </p>
        
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 max-w-2xl mx-auto">
          <p className="text-lg mb-2"><strong>Niente Freemium</strong> - Solo piani verticali B2B</p>
          <p className="text-blue-100">Prova gratuita 14 giorni - Nessuna carta di credito richiesta</p>
        </div>
      </section>
    </div>

    {/* Pricing Cards Section */}
    <section className="max-w-7xl mx-auto px-4 py-16 -mt-8">
      <div className="grid md:grid-cols-3 gap-8">
        {plans.map((plan, i) => (
          <div key={plan.name} className={`relative rounded-2xl border-2 p-8 pt-16 shadow-xl transition-all duration-300 hover:scale-105
            ${plan.popular ? "border-[#ff5758] bg-gradient-to-b from-white to-red-50 transform scale-105" : "border-gray-200 bg-white"}
            ${plan.custom ? "border-dashed bg-gradient-to-b from-white to-blue-50" : ""}
          `}>
            
            {/* Popular Badge */}
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-[#ff5758] text-white px-6 py-2 rounded-full font-bold text-sm flex items-center">
                  <span className="mr-2">⭐</span> PIÙ SCELTO
                </div>
              </div>
            )}
            
            {/* Enterprise Badge */}
            {plan.custom && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-[#343a4D] text-white px-6 py-2 rounded-full font-bold text-sm">
                  ⚓ ENTERPRISE
                </div>
              </div>
            )}

            {/* Plan Header */}
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-[#343a4D] mb-2">{plan.name}</h2>
              <div className="flex items-end justify-center mb-2">
                <span className="text-4xl font-bold text-[#343a4D]">{plan.price}</span>
                <span className="text-gray-600 ml-1 text-xl">{plan.period}</span>
              </div>
              <div className="bg-[#343a4D] text-white px-3 py-1 rounded-full text-sm font-semibold inline-block">
                {plan.stores}
              </div>
            </div>

            <p className="text-gray-700 mb-6 text-center">{plan.description}</p>
            
            {/* Features List */}
            <ul className="mb-6 space-y-3">
              {plan.features.map((f, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#ff5758] mr-3 mt-1">⚓</span>
                  <span className="text-gray-700">{f}</span>
                </li>
              ))}
            </ul>

            {/* Commission Info */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <span className="block text-sm text-gray-500 font-semibold">MODELLO COMMISSIONI:</span>
              <span className="block font-semibold text-[#343a4D]">{plan.commission}</span>
            </div>

            {/* CTA Button */}
            {plan.custom ? (
              <a href="mailto:sales@linkbay-cms.com" className="w-full block py-3 px-6 rounded-lg font-bold bg-[#343a4D] text-white hover:bg-[#ff5758] transition-colors text-center">
                ⚓ {plan.cta}
              </a>
            ) : (
              <Link 
                to={plan.popular ? "/register" : "/contact"} 
                className={`w-full block py-3 px-6 rounded-lg font-bold transition-colors text-center 
                  ${plan.popular ? "bg-[#ff5758] text-white hover:bg-[#e04e4f]" : "bg-[#343a4D] text-white hover:bg-[#ff5758]"}`}
              >
                {plan.popular ? "🚀 " : "⚓ "}{plan.cta}
              </Link>
            )}
          </div>
        ))}
      </div>
    </section>

    {/* Value Proposition Section */}
    <section className="max-w-4xl mx-auto px-4 py-12 text-center">
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
        <h2 className="text-2xl font-bold text-[#343a4D] mb-6">Cosa ottieni con LinkBay-CMS?</h2>
        
        <div className="grid md:grid-cols-2 gap-6 text-left">
          <div className="flex items-start">
            <span className="text-[#ff5758] mr-3 text-xl">🌊</span>
            <div>
              <h3 className="font-semibold text-[#343a4D]">Architettura Multitenant Nativa</h3>
              <p className="text-gray-600 text-sm">Gestisci 10 o 10.000 store dalla stessa dashboard</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <span className="text-[#ff5758] mr-3 text-xl">⚡</span>
            <div>
              <h3 className="font-semibold text-[#343a4D]">Automazione Completa</h3>
              <p className="text-gray-600 text-sm">Domini, SSL, deployment e aggiornamenti automatici</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <span className="text-[#ff5758] mr-3 text-xl">🎯</span>
            <div>
              <h3 className="font-semibold text-[#343a4D]">White-labeling Integrato</h3>
              <p className="text-gray-600 text-sm">Marchia la piattaforma come tua verso i clienti finali</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <span className="text-[#ff5758] mr-3 text-xl">💼</span>
            <div>
              <h3 className="font-semibold text-[#343a4D]">Modello Revenue Sharing</h3>
              <p className="text-gray-600 text-sm">Guadagna con le commissioni sui marketplace dei tuoi clienti</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* Final CTA Section */}
    <section className="max-w-3xl mx-auto px-4 py-12 text-center">
      <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-8 text-white">
        <h2 className="text-2xl font-bold mb-4">Pronto a Salpare?</h2>
        <p className="mb-6 text-blue-100">Unisciti alle agenzie che già navigano con LinkBay-CMS</p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="http://localhost:3003/register" target="_blank" rel="noopener noreferrer" className="px-8 py-3 font-bold rounded-lg bg-white text-[#343a4D] hover:bg-gray-100 transition-colors">
            🚀 Inizia la Prova Gratuita
          </a>
          <Link to="/demo" className="px-8 py-3 font-bold rounded-lg border-2 border-white text-white hover:bg-white/10 transition-colors">
            ⚓ Richiedi una Demo
          </Link>
        </div>
        
        <p className="text-sm text-blue-100 mt-4">
          <strong>Nessun impegno</strong> - Upgrade/downgrade flessibile in qualsiasi momento
        </p>
      </div>
    </section>
  </main>
  );
};

export default PricingPage;