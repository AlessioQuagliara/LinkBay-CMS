import React from "react";
import { Link } from "react-router-dom";
import { MapPin, Mail, Instagram, Linkedin, Github } from "lucide-react";

export const Footer: React.FC = () => (
  <footer className="bg-[#343a4D] text-white">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid lg:grid-cols-4 md:grid-cols-2 gap-8">
        {/* Brand & tagline */}
        <div className="lg:col-span-1">
          <Link to="/" className="flex items-center space-x-3 mb-6 group">
            <img src="/logo-white.svg" alt="LinkBay CMS" className="h-12 w-auto" />
            <span className="sr-only">LinkBay - Modern Content Management</span>
          </Link>
          <p className="text-gray-300 text-sm leading-relaxed mb-6">
            L'armaiolo delle agenzie digitali. Gestione multi-tenant, marketplace, automazione: 
            il tuo arsenale per conquistare infinite nicchie di mercato.
          </p>
          <div className="flex space-x-4">
            <a 
              href="https://www.instagram.com/linkbaycms/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 bg-white/10 rounded-lg hover:bg-[#ff5758] transition-colors duration-300"
              aria-label="Seguici su Instagram"
            >
              <Instagram className="w-5 h-5" />
            </a>
            <a 
              href="https://www.linkedin.com/showcase/linkbay-cms/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 bg-white/10 rounded-lg hover:bg-[#ff5758] transition-colors duration-300"
              aria-label="Seguici su LinkedIn"
            >
              <Linkedin className="w-5 h-5" />
            </a>
            <a 
              href="https://github.com/AlessioQuagliara/LinkBay-CMS/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 bg-white/10 rounded-lg hover:bg-[#ff5758] transition-colors duration-300"
              aria-label="Visualizza su GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>

        {/* Product */}
        <div>
          <h3 className="font-bold text-lg mb-6 relative pb-2">
            Prodotto
            <span className="absolute bottom-0 left-0 w-8 h-0.5 bg-[#ff5758]"></span>
          </h3>
          <ul className="space-y-3">
            <li>
              <Link 
                to="/features" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Funzionalità
              </Link>
            </li>
            <li>
              <Link 
                to="/pricing" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Pricing
              </Link>
            </li>
            <li>
              <Link 
                to="/marketplace" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Marketplace
              </Link>
            </li>
            <li>
              <Link 
                to="/api-docs" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                API Docs
              </Link>
            </li>
          </ul>
        </div>

        {/* Company */}
        <div>
          <h3 className="font-bold text-lg mb-6 relative pb-2">
            Azienda
            <span className="absolute bottom-0 left-0 w-8 h-0.5 bg-[#ff5758]"></span>
          </h3>
          <ul className="space-y-3">
            <li>
              <Link 
                to="/about" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Chi siamo
              </Link>
            </li>
            <li>
              <Link 
                to="/contact" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Contattaci
              </Link>
            </li>
            <li>
              <Link 
                to="/work-with-us" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Lavora con noi
              </Link>
            </li>
            <li>
              <Link 
                to="/blog" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Blog
              </Link>
            </li>
          </ul>
        </div>

        {/* Legal & Contact */}
        <div>
          <h3 className="font-bold text-lg mb-6 relative pb-2">
            Supporto
            <span className="absolute bottom-0 left-0 w-8 h-0.5 bg-[#ff5758]"></span>
          </h3>
          <ul className="space-y-3 mb-6">
            <li>
              <Link 
                to="/privacy" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Privacy Policy
              </Link>
            </li>
            <li>
              <Link 
                to="/terms" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Termini di Servizio
              </Link>
            </li>
            <li>
              <Link 
                to="/cookie-policy" 
                className="text-gray-300 hover:text-[#ff5758] transition-colors duration-300 flex items-center group"
              >
                <span className="w-1 h-1 bg-[#ff5758] rounded-full mr-3 opacity-0 group-hover:opacity-100 transition-opacity"></span>
                Cookie Policy
              </Link>
            </li>
          </ul>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-3 text-gray-300">
              <Mail className="w-4 h-4 text-[#ff5758]" />
              <span className="text-sm">info@linkbay-cms.com</span>
            </div>
            <div className="flex items-center space-x-3 text-gray-300">
              <MapPin className="w-4 h-4 text-[#ff5758]" />
              <span className="text-sm">Faloppio, CO - Italia</span>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-[#ff5758]/10 to-[#343a4D] border border-[#ff5758]/20 rounded-2xl p-8 mt-12 text-center">
        <h3 className="text-2xl font-bold mb-2">Pronto a salpare con noi?</h3>
        <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
          Unisciti alle agenzie che stanno rivoluzionando il modo di gestire l'e-commerce multitenant. 
          La tua flotta di negozi ti aspetta.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="http://localhost:3003/register"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 bg-[#ff5758] text-white rounded-xl hover:bg-[#e04e4e] transition-colors duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            Inizia Trial Gratuito
          </a>
          <Link
            to="/contact"
            className="px-8 py-3 border border-[#ff5758] text-[#ff5758] rounded-xl hover:bg-[#ff5758] hover:text-white transition-all duration-300 font-medium"
          >
            Richiedi Demo
          </Link>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-600 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
        <p className="text-gray-400 text-sm mb-4 md:mb-0">
          &copy; {new Date().getFullYear()} LinkBay-CMS. 
          <span className="text-[#ff5758] mx-1">⚓</span> 
          Developed by Alessio Quagliara. All rights reserved.
        </p>
        <div className="flex space-x-6 text-gray-400 text-sm">
          <span>P.IVA: In fase di registrazione</span>
          <span>•</span>
          <span>REA: CO- In fase di registrazione</span>
        </div>
      </div>
    </div>
  </footer>
);

export default Footer;