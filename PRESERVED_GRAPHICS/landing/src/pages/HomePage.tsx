import React from "react";
import { Link } from "react-router-dom";
import { useSEO } from "../hooks/useSimpleSEO";

export const HomePage: React.FC = () => {
  // SEO dinamica - si aggiorna automaticamente quando la pagina viene caricata
  useSEO({
    title: "Home",
    description: "LinkBay CMS è la piattaforma completa per agenzie web. Gestisci tutti i siti dei tuoi clienti da un'unica dashboard professionale.",
    keywords: "cms, agenzia web, gestione siti, multi-tenant, dashboard, web agency"
  });

  return (
  <main className="min-h-screen overflow-hidden">

      {/* Onde decorative */}
      <div className="left-0 w-full overflow-hidden">
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

    {/* Hero Section con Onde */}
    <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-32">
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">


        <div className="mb-8">
          <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
            Piattaforma B2B Multitenant
          </span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 mb-6 leading-tight font-[Electrolize]">
          LinkBay<span className="text-red-600">-CMS</span>
        </h1>
        
        <p className="text-2xl md:text-3xl text-gray-700 mb-2 font-light">
          L'<span className="text-red-600 font-semibold">Arms Dealer</span> per Agenzie e Software House
        </p>
        
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
          <b>Forniamo l'arsenale, tu conquisti il mercato.</b> La piattaforma B2B per gestire infiniti 
          e-commerce white-label con controllo totale, risparmiando tempo e scalando senza limiti.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            to="/pricing"
            className="px-8 py-4 text-lg font-bold rounded-xl bg-red-600 text-white hover:bg-red-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
          >
            Prova gratuita 14 giorni – Agency Pro
          </Link>
          <Link
            to="/demo"
            className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-gray-300 text-gray-700 hover:border-red-600 hover:text-red-600 transition-all duration-300"
          >
            Richiedi una Demo
          </Link>
        </div>
        
        <div className="mt-6 text-gray-500 font-mono text-sm italic font-[Electrolize]">
          "I dock your dream, then set it sail"
        </div>
      </div>
    </section>

    {/* Statistiche */}
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-red-600">10k+</div>
            <div className="text-gray-600">Negozi gestibili</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">0</div>
            <div className="text-gray-600">Limiti di crescita</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">100%</div>
            <div className="text-gray-600">White-label</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">∞</div>
            <div className="text-gray-600">Scalabilità</div>
          </div>
        </div>
      </div>
    </section>

    {/* Filosofia */}
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Filosofia: Tre Pilastri per Agenzie in Crescita
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Costruiamo relazioni di partnership basate su valori concreti e crescita reciproca
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-6">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Potenza senza Peso</h3>
            <p className="text-gray-600 leading-relaxed">
              Infrastruttura enterprise robusta e scalabile senza le complicazioni di gestione. 
              La complessità tecnica è nostra, il controllo strategico è tuo.
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-6">
              <span className="text-2xl">🚀</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Crescita Condivisa</h3>
            <p className="text-gray-600 leading-relaxed">
              Il tuo successo è il nostro. Modello di revenue sharing che premia la tua crescita. 
              Quando tu vinci, vinciamo insieme.
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-6">
              <span className="text-2xl">🛡️</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Fiducia come Fondamento</h3>
            <p className="text-gray-600 leading-relaxed">
              Base solida e sicura per il tuo impero digitale. Sicurezza, trasparenza e stabilità 
              sono i pilastri non negoziabili del nostro rapporto.
            </p>
          </div>
        </div>
      </div>
    </section>

    {/* Target Client */}
    <section className="py-20 bg-gray-50">

      <div className="max-w-7xl mx-auto px-4">

        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            A Chi Si Rivolge LinkBay-CMS
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            La soluzione perfetta per realtà che gestiscono multiple identità digitali
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🏢</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Web Agency</h3>
            <p className="text-gray-600">
              Che vogliono offrire e-commerce white-label senza i costi e la complessità 
              dello sviluppo e mantenimento di una piattaforma proprietaria.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">💻</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Software House & SaaS</h3>
            <p className="text-gray-600">
              Che cercano un componente pronto all'uso per aggiungere funzionalità 
              e-commerce multitenant alle loro offerte esistenti.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🌟</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Brand Multipli</h3>
            <p className="text-gray-600">
              Creator e brand affermati che operano in multiple nicchie e necessitano 
              di gestire identità separate con logiche comuni.
            </p>
          </div>
        </div>
      </div>
    </section>

    {/* Vantaggi Tecnici */}
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              Tecnologia che Fa la Differenza
            </h2>
            <ul className="space-y-4">
              <li className="flex items-start">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-red-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>Architettura Multitenant Nativa:</b> Isolamento totale tra clienti</span>
              </li>
              <li className="flex items-start">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-red-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>White-Label Completo:</b> La piattaforma diventa tua</span>
              </li>
              <li className="flex items-start">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-red-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>Automazione Domini/SSL:</b> Configurazione in un click</span>
              </li>
              <li className="flex items-start">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-red-600 text-sm">✓</span>
                </div>
                <span className="text-gray-700"><b>Marketplace Interno:</b> Monetizza con temi e plugin</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-gradient-to-br from-red-50 to-white rounded-2xl p-8 border border-red-100">
            <div className="text-center">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Posizionamento Unico</h3>
              <p className="text-gray-700 mb-6">
                Il primo CMS <b>nativo multitenant</b> con revenue-sharing integrato, 
                progettato esclusivamente per il mercato B2B.
              </p>
              <p className="text-lg font-semibold text-red-600">
                Gestisci 10 o 10.000 e-commerce, nessuno ti limita.
              </p>
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

export default HomePage;