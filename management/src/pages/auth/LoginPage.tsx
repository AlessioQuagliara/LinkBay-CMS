import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Ship, Lock, Mail, Eye, EyeOff, Compass, Waves } from "lucide-react";
import { useSEO } from "../../hooks/useSimpleSEO";

export const LoginPage: React.FC = () => {
  // SEO per la pagina di login (con noindex per privacy)
  useSEO({
    title: "Accedi",
    description: "Accedi alla dashboard LinkBay CMS per gestire i siti web dei tuoi clienti. Area riservata per agenzie e team autorizzati.",
    keywords: "login linkbay, accesso dashboard, area riservata agenzia",
    noindex: true
  });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError("Inserisci email e password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Simulazione chiamata API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Qui chiamata backend per login
      console.log("Login attempt:", { email, password });
      alert("Demo: login backend non implementato");
    } catch (err) {
      setError("Errore durante il login. Riprova.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center relative overflow-hidden p-4">
      {/* Onde decorative */}
      <div className="absolute top-0 left-0 w-full opacity-10">
        <Waves className="w-full h-32 text-[#343a4D]" />
      </div>
      
      <div className="absolute bottom-0 left-0 w-full opacity-5 rotate-180">
        <Waves className="w-full h-32 text-[#343a4D]" />
      </div>

      {/* Elementi decorativi */}
      <div className="absolute top-10 left-10 opacity-5 animate-float">
        <Compass className="w-16 h-16 text-[#343a4D]" />
      </div>
      <div className="absolute bottom-10 right-10 opacity-5 animate-float-delayed">
        <Ship className="w-20 h-20 text-[#343a4D]" />
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* Card del form */}
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
          {/* Header con logo */}
          <div className="bg-gradient-to-r from-[#343a4D] to-[#2a2f3f] p-8 text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <img src="/logo-white.svg" alt="LinkBay CMS" className="h-12 w-auto" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Accesso Agenzia</h1>
            <p className="text-blue-100 text-sm">Accedi al tuo arsenale digitale</p>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-6" autoComplete="off">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-center text-sm flex items-center justify-center">
                <Lock className="w-4 h-4 mr-2" />
                {error}
              </div>
            )}

            {/* Campo Email */}
            <div className="space-y-2">
              <label htmlFor="email" className="block font-semibold text-[#343a4D] flex items-center">
                <Mail className="w-4 h-4 mr-2 text-[#ff5758]" />
                Email Agenzia
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="w-full px-4 py-3 pl-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                  placeholder="nome@agenzia.com"
                  required
                  disabled={isLoading}
                />
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>

            {/* Campo Password */}
            <div className="space-y-2">
              <label htmlFor="password" className="block font-semibold text-[#343a4D] flex items-center">
                <Lock className="w-4 h-4 mr-2 text-[#ff5758]" />
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full px-4 py-3 pl-11 pr-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                  placeholder="Inserisci la tua password"
                  required
                  disabled={isLoading}
                />
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-[#ff5758] transition-colors duration-300"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Link Password Dimenticata */}
            <div className="text-right">
              <Link 
                to="/forgot-password" 
                className="text-sm text-[#ff5758] hover:text-[#e04e4e] transition-colors duration-300 font-medium"
              >
                Password dimenticata?
              </Link>
            </div>

            {/* Bottone di Accesso */}
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-4 px-6 font-semibold rounded-xl bg-gradient-to-r from-[#ff5758] to-[#e04e4e] text-white hover:from-[#e04e4e] hover:to-[#ff5758] shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-lg flex items-center justify-center space-x-2"
            >
                  {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Accesso in corso...</span>
                </>
              ) : (
                <>
                      <span>Accedi alla Dashboard</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className="relative flex items-center justify-center my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative bg-white px-4 text-sm text-gray-500">Nuovo qui?</div>
            </div>

            {/* Link Registrazione */}
            <div className="text-center">
              <Link 
                to="/register" 
                className="inline-flex items-center justify-center w-full py-3 px-6 font-semibold rounded-xl border-2 border-[#343a4D] text-[#343a4D] hover:bg-[#343a4D] hover:text-white transition-all duration-300 group"
              >
                <Compass className="w-5 h-5 mr-2 group-hover:rotate-180 transition-transform duration-300" />
                Registra la tua Agenzia
              </Link>
            </div>
          </form>

          {/* Footer */}
          <div className="bg-gray-50 px-8 py-4 border-t border-gray-200">
            <div className="text-center text-xs text-gray-500">
              &copy; {new Date().getFullYear()} LinkBay-CMS · 
              <span className="text-[#ff5758] mx-1">⚓</span>
              Il tuo arsenale digitale
            </div>
          </div>
        </div>

        {/* Informazioni di sicurezza */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center space-x-4 text-xs text-gray-500 bg-white/50 backdrop-blur-sm rounded-xl px-4 py-2">
            <Lock className="w-3 h-3 text-green-500" />
            <span>Connessione sicura SSL · 256-bit encryption</span>
          </div>
        </div>
      </div>

    </div>
  );
};

export default LoginPage;