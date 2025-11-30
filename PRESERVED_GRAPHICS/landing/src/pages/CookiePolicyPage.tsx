import React from "react";

export const CookiePolicyPage: React.FC = () => (
  <main className="max-w-4xl mx-auto py-16 px-4">
    {/* Header con branding */}
    <div className="text-center mb-12">
      <h1 className="text-4xl font-bold text-[#343a4D] mb-4">Cookie Policy</h1>
      <div className="w-20 h-1 bg-[#ff5758] mx-auto mb-6"></div>
      <p className="text-lg text-gray-700 max-w-2xl mx-auto">
        Questa Cookie Policy spiega come <strong>LinkBay-CMS</strong> utilizza i cookie e tecnologie simili, 
        nel rispetto del GDPR e della direttiva ePrivacy.
      </p>
    </div>

    <div className="bg-gray-50 rounded-lg p-6 mb-8 border-l-4 border-[#ff5758]">
      <p className="text-gray-700">
        <strong>Ultimo aggiornamento:</strong> 21 Luglio 2025<br/>
        <strong>Titolare del Trattamento:</strong> Alessio Quagliara<br/>
        <strong>Email DPO:</strong> <a href="mailto:privacy@linkbay-cms.com" className="text-[#ff5758] underline">privacy@linkbay-cms.com</a>
      </p>
    </div>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">1</span>
        Cosa sono i Cookie?
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          I cookie sono piccoli file di testo che i siti visitati inviano al tuo dispositivo (computer, tablet, smartphone), 
          dove vengono memorizzati per essere poi ritrasmessi agli stessi siti alla visita successiva.
        </p>
        <p className="text-gray-700">
          I cookie sono utilizzati per differenti finalità: esecuzione di autenticazioni informatiche, 
          monitoraggio di sessioni, memorizzazione di informazioni su specifiche configurazioni riguardanti 
          gli utenti che accedono al server, ecc.
        </p>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">2</span>
        Tipologie di Cookie Utilizzati
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-[#343a4D] mb-3">Cookie Tecnici (NECESSARI)</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li><strong>Funzionalità:</strong> Consentono il corretto funzionamento della piattaforma</li>
          <li><strong>Sessione:</strong> Memorizzano lo stato di login e preferenze utente</li>
          <li><strong>Sicurezza:</strong> Proteggono da attacchi CSRF e altre minacce</li>
          <li><strong>Base Giuridica:</strong> Esecuzione contratto (Art. 6.1.b GDPR)</li>
          <li><strong>Consenso:</strong> Non richiesto - necessari per il servizio</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">Cookie Analytics (STATISTICI)</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li><strong>Google Analytics 4:</strong> Dati anonimizzati e aggregati</li>
          <li><strong>Finalità:</strong> Analisi del traffico e miglioramento servizio</li>
          <li><strong>IP Anonimizzato:</strong> Ultimi 3 ottetti mascherati</li>
          <li><strong>Base Giuridica:</strong> Legittimo interesse (Art. 6.1.f GDPR)</li>
          <li><strong>Consenso:</strong> Esente per analytics anonimizzati</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">Cookie di Preferenze</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li><strong>Lingua e Regione:</strong> Memorizzano preferenze di localizzazione</li>
          <li><strong>Layout e Tema:</strong> Personalizzazioni dell'interfaccia</li>
          <li><strong>Base Giuridica:</strong> Consenso esplicito (Art. 6.1.a GDPR)</li>
        </ul>

        <div className="mt-4 p-4 bg-blue-50 rounded border border-blue-200">
          <strong>Importante:</strong> LinkBay-CMS <strong>NON utilizza cookie di profilazione</strong> 
          né cookie di terze parti a scopo pubblicitario o di tracciamento cross-site.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">3</span>
        Dettaglio Cookie Specifici
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-gray-700">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 text-left">Nome Cookie</th>
                <th className="p-3 text-left">Tipo</th>
                <th className="p-3 text-left">Finalità</th>
                <th className="p-3 text-left">Durata</th>
                <th className="p-3 text-left">Provider</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-3 font-mono">auth_token</td>
                <td className="p-3">Tecnico</td>
                <td className="p-3">Autenticazione utente e sicurezza sessione</td>
                <td className="p-3">24 ore</td>
                <td className="p-3">LinkBay-CMS</td>
              </tr>
              <tr className="border-b">
                <td className="p-3 font-mono">tenant_session</td>
                <td className="p-3">Tecnico</td>
                <td className="p-3">Identificazione tenant multitenant</td>
                <td className="p-3">Sessione</td>
                <td className="p-3">LinkBay-CMS</td>
              </tr>
              <tr className="border-b">
                <td className="p-3 font-mono">user_preferences</td>
                <td className="p-3">Preferenze</td>
                <td className="p-3">Memorizza layout e impostazioni utente</td>
                <td className="p-3">30 giorni</td>
                <td className="p-3">LinkBay-CMS</td>
              </tr>
              <tr className="border-b">
                <td className="p-3 font-mono">_ga</td>
                <td className="p-3">Analytics</td>
                <td className="p-3">Distinzione utenti (anonimizzato)</td>
                <td className="p-3">2 anni</td>
                <td className="p-3">Google Analytics</td>
              </tr>
              <tr>
                <td className="p-3 font-mono">_ga_*</td>
                <td className="p-3">Analytics</td>
                <td className="p-3">Persistenza sessione analytics</td>
                <td className="p-3">2 anni</td>
                <td className="p-3">Google Analytics</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">4</span>
        Gestione del Consenso
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Al primo accesso alla piattaforma, viene mostrato un banner di consenso cookies 
          che permette di:
        </p>
        
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-green-50 rounded border border-green-200">
            <strong className="text-[#343a4D]">Accettazione Selettiva</strong>
            <p className="text-sm mt-1">Consenti solo i cookie tecnici o anche quelli analytics</p>
          </div>
          <div className="p-4 bg-green-50 rounded border border-green-200">
            <strong className="text-[#343a4D]">Rifiuto Parziale/Totale</strong>
            <p className="text-sm mt-1">Rifiuta i cookie non necessari in qualsiasi momento</p>
          </div>
          <div className="p-4 bg-green-50 rounded border border-green-200">
            <strong className="text-[#343a4D]">Modifica Successiva</strong>
            <p className="text-sm mt-1">Cambia le preferenze dalle impostazioni account</p>
          </div>
          <div className="p-4 bg-green-50 rounded border border-green-200">
            <strong className="text-[#343a4D]">Revoca Consenso</strong>
            <p className="text-sm mt-1">Elimina i cookie dal browser o disattivali</p>
          </div>
        </div>

        <div className="p-4 bg-yellow-50 rounded border border-yellow-200">
          <strong>Nota:</strong> Il rifiuto dei cookie tecnici potrebbe compromettere 
          il corretto funzionamento della piattaforma e l'accesso ad alcune funzionalità.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">5</span>
        Come Disabilitare i Cookie
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Puoi gestire le preferenze sui cookie direttamente dal tuo browser:
        </p>
        
        <h3 className="font-semibold text-[#343a4D] mb-3">Browser più comuni:</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li><strong>Chrome:</strong> Impostazioni → Privacy e sicurezza → Cookie e altri dati dei siti</li>
          <li><strong>Firefox:</strong> Opzioni → Privacy & Sicurezza → Cookie e dati dei siti</li>
          <li><strong>Safari:</strong> Preferenze → Privacy → Gestisci dati sito web</li>
          <li><strong>Edge:</strong> Impostazioni → Cookie e autorizzazioni sito</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">Strumenti di terze parti:</h3>
        <p className="text-gray-700 mb-4">
          Esistono servizi come <strong>YourOnlineChoices</strong> (EDAA) che permettono 
          di gestire le preferenze di tracciamento per la pubblicità online.
        </p>

        <div className="p-4 bg-blue-50 rounded border border-blue-200">
          <strong>Modalità di navigazione privata:</strong> Puoi navigare in "modalità privata" 
          o "incognito" per limitare la memorizzazione dei cookie durante la sessione.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">6</span>
        Trasferimento Dati e Privacy
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          I dati raccolti tramite cookie possono essere trasferiti a:
        </p>
        
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li><strong>Google Ireland Limited:</strong> Per servizi analytics (adeguato GDPR)</li>
          <li><strong>Server Kamatera EU:</strong> Hosting in Europa (Francia/Germania)</li>
        </ul>

        <p className="text-gray-700">
          Per maggiori informazioni sul trattamento dei dati personali, 
          consulta la nostra <a href="/privacy" className="text-[#ff5758] underline">Privacy Policy</a> completa.
        </p>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">7</span>
        Aggiornamenti alla Cookie Policy
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Questa policy potrebbe essere aggiornata per adeguamenti normativi o evoluzioni tecniche.
        </p>
        <p className="text-gray-700">
          Le modifiche sostanziali saranno comunicate tramite:
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mt-2">
          <li>Notifica in piattaforma per gli utenti registrati</li>
          <li>Banner di avviso al primo accesso successivo alla modifica</li>
          <li>Pubblicazione della nuova versione su questa pagina</li>
        </ul>
      </div>
    </section>

    <section className="bg-[#343a4D] text-white rounded-lg p-8 text-center">
      <h2 className="text-2xl font-semibold mb-4">Domande sui Cookie?</h2>
      <p className="mb-4">Il nostro team è a disposizione per chiarimenti e gestione delle preferenze</p>
      <a href="mailto:privacy@linkbay-cms.com" className="inline-block bg-[#ff5758] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors">
        Contatta il Data Protection Officer
      </a>
      <p className="text-sm mt-4 text-gray-300">
        LinkBay-CMS • P.IVA: In fase di registrazione • Email: privacy@linkbay-cms.com
      </p>
    </section>
  </main>
);

export default CookiePolicyPage;