import React from "react";
import { useSEO } from "../hooks/useSimpleSEO";

export const PrivacyPage: React.FC = () => {
  // SEO per Privacy Policy
  useSEO({
    title: "Privacy Policy",
    description: "Informativa sulla Privacy di LinkBay CMS. Scopri come proteggiamo e gestiamo i dati personali degli utenti e dei clienti.",
    keywords: "privacy policy, protezione dati, gdpr, informativa privacy, trattamento dati"
  });

  return (
  <main className="max-w-4xl mx-auto py-16 px-4">
    {/* Header con branding */}
    <div className="text-center mb-12">
      <h1 className="text-4xl font-bold text-[#343a4D] mb-4">Informativa sulla Privacy</h1>
      <div className="w-20 h-1 bg-[#ff5758] mx-auto mb-6"></div>
      <p className="text-lg text-gray-700 max-w-2xl mx-auto">
        <strong>LinkBay-CMS</strong> tratta la privacy e la sicurezza dei dati con la massima serietà, 
        in conformità con il Regolamento Generale sulla Protezione dei Dati (GDPR) UE 2016/679.
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
        Definizioni e Campo di Applicazione
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Questa informativa si applica a tutti i servizi offerti da <strong>LinkBay-CMS</strong>, 
          piattaforma SaaS multitenant B2B per la gestione di e-commerce white-label.
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li><strong>Interessato:</strong> Utente finale, cliente agenzia, visitatore del sito</li>
          <li><strong>Titolare:</strong> Alessio Quagliara, ideatore e sviluppatore di LinkBay-CMS</li>
          <li><strong>Responsabili del Trattamento:</strong> Fornitori di servizi tecnici (hosting, pagamenti)</li>
          <li><strong>Dati Personali:</strong> Qualsiasi informazione relativa a persona identificata o identificabile</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">2</span>
        Categorie di Dati Trattati
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-[#343a4D] mb-3">Dati Raccolti Automaticamente</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li>Dati di utilizzo (IP, browser, dispositivo, pagine visitate, durata sessione)</li>
          <li>Dati tecnici (log di sistema, errori, performance della piattaforma)</li>
          <li>Cookie tecnici e analytics anonimizzati</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">Dati Forniti Volontariamente</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>Dati di contatto (email, nome, telefono) per richieste commerciali</li>
          <li>Dati aziendali (nome agenzia, partita IVA, indirizzo) per contrattazione</li>
          <li>Credenziali di accesso alla piattaforma (crittografate)</li>
        </ul>

        <div className="mt-4 p-4 bg-yellow-50 rounded border border-yellow-200">
          <strong>Nota importante:</strong> LinkBay-CMS non raccoglie direttamente dati di pagamento. 
          Le transazioni sono gestite tramite <strong>Stripe</strong> e <strong>PayPal</strong>, 
          soggetti alle loro rispettive privacy policy.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">3</span>
        Base Giuridica e Finalità del Trattamento
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <table className="w-full text-sm text-gray-700">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Finalità</th>
              <th className="p-3 text-left">Base Giuridica</th>
              <th className="p-3 text-left">Conservazione</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3">Erogazione servizi SaaS</td>
              <td className="p-3">Esecuzione contratto (Art. 6.1.b GDPR)</td>
              <td className="p-3">Durata contratto + 10 anni (fiscale)</td>
            </tr>
            <tr className="border-b">
              <td className="p-3">Supporto tecnico e customer care</td>
              <td className="p-3">Legittimo interesse (Art. 6.1.f GDPR)</td>
              <td className="p-3">24 mesi dall'ultimo contatto</td>
            </tr>
            <tr className="border-b">
              <td className="p-3">Marketing diretto (newsletter)</td>
              <td className="p-3">Consenso esplicito (Art. 6.1.a GDPR)</td>
              <td className="p-3">Fino alla revoca del consenso</td>
            </tr>
            <tr>
              <td className="p-3">Compliance legale e sicurezza</td>
              <td className="p-3">Obbligo legale (Art. 6.1.c GDPR)</td>
              <td className="p-3">Come richiesto dalla legge</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">4</span>
        Trasferimento e Condivisione Dati
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          I dati possono essere condivisi con i seguenti soggetti, nel rispetto delle garanzie GDPR:
        </p>
        
        <h3 className="font-semibold text-[#343a4D] mb-3">Responsabili del Trattamento</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li><strong>Kamatera:</strong> Servizi di hosting (server in Europa)</li>
          <li><strong>Stripe:</strong> Elaborazione pagamenti (GDPR compliant)</li>
          <li><strong>PayPal:</strong> Pagamenti alternativi</li>
          <li><strong>Google Cloud:</strong> Servizi email e analytics (dati anonimizzati)</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">Trasferimenti Extra-UE</h3>
        <p className="text-gray-700">
          Qualora alcuni servizi implicassero trasferimenti fuori dall'SEE, ci assicuriamo che avvengano 
          nel rispetto del GDPR tramite:<br/>
          • Decisioni di Adeguatezza della Commissione Europea<br/>
          • Clausole Contrattuali Standard<br/>
          • Binding Corporate Rules
        </p>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">5</span>
        Diritti degli Interessati
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          In conformità con gli articoli 15-22 GDPR, hai diritto a:
        </p>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded border border-blue-200">
            <strong className="text-[#343a4D]">Accesso e Portabilità</strong>
            <p className="text-sm mt-1">Ottenere copia dei tuoi dati in formato strutturato</p>
          </div>
          <div className="p-4 bg-blue-50 rounded border border-blue-200">
            <strong className="text-[#343a4D]">Rettifica</strong>
            <p className="text-sm mt-1">Modificare dati inesatti o incompleti</p>
          </div>
          <div className="p-4 bg-blue-50 rounded border border-blue-200">
            <strong className="text-[#343a4D]">Cancellazione ("Diritto all'Oblio")</strong>
            <p className="text-sm mt-1">Eliminare i tuoi dati quando non più necessari</p>
          </div>
          <div className="p-4 bg-blue-50 rounded border border-blue-200">
            <strong className="text-[#343a4D]">Limitazione e Opposizione</strong>
            <p className="text-sm mt-1">Limitare il trattamento in specifiche circostanze</p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-green-50 rounded border border-green-200">
          <strong>Come esercitare i tuoi diritti:</strong><br/>
          Scrivi a <a href="mailto:privacy@linkbay-cms.com" className="text-[#ff5758] underline">privacy@linkbay-cms.com</a>. 
          Risponderemo entro 30 giorni dall'avvenuta ricezione della richiesta.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">6</span>
        Sicurezza delle Informazioni
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Implementiamo misure tecniche e organizzative adeguate per proteggere i dati personali:
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>Crittografia end-to-end dei dati sensibili</li>
          <li>Accesso ai dati limitato al personale autorizzato</li>
          <li>Backup giornalieri e sistemi di disaster recovery</li>
          <li>Monitoraggio continuo della sicurezza</li>
          <li>Valutazione periodica dei rischi (DPIA)</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">7</span>
        Cookies e Tecnologie Simili
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Utilizziamo solo cookie tecnici necessari al funzionamento della piattaforma. 
          I cookie analytics sono anonimizzati e non richiedono consenso preventivo.
        </p>
        <div className="text-sm text-gray-600">
          Per disabilitare i cookie, modifica le impostazioni del tuo browser. 
          Tieni presente che questo potrebbe compromettere alcune funzionalità del sito.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">8</span>
        Modifiche all'Informativa
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700">
          Questa informativa potrebbe essere aggiornata per riflettere cambiamenti normativi o evoluzioni del servizio. 
          Le modifiche sostanziali saranno comunicate via email agli utenti registrati e pubblicate in questa pagina.
        </p>
      </div>
    </section>

    <section className="bg-[#343a4D] text-white rounded-lg p-8 text-center">
      <h2 className="text-2xl font-semibold mb-4">Hai Domande sulla Privacy?</h2>
      <p className="mb-4">Il nostro team è a disposizione per chiarimenti e richieste</p>
      <a href="mailto:privacy@linkbay-cms.com" className="inline-block bg-[#ff5758] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors">
        Contatta il Data Protection Officer
      </a>
      <p className="text-sm mt-4 text-gray-300">
        LinkBay-CMS • P.IVA: In fase di registrazione • Email: privacy@linkbay-cms.com
      </p>
    </section>
  </main>
  );
};

export default PrivacyPage;