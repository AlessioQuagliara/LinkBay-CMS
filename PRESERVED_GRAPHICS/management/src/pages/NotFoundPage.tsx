import React from "react";
import { Link } from "react-router-dom";
import { Compass, Ship, Anchor, Waves, Navigation } from "lucide-react";
import { useSEO } from "../hooks/useSimpleSEO";

export const NotFoundPage: React.FC = () => {
  // SEO per 404 (con noindex)
  useSEO({
    title: "Pagina Non Trovata - 404",
    description: "La pagina richiesta non è stata trovata. Torna alla homepage di LinkBay CMS per esplorare la nostra piattaforma per agenzie.",
    keywords: "404 not found, pagina non trovata, errore navigazione"
  });

  return (
  <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-50 flex items-center justify-center relative overflow-hidden">
    {/* Onde decorative */}
    <div className="absolute top-0 left-0 w-full opacity-10">
      <Waves className="w-full h-32 text-[#343a4D]" />
    </div>
    
    <div className="absolute bottom-0 left-0 w-full opacity-5 rotate-180">
      <Waves className="w-full h-32 text-[#343a4D]" />
    </div>

    {/* Elementi fluttuanti */}
    <div className="absolute top-1/4 left-1/4 opacity-5 animate-float">
      <Ship className="w-24 h-24 text-[#343a4D]" />
    </div>
    <div className="absolute bottom-1/3 right-1/4 opacity-5 animate-float-delayed">
      <Anchor className="w-20 h-20 text-[#343a4D]" />
    </div>
    <div className="absolute top-1/3 right-1/3 opacity-5 animate-float-slow">
      <Compass className="w-16 h-16 text-[#343a4D]" />
    </div>

    <main className="max-w-2xl mx-auto text-center px-4 sm:px-6 lg:px-8 relative z-10">
      {/* Icona centrale */}
      <div className="relative mb-8">
        <div className="relative inline-block">
          <div className="w-40 h-40 bg-[#ff5758] rounded-full flex items-center justify-center shadow-2xl mx-auto mb-6">
            <Navigation className="w-20 h-20 text-white" />
          </div>
          <div className="absolute -top-4 -right-4 bg-[#343a4D] text-white rounded-full w-16 h-16 flex items-center justify-center shadow-lg">
            <span className="text-2xl font-bold font-[Electrolize]">404</span>
          </div>
        </div>
      </div>

      {/* Contenuto testuale */}
      <div className="mb-8">
        <h1 className="text-5xl md:text-6xl font-bold text-[#343a4D] mb-4 font-[Electrolize]">
          Rotta Interrotta
        </h1>
        
        <div className="w-24 h-1 bg-[#ff5758] mx-auto mb-6"></div>
        
        <p className="text-xl text-[#343a4D] mb-6 leading-relaxed">
          La pagina che stai cercando ha preso il largo e non è più raggiungibile.
        </p>
        
        <p className="text-lg text-gray-600 max-w-lg mx-auto mb-8">
          Forse stavi cercando una funzionalità dell'arsenale LinkBay-CMS che verrà 
          pubblicata a breve, oppure il link che hai usato non è più attivo.
        </p>
      </div>

      {/* Azioni principali */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <Link
          to="/"
          className="inline-flex items-center justify-center px-8 py-4 bg-[#ff5758] text-white font-semibold rounded-xl hover:bg-[#e04e4e] shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 group"
        >
          <Ship className="w-5 h-5 mr-2 group-hover:animate-bounce" />
          Torna alla Home
        </Link>
        
        <Link
          to="/features"
          className="inline-flex items-center justify-center px-8 py-4 border-2 border-[#343a4D] text-[#343a4D] font-semibold rounded-xl hover:bg-[#343a4D] hover:text-white transition-all duration-300 group"
        >
          <Compass className="w-5 h-5 mr-2" />
          Esplora Funzionalità
        </Link>
      </div>

      {/* Link rapidi */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 mb-8">
        <h3 className="font-semibold text-[#343a4D] mb-4 flex items-center justify-center">
          <Anchor className="w-5 h-5 mr-2 text-[#ff5758]" />
          Navigazione Rapida
        </h3>
        <div className="flex flex-wrap justify-center gap-4">
          <Link to="/pricing" className="text-[#343a4D] hover:text-[#ff5758] transition-colors duration-300 text-sm">
            Pricing
          </Link>
          <Link to="/about" className="text-[#343a4D] hover:text-[#ff5758] transition-colors duration-300 text-sm">
            Chi Siamo
          </Link>
          <Link to="/contact" className="text-[#343a4D] hover:text-[#ff5758] transition-colors duration-300 text-sm">
            Contatti
          </Link>
          <Link to="/blog" className="text-[#343a4D] hover:text-[#ff5758] transition-colors duration-300 text-sm">
            Blog
          </Link>
        </div>
      </div>

      {/* Supporto */}
      <div className="text-gray-600">
        <p className="mb-2">Se pensi che questo sia un errore, siamo qui per aiutarti</p>
        <a 
          href="mailto:support@linkbay-cms.com" 
          className="inline-flex items-center text-[#ff5758] hover:text-[#e04e4e] font-semibold transition-colors duration-300"
        >
          <span className="w-2 h-2 bg-[#ff5758] rounded-full mr-2 animate-pulse"></span>
          support@linkbay-cms.com
        </a>
      </div>

      {/* Codice di errore stilizzato */}
      <div className="mt-12 opacity-20">
        <code className="text-[#343a4D] font-mono text-sm">
          ERROR 404: DESTINATION_NOT_FOUND • LAT: 44.7128° N • LONG: 74.0060° W • COURSE: HOME
        </code>
      </div>
    </main>

  </div>
  );
};

export default NotFoundPage;