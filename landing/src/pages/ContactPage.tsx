import React, { useState } from "react";
import { Mail, Phone, MapPin, Ship, Send, Anchor, Waves } from "lucide-react";
import { useSEO } from "../hooks/useSimpleSEO";

export const ContactPage: React.FC = () => {
  // SEO per la pagina contatti
  useSEO({
    title: "Contatti",
    description: "Contatta il team LinkBay CMS per supporto, demo personalizzate o partnership. Siamo qui per aiutarti a far crescere la tua agenzia.",
    keywords: "contatti linkbay, supporto cms, demo agenzia, partnership web, assistenza tecnica"
  });
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Onde decorative */}
      <div className="absolute top-0 left-0 w-full opacity-10">
        <Waves className="w-full h-32 text-[#343a4D]" />
      </div>
      
      <div className="absolute bottom-0 left-0 w-full opacity-5 rotate-180">
        <Waves className="w-full h-32 text-[#343a4D]" />
      </div>

      <main className="max-w-6xl mx-auto py-16 px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Header Section */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="w-20 h-20 bg-[#ff5758] rounded-2xl flex items-center justify-center shadow-lg">
                <Ship className="w-10 h-10 text-white" />
              </div>
              <div className="absolute -bottom-2 -right-2 bg-[#343a4D] text-white p-2 rounded-full">
                <Mail className="w-4 h-4" />
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-[#343a4D] mb-4 font-[Electrolize]">
            Contattaci
          </h1>
          
          <div className="w-24 h-1 bg-[#ff5758] mx-auto mb-6"></div>
          
          <p className="text-xl text-[#343a4D] max-w-3xl mx-auto leading-relaxed">
            Pronto a salpare verso nuove opportunità? Parliamo di <span className="text-[#ff5758] font-semibold">crescita condivisa</span>, 
            non solo di codice. La tua prossima flotta di e-commerce ti aspetta.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 mb-20">
          {/* Informazioni di Contatto */}
          <div className="space-y-8">
            <div>
              <h2 className="text-3xl font-bold text-[#343a4D] mb-6">Get in Touch</h2>
              <p className="text-[#343a4D] text-lg mb-8">
                Sei un'agenzia digitale in crescita? Una software house che cerca partner tecnologici? 
                Un brand che vuole espandersi in multiple nicchie? Siamo qui per te.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-4 p-6 bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <div className="bg-[#ff5758] p-3 rounded-lg">
                  <Mail className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#343a4D] mb-1">Email</h3>
                  <p className="text-[#343a4D]">info@linkbay-cms.com</p>
                  <p className="text-sm text-gray-600">Risposta entro 24 ore</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 p-6 bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <div className="bg-[#ff5758] p-3 rounded-lg">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#343a4D] mb-1">Telefono</h3>
                  <p className="text-[#343a4D]">+39 02 1234 5678</p>
                  <p className="text-sm text-gray-600">Lun-Ven, 9:00-18:00</p>
                </div>
              </div>

              <div className="flex items-start space-x-4 p-6 bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <div className="bg-[#ff5758] p-3 rounded-lg">
                  <MapPin className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#343a4D] mb-1">Sede</h3>
                  <p className="text-[#343a4D]">Faloppio, CO</p>
                  <p className="text-sm text-gray-600">Lombardia, Italia - 21020</p>
                </div>
              </div>
            </div>

            {/* Statistiche */}
            <div className="grid grid-cols-3 gap-4 pt-6">
              <div className="text-center p-4 bg-white rounded-xl shadow-md">
                <div className="text-2xl font-bold text-[#ff5758]">50+</div>
                <div className="text-sm text-[#343a4D]">Agenzie Partner</div>
              </div>
              <div className="text-center p-4 bg-white rounded-xl shadow-md">
                <div className="text-2xl font-bold text-[#ff5758]">500+</div>
                <div className="text-sm text-[#343a4D]">Negozi Gestiti</div>
              </div>
              <div className="text-center p-4 bg-white rounded-xl shadow-md">
                <div className="text-2xl font-bold text-[#ff5758]">24/7</div>
                <div className="text-sm text-[#343a4D]">Supporto</div>
              </div>
            </div>
          </div>

          {/* Form di Contatto */}
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
            <div className="flex items-center space-x-3 mb-6">
              <div className="bg-[#ff5758] p-2 rounded-lg">
                <Send className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-[#343a4D]">Invia un Messaggio</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block mb-2 font-medium text-[#343a4D]">
                    Nome *
                  </label>
                  <input
                    id="name"
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="Il tuo nome"
                  />
                </div>
                <div>
                  <label htmlFor="company" className="block mb-2 font-medium text-[#343a4D]">
                    Azienda *
                  </label>
                  <input
                    id="company"
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="Nome azienda"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="email" className="block mb-2 font-medium text-[#343a4D]">
                    Email *
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="email@azienda.com"
                  />
                </div>
                <div>
                  <label htmlFor="phone" className="block mb-2 font-medium text-[#343a4D]">
                    Telefono
                  </label>
                  <input
                    id="phone"
                    type="tel"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="+39 ..."
                  />
                </div>
              </div>

              <div>
                <label htmlFor="subject" className="block mb-2 font-medium text-[#343a4D]">
                  Oggetto *
                </label>
                <select 
                  id="subject"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                >
                  <option value="">Seleziona un oggetto</option>
                  <option value="demo">Richiesta Demo</option>
                  <option value="partnership">Partnership</option>
                  <option value="support">Supporto Tecnico</option>
                  <option value="custom">Sviluppo Custom</option>
                  <option value="other">Altro</option>
                </select>
              </div>

              <div>
                <label htmlFor="message" className="block mb-2 font-medium text-[#343a4D]">
                  Messaggio *
                </label>
                <textarea
                  id="message"
                  required
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 resize-none focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                  placeholder="Raccontaci la tua esigenza... Quanti negozi gestisci? Quali sono le tue principali sfide?"
                ></textarea>
              </div>

              <button
                type="submit"
                disabled={sent}
                className="w-full py-4 px-6 font-semibold rounded-xl bg-gradient-to-r from-[#ff5758] to-[#e04e4e] text-white hover:from-[#e04e4e] hover:to-[#ff5758] shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                {sent ? (
                  <>
                    <Anchor className="w-5 h-5" />
                    <span>Messaggio Inviato!</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Invia Richiesta</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-[#343a4D] to-[#2a2f3f] rounded-2xl p-12 text-center text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <Ship className="w-64 h-64" />
          </div>
          
          <h2 className="text-3xl font-bold mb-4 relative z-10">Pronto a Rivoluzionare il Tuo Business?</h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto relative z-10">
            Unisciti alle agenzie che hanno già scelto LinkBay-CMS per gestire la loro flotta di e-commerce.
            La tua crescita inizia da qui.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center relative z-10">
            <a
              href="/demo"
              className="px-8 py-3 bg-[#ff5758] text-white rounded-xl hover:bg-[#e04e4e] transition-colors duration-300 font-medium shadow-lg hover:shadow-xl"
            >
              Richiedi una Demo Personalizzata
            </a>
            <a
              href="/pricing"
              className="px-8 py-3 border border-white text-white rounded-xl hover:bg-white hover:text-[#343a4D] transition-all duration-300 font-medium"
            >
              Scopri i Piani
            </a>
          </div>
        </div>

        {/* Direct Email */}
        <div className="text-center mt-12 p-6 bg-white rounded-2xl shadow-lg border border-gray-100">
          <p className="text-[#343a4D] text-lg mb-2">
            Preferisci scrivere direttamente?
          </p>
          <a 
            href="mailto:alessio@linkbay-cms.com" 
            className="text-2xl font-bold text-[#ff5758] hover:text-[#e04e4e] transition-colors duration-300"
          >
            alessio@linkbay-cms.com
          </a>
          <p className="text-gray-600 mt-2">Risposta garantita entro 24 ore lavorative</p>
        </div>
      </main>
    </div>
  );
};

export default ContactPage;