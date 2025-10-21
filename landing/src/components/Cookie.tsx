import React, { useState, useEffect } from 'react';

type CookiePrefs = {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
};

const CookieConsentBanner: React.FC = () => {
  const [showBanner, setShowBanner] = useState<boolean>(false);
  const [showPreferences, setShowPreferences] = useState<boolean>(false);
  const [consentGiven, setConsentGiven] = useState<'pending' | 'custom' | 'denied'>('pending');
  const [preferences, setPreferences] = useState<CookiePrefs>({
    necessary: true, // Sempre attivi
    analytics: false,
    marketing: false,
  });

  // Controlla lo stato del consenso all'avvio
  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    const saved = localStorage.getItem('cookiePreferences');

    if (consent === 'pending' || consent === 'custom' || consent === 'denied') {
      setConsentGiven(consent);
      if (saved) {
        try {
          setPreferences(JSON.parse(saved));
        } catch {}
      }
    } else {
      setShowBanner(true);
    }
  }, []);

  const savePreferences = (prefs: CookiePrefs) => {
    const final = { ...prefs, necessary: true };
    setPreferences(final);
    localStorage.setItem('cookiePreferences', JSON.stringify(final));
    localStorage.setItem('cookieConsent', 'custom');
    setConsentGiven('custom');
    
    // Gestione cookie
    console.log(final.analytics ? 'Analytics attivati' : 'Analytics disattivati');
    console.log(final.marketing ? 'Marketing attivati' : 'Marketing disattivati');
  };

  const closeBanner = () => {
    setShowBanner(false);
    setShowPreferences(false);
  };

  const handleAcceptAll = () => {
    savePreferences({ necessary: true, analytics: true, marketing: true });
    closeBanner();
  };

  const handleRejectAll = () => {
    savePreferences({ necessary: true, analytics: false, marketing: false });
    closeBanner();
  };

  const handleSavePreferences = () => {
    savePreferences(preferences);
    closeBanner();
  };

  const togglePreference = (category: keyof CookiePrefs) => {
    if (category !== 'necessary') {
      setPreferences(prev => ({ ...prev, [category]: !prev[category] }));
    }
  };

  // Modale Preferenze Cookie
  const PreferencesModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={() => setShowPreferences(false)}
      ></div>
      
      {/* Modale */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-[#343a4D] text-white p-6 rounded-t-2xl">
          <h3 className="text-xl font-bold">Impostazioni Cookie</h3>
          <p className="text-blue-100 mt-1">Gestisci le tue preferenze sulla privacy</p>
        </div>
        
        {/* Contenuto */}
        <div className="p-6">
          {/* Cookie Necessari */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="font-semibold text-[#343a4D]">Cookie Necessari</h4>
                <p className="text-sm text-gray-600">Sempre attivi - essenziali per il funzionamento</p>
              </div>
              <div className="w-12 h-6 bg-[#ff5758] rounded-full flex items-center justify-center">
                <span className="text-white text-sm">Sì</span>
              </div>
            </div>
            <p className="text-xs text-gray-500">
              Sessioni utente, sicurezza, preferenze lingua, carrello acquisti
            </p>
          </div>
          
          {/* Cookie Analytics */}
          <div className="mb-6 p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="font-semibold text-[#343a4D]">Cookie Analytics</h4>
                <p className="text-sm text-gray-600">Ci aiutano a migliorare il sito</p>
              </div>
              <button
                onClick={() => togglePreference('analytics')}
                className={`w-12 h-6 rounded-full relative transition-colors ${
                  preferences.analytics ? 'bg-[#ff5758]' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    preferences.analytics ? 'transform translate-x-7' : 'transform translate-x-1'
                  }`}
                />
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Statistiche visite, pagine più visualizzate, performance sito
            </p>
          </div>
          
          {/* Cookie Marketing */}
          <div className="mb-6 p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="font-semibold text-[#343a4D]">Cookie Marketing</h4>
                <p className="text-sm text-gray-600">Personalizzano la tua esperienza</p>
              </div>
              <button
                onClick={() => togglePreference('marketing')}
                className={`w-12 h-6 rounded-full relative transition-colors ${
                  preferences.marketing ? 'bg-[#ff5758]' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                    preferences.marketing ? 'transform translate-x-7' : 'transform translate-x-1'
                  }`}
                />
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Pubblicità personalizzata, contenuti rilevanti, campagne marketing
            </p>
          </div>
          
          {/* Pulsanti */}
          <div className="flex flex-col gap-3">
            <button
              onClick={handleSavePreferences}
              className="bg-[#ff5758] text-white py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors"
            >
              Salva le mie preferenze
            </button>
            <button
              onClick={handleAcceptAll}
              className="border border-[#343a4D] text-[#343a4D] py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Accetta tutto
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Banner principale
  const CookieBanner = () => (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t-4 border-[#ff5758] shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Testo e descrizione */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[#343a4D] mb-2 flex items-center">
              <span className="mr-2">🔒</span> Controllo della Privacy
            </h3>
            <p className="text-gray-700 text-sm">
              Utilizziamo cookie per migliorare la tua esperienza. I cookie necessari sono sempre attivi, 
              ma puoi scegliere quali altri cookie accettare. 
              <a href="/privacy" className="text-[#ff5758] underline ml-1">Leggi la nostra policy</a>
            </p>
          </div>

          {/* Pulsanti di azione */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleRejectAll}
              className="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Rifiuta tutto
            </button>
            <button
              onClick={() => setShowPreferences(true)}
              className="px-5 py-2 border border-[#343a4D] text-[#343a4D] rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Personalizza
            </button>
            <button
              onClick={handleAcceptAll}
              className="px-5 py-2 bg-[#ff5758] text-white rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors"
            >
              Accetta tutto
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Pulsante fisso per riaprire le preferenze
  const FloatingPreferencesButton = () => (
    <button 
      onClick={() => setShowPreferences(true)}
      className="fixed bottom-4 left-4 z-30 bg-[#343a4D] text-white p-3 rounded-full shadow-lg hover:bg-[#ff5758] transition-colors group"
      title="Gestisci preferenze cookie"
    >
      {/* Icona che cambia in base allo stato */}
      {consentGiven === 'pending' ? (
        <span className="text-lg">🍪</span>
      ) : consentGiven === 'denied' || (consentGiven === 'custom' && !preferences.analytics && !preferences.marketing) ? (
        <span className="text-lg" title="Privacy protetta">🔒</span>
      ) : (
        <span className="text-lg" title="Preferenze cookie">⚙️</span>
      )}
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        {consentGiven === 'pending' ? 'Cookie non impostati' : 
         consentGiven === 'denied' ? 'Privacy massima' : 'Gestisci cookie'}
      </div>
    </button>
  );

  return (
    <>
      {/* Overlay per il banner */}
      {showBanner && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-30" onClick={handleRejectAll}></div>
      )}
      
      {/* Banner Cookie */}
      {showBanner && <CookieBanner />}
      
      {/* Modale Preferenze */}
      {showPreferences && <PreferencesModal />}
      
      {/* Pulsante fisso per riaprire le preferenze */}
      {!showBanner && consentGiven !== 'pending' && <FloatingPreferencesButton />}
    </>
  );
};

export default CookieConsentBanner;