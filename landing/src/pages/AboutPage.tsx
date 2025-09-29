import React from "react";
import { Link } from "react-router-dom";
import { useSEO } from "../hooks/useSimpleSEO";

export const AboutPage: React.FC = () => {
  // SEO per la pagina About
  useSEO({
    title: "Chi Siamo",
    description: "Scopri la storia di LinkBay CMS, il team e la missione di rivoluzionare la gestione dei siti web per le agenzie digitali.",
    keywords: "about linkbay, team cms, storia agenzia web, missione digitale, chi siamo"
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


    <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-16">

      <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
        <div className="mb-6">
          <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
            La Nostra Storia
          </span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Chi Siamo
        </h1>
        
        <div className="text-red-600 font-semibold italic text-xl mb-6">
          Il moltiplicatore di forza per i creatori di e-commerce
        </div>
        
        <p className="text-lg text-gray-700 leading-relaxed max-w-3xl mx-auto">
          LinkBay-CMS nasce per rivoluzionare la gestione e la <b className="text-red-600">scalabilità</b> di progetti web <b>multi-tenant</b>, 
          offrendo un'infrastruttura robusta alle agenzie, software house e brand che devono gestire 
          decine o centinaia di marketplace o e-commerce white-label.
        </p>
      </div>
    </section>

    {/* Visione */}
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mb-6">
              <span className="text-3xl">🎯</span>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">La Nostra Visione</h2>
            <p className="text-gray-700 text-lg leading-relaxed mb-6">
              Crediamo che il ruolo dell'agenzia moderna sia quello di <b>creare valore</b> per i propri clienti, 
              non di gestire l'infrastruttura tecnica. Per questo LinkBay vuole essere il "braccio armato" di chi costruisce.
            </p>
            <div className="bg-red-50 border-l-4 border-red-600 pl-4 py-3 mb-6">
              <p className="text-red-800 font-semibold italic">
                "Tu ti concentri sui progetti e sulla crescita, al resto pensa la piattaforma"
              </p>
            </div>
            <p className="text-gray-700">
              In LinkBay il successo è condiviso: <span className="font-semibold text-red-600">crescita, ricavi e partnership sono allineati e trasparenti</span>.
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-200">
            <div className="text-center">
              <div className="text-6xl mb-4">⚡</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Filosofia Operativa</h3>
              <ul className="space-y-4 text-left">
                <li className="flex items-start">
                  <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                    <span className="text-red-600 text-sm">✓</span>
                  </div>
                  <span className="text-gray-700"><b>Partnership reale:</b> meno fornitori, più alleati</span>
                </li>
                <li className="flex items-start">
                  <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                    <span className="text-red-600 text-sm">✓</span>
                  </div>
                  <span className="text-gray-700"><b>Massima affidabilità:</b> sicurezza, compliance, trasparenza</span>
                </li>
                <li className="flex items-start">
                  <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                    <span className="text-red-600 text-sm">✓</span>
                  </div>
                  <span className="text-gray-700"><b>Innovazione continua:</b> progettato per scalare e durare</span>
                </li>
                <li className="flex items-start">
                  <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                    <span className="text-red-600 text-sm">✓</span>
                  </div>
                  <span className="text-gray-700"><b>Focus SaaS B2B:</b> niente entry-level, nessun compromesso</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* Founder */}
    <section className="py-16 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Chi C'è Dietro</h2>
          <p className="text-lg text-gray-600">La mente e il cuore del progetto</p>
        </div>
        
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200 max-w-2xl mx-auto">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-full flex items-center justify-center">
              <span className="text-3xl">👨‍💻</span>
            </div>
            <div className="text-center md:text-left">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Alessio Quagliara</h3>
              <p className="text-red-600 font-semibold mb-3">Founder & Full-Stack Developer</p>
              <p className="text-gray-700 leading-relaxed">
                Sono l'unico sviluppatore e proprietario di LinkBay-CMS. Il progetto nasce dalla mia esperienza 
                nel mondo SaaS, sviluppo web e gestione di sistemi scalabili. La mia filosofia è 
                <span className="font-semibold text-red-600"> indipendenza, velocità e innovazione senza compromessi</span>.
              </p>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-gray-600 text-sm italic text-center">
              "Tutto il codice e la progettazione sono interamente curati da me, con attenzione maniacale 
              a sicurezza, performance ed evolvibilità. Credo nella trasparenza totale e nel costruire 
              relazioni di partnership durature."
            </p>
          </div>
        </div>
      </div>
    </section>

    {/* Valori */}
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">I Nostri Valori Fondamentali</h2>
          <p className="text-lg text-gray-600">I principi che guidano ogni nostra decisione</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🛡️</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Trasparenza Radicale</h3>
            <p className="text-gray-600">
              Niente clausole nascoste, niente sorprese. Condividiamo metriche, roadmap e decisioni 
              con i nostri partner.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🚀</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Innovazione Pratica</h3>
            <p className="text-gray-600">
              Implementiamo solo tecnologie che risolvono problemi reali. Niente feature bloat, 
              solo valore concreto.
            </p>
          </div>
          
          <div className="text-center p-6">
            <div className="w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🤝</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Crescita Simbiotica</h3>
            <p className="text-gray-600">
              Il tuo successo è il nostro successo. Il nostro modello di ricavo è allineato 
              alla tua crescita.
            </p>
          </div>
        </div>
      </div>
    </section>

    {/* Numeri */}
    <section className="py-16 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-12">LinkBay-CMS in Numeri</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <div className="text-3xl font-bold text-red-600">2.880+</div>
            <div className="text-gray-600">Ore di sviluppo</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">100%</div>
            <div className="text-gray-600">Codice proprietario</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">∞</div>
            <div className="text-gray-600">Negozi gestibili</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-red-600">0</div>
            <div className="text-gray-600">Compromessi</div>
          </div>
        </div>
      </div>
    </section>

    {/* Citazione */}
    <section className="py-16 bg-gradient-to-r from-red-600 to-red-700 text-white">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <div className="text-6xl mb-4">"</div>
        <p className="text-2xl md:text-3xl font-light mb-6 leading-relaxed">
          Forniamo l'arsenale tecnico per chi vuole scalare davvero
        </p>
        <p className="text-red-100 italic">Tutto il resto è solo CMS</p>
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
            className="fill-[#c51f1f]"
          ></path>
          <path 
            d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" 
            opacity=".5" 
            className="fill-[#c51f1f]"
          ></path>
          <path 
            d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" 
            className="fill-[#c51f1f]"
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

export default AboutPage;