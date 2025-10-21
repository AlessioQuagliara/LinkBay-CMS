import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Ship, Lock, Mail, Eye, EyeOff, User, Building, Check, Waves, Anchor } from "lucide-react";
import { useSEO } from "../../hooks/useSimpleSEO";

export const RegisterPage: React.FC = () => {
  // SEO per la registrazione
  useSEO({
    title: "Registrati",
    description: "Registra la tua agenzia su LinkBay CMS. Prova gratuita 14 giorni per gestire tutti i siti dei tuoi clienti da un'unica piattaforma.",
    keywords: "registrazione linkbay, prova gratuita cms, signup agenzia, trial gratuito",
    noindex: true
  });
  const [form, setForm] = useState({ 
    name: "", 
    email: "", 
    password: "", 
    agency: "",
    phone: "",
    website: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!form.name || !form.email || !form.password || !form.agency) {
      setError("Compila tutti i campi obbligatori per registrarti.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Simulazione chiamata API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Qui chiamata API per nuova agency
      console.log("Registration attempt:", form);
      setSent(true);
    } catch (err) {
      setError("Errore durante la registrazione. Riprova.");
    } finally {
      setIsLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center relative overflow-hidden p-4">
        <div className="absolute top-0 left-0 w-full opacity-10">
          <Waves className="w-full h-32 text-[#343a4D]" />
        </div>
        
        <div className="max-w-md w-full text-center relative z-10">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="w-10 h-10 text-white" />
            </div>
            
            <h1 className="text-2xl font-bold text-[#343a4D] mb-4">Registrazione Completata!</h1>
            
            <p className="text-gray-600 mb-6">
              Abbiamo inviato un'email di conferma a <strong>{form.email}</strong>. 
              Controlla la tua casella per attivare la prova gratuita.
            </p>
            
            <div className="bg-blue-50 rounded-xl p-4 mb-6">
              <h3 className="font-semibold text-[#343a4D] mb-2">Prossimi passi:</h3>
              <ul className="text-sm text-gray-600 space-y-1 text-left">
                <li>• Conferma il tuo account via email</li>
                <li>• Accedi alla dashboard</li>
                <li>• Configura il tuo primo negozio</li>
                <li>• Invita il tuo team</li>
              </ul>
            </div>

            <Link
              to="/login"
              className="inline-flex items-center justify-center w-full py-3 px-6 font-semibold rounded-xl bg-[#ff5758] text-white hover:bg-[#e04e4e] transition-colors duration-300"
            >
              <img src="/logo-white.svg" alt="LinkBay" className="h-5 w-auto mr-2" />
              Accedi alla Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
      <div className="absolute top-20 left-5 opacity-5 animate-float">
        <Anchor className="w-16 h-16 text-[#343a4D]" />
      </div>
      <div className="absolute bottom-20 right-5 opacity-5 animate-float-delayed">
        <Ship className="w-20 h-20 text-[#343a4D]" />
      </div>

      <div className="max-w-lg w-full relative z-10">
        {/* Card del form */}
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
          {/* Header con logo */}
          <div className="bg-gradient-to-r from-[#343a4D] to-[#2a2f3f] p-8 text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <img src="/logo-white.svg" alt="LinkBay CMS" className="h-12 w-auto" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Registra la tua Agenzia</h1>
            <p className="text-blue-100 text-sm">Prova gratuita 14 giorni · Nessuna carta richiesta</p>
          </div>

          <form onSubmit={handleSubmit} className="p-8 space-y-6" autoComplete="off">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-center text-sm">
                {error}
              </div>
            )}

            {/* Informazioni Personali */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="name" className="block font-semibold text-[#343a4D] flex items-center">
                  <User className="w-4 h-4 mr-2 text-[#ff5758]" />
                  Nome Completo *
                </label>
                <div className="relative">
                  <input
                    id="name"
                    name="name"
                    type="text"
                    autoComplete="name"
                    value={form.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 pl-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="Mario Rossi"
                    required
                    disabled={isLoading}
                  />
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="phone" className="block font-semibold text-[#343a4D] flex items-center">
                  <span className="w-4 h-4 mr-2 text-[#ff5758]">📱</span>
                  Telefono
                </label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  autoComplete="tel"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                  placeholder="+39 123 456 7890"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Informazioni Agenzia */}
            <div className="space-y-2">
              <label htmlFor="agency" className="block font-semibold text-[#343a4D] flex items-center">
                <Building className="w-4 h-4 mr-2 text-[#ff5758]" />
                Nome Agenzia/Brand *
              </label>
              <div className="relative">
                <input
                  id="agency"
                  name="agency"
                  type="text"
                  value={form.agency}
                  onChange={handleChange}
                  className="w-full px-4 py-3 pl-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                  placeholder="Digital Agency SRL"
                  required
                  disabled={isLoading}
                />
                <Building className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="website" className="block font-semibold text-[#343a4D]">
                Sito Web (opzionale)
              </label>
              <input
                id="website"
                name="website"
                type="url"
                autoComplete="url"
                value={form.website}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                placeholder="https://la-tua-agenzia.com"
                disabled={isLoading}
              />
            </div>

            {/* Credenziali */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="email" className="block font-semibold text-[#343a4D] flex items-center">
                  <Mail className="w-4 h-4 mr-2 text-[#ff5758]" />
                  Email *
                </label>
                <div className="relative">
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 pl-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="nome@agenzia.com"
                    required
                    disabled={isLoading}
                  />
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="block font-semibold text-[#343a4D] flex items-center">
                  <Lock className="w-4 h-4 mr-2 text-[#ff5758]" />
                  Password *
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    className="w-full px-4 py-3 pl-11 pr-11 border border-gray-300 rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent transition-all duration-300"
                    placeholder="Min. 8 caratteri"
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
            </div>

            {/* Vantaggi */}
            <div className="bg-blue-50 rounded-xl p-4">
              <h4 className="font-semibold text-[#343a4D] mb-2 flex items-center">
                <Check className="w-4 h-4 mr-2 text-green-500" />
                Cosa otterrai subito:
              </h4>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-[#ff5758] rounded-full mr-2"></span>
                  Accesso immediato
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-[#ff5758] rounded-full mr-2"></span>
                  14 giorni gratuiti
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-[#ff5758] rounded-full mr-2"></span>
                  Supporto dedicato
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-[#ff5758] rounded-full mr-2"></span>
                  Demo personalizzata
                </div>
              </div>
            </div>

            {/* Bottone di Registrazione */}
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-4 px-6 font-semibold rounded-xl bg-gradient-to-r from-[#ff5758] to-[#e04e4e] text-white hover:from-[#e04e4e] hover:to-[#ff5758] shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-lg flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Registrazione in corso...</span>
                </>
              ) : (
                <>
                  <Ship className="w-5 h-5" />
                  <span>Attiva la Prova Gratuita</span>
                </>
              )}
            </button>

            {/* Link Login */}
            <div className="text-center text-sm text-gray-600">
              Hai già un account agency?{' '}
              <Link
                to="/login"
                className="text-[#ff5758] font-semibold hover:text-[#e04e4e] transition-colors duration-300"
              >
                Accedi ora
              </Link>
            </div>
          </form>

          {/* Footer */}
          <div className="bg-gray-50 px-8 py-4 border-t border-gray-200">
            <div className="text-center text-xs text-gray-500">
              &copy; {new Date().getFullYear()} LinkBay-CMS. 
              <span className="text-[#ff5758] mx-1">⚓</span>
              Il tuo arsenale digitale
            </div>
          </div>
        </div>{/* end card */}

        {/* Informazioni di sicurezza */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center space-x-4 text-xs text-gray-500 bg-white/50 backdrop-blur-sm rounded-xl px-4 py-2">
            <Lock className="w-3 h-3 text-green-500" />
            <span>I tuoi dati sono protetti e crittografati</span>
          </div>
        </div>
      </div>{/* end max-w-lg */}
    </div>
  );
};

export default RegisterPage;