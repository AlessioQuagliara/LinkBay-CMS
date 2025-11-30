import React from "react";
import { useSEO } from "../hooks/useSimpleSEO";

export const TermsPage: React.FC = () => {
  // SEO per Terms of Service
  useSEO({
    title: "Termini di Servizio",
    description: "Termini e Condizioni di utilizzo di LinkBay CMS. Leggi le regole d'uso della piattaforma per agenzie web e sviluppatori.",
    keywords: "termini servizio, condizioni uso, regole piattaforma, termini cms, contratto utilizzo"
  });

  return (
  <main className="max-w-4xl mx-auto py-16 px-4">
    {/* Header con branding */}
    <div className="text-center mb-12">
      <h1 className="text-4xl font-bold text-[#343a4D] mb-4">Termini e Condizioni di Servizio</h1>
      <div className="w-20 h-1 bg-[#ff5758] mx-auto mb-6"></div>
      <p className="text-lg text-gray-700 max-w-2xl mx-auto">
        Benvenuto su <strong>LinkBay-CMS</strong>. Questi Termini regolano l'utilizzo della nostra piattaforma SaaS B2B. 
        Leggili attentamente prima di accedere ai nostri servizi.
      </p>
    </div>

    <div className="bg-red-50 rounded-lg p-6 mb-8 border-l-4 border-[#ff5758]">
      <p className="text-gray-700">
        <strong>⚠️ Importante:</strong> Questi Termini costituiscono un accordo legalmente vincolante tra te e LinkBay-CMS. 
        Accedendo alla piattaforma, accetti integralmente queste condizioni.
      </p>
    </div>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">1</span>
        Definizioni
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <dl className="grid md:grid-cols-2 gap-4 text-gray-700">
          <div>
            <dt className="font-semibold text-[#343a4D]">Piattaforma</dt>
            <dd>Il software LinkBay-CMS fornito come servizio (SaaS)</dd>
          </div>
          <div>
            <dt className="font-semibold text-[#343a4D]">Agenzia Partner</dt>
            <dd>Cliente B2B che utilizza la piattaforma per i propri clienti finali</dd>
          </div>
          <div>
            <dt className="font-semibold text-[#343a4D]">Servizio</dt>
            <dd>Piano di abbonamento sottoscritto (Pro, Scale, Enterprise)</dd>
          </div>
          <div>
            <dt className="font-semibold text-[#343a4D]">Contenuto</dt>
            <dd>Dati, immagini, testi caricati dall'Agenzia Partner</dd>
          </div>
        </dl>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">2</span>
        Accettazione dei Termini
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          Creando un account su LinkBay-CMS, confermi di:
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>Avere almeno 18 anni e la capacità legale di stipulare contratti</li>
          <li>Rappresentare un'agenzia, software house o azienda legittimamente costituita</li>
          <li>Fornire informazioni accurate e complete durante la registrazione</li>
          <li>Mantenere la riservatezza delle credenziali di accesso</li>
          <li>Accettare la nostra Privacy Policy e le condizioni di utilizzo</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">3</span>
        Descrizione del Servizio
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          LinkBay-CMS è una piattaforma infrastrutturale SaaS multitenant di tipo B2B che permette ad Agenzie Partner di:
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li>Creare e gestire negozi e-commerce white-label per i propri clienti finali</li>
          <li>Utilizzare funzionalità di marketplace con gestione commissioni</li>
          <li>Configurare domini, SSL e impostazioni tecniche in modo automatizzato</li>
          <li>Accedere a dashboard centralizzata per la gestione multi-tenant</li>
        </ul>
        
        <div className="p-4 bg-blue-50 rounded border border-blue-200">
          <strong>Modello di Licenza:</strong> Il servizio è fornito in modalità subscription (SaaS). 
          Non viene concessa alcuna licenza d'uso del codice sorgente.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">4</span>
        Obblighi e Responsabilità dell'Agenzia Partner
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-[#343a4D] mb-3">4.1 Utilizzo Consentito</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li>Utilizzare la piattaforma esclusivamente per scopi legittimi e leciti</li>
          <li>Rispettare tutte le leggi applicabili (privacy, e-commerce, consumer protection)</li>
          <li>Mantenere aggiornati i dati di fatturazione e contatto</li>
          <li>Formare adeguatamente i propri clienti finali sull'utilizzo della piattaforma</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">4.2 Utilizzo Vietato</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>Attività illegali, fraudolente o diffamatorie</li>
          <li>Spam, phishing o attività di marketing non consentite</li>
          <li>Violazione di diritti di proprietà intellettuale di terzi</li>
          <li>Utilizzo eccessivo che comprometta le performance della piattaforma</li>
          <li>Reverse engineering, decompilazione o copia del software</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">5</span>
        Piani e Pagamenti
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-[#343a4D] mb-3">5.1 Subscription</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>I piani sono fatturati mensilmente o annualmente con pagamento anticipato</li>
          <li>Il prezzo include IVA o altre tasse applicabili</li>
          <li>È possibile effettuare upgrade in qualsiasi momento</li>
          <li>I downgrade decorrono dal ciclo di fatturazione successivo</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">5.2 Commissioni Marketplace</h3>
        <p className="text-gray-700 mb-4">
          Oltre all'abbonamento, possono applicarsi commissioni sulle transazioni dei marketplace creati:
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>Agency Pro: 5% sulle commissioni dell'agenzia</li>
          <li>Agency Scale: 3% sulle commissioni dell'agenzia</li>
          <li>Enterprise: Personalizzato in base all'accordo</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">5.3 Rinnovi e Disdetta</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>I contratti si rinnovano automaticamente alla scadenza</li>
          <li>La disdetta può essere effettuata con 30 giorni di preavviso</li>
          <li>Non sono previsti rimborsi per periodi non utilizzati</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">6</span>
        Proprietà Intellettuale
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Diritti di LinkBay-CMS</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1 text-sm">
              <li>Software e piattaforma sono di proprietà esclusiva</li>
              <li>Marchio registrato "LinkBay-CMS"</li>
              <li>Documentazione, know-how, processi</li>
              <li>Modelli e template forniti</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Diritti dell'Agenzia Partner</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1 text-sm">
              <li>Contenuti creati dall'agenzia</li>
              <li>Dati dei clienti finali</li>
              <li>Brand identity dell'agenzia</li>
              <li>Customizzazioni approvate</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-yellow-50 rounded border border-yellow-200">
          <strong>Licenza Limitata:</strong> Concediamo una licenza non esclusiva e non trasferibile 
          per utilizzare la piattaforma durante il periodo di subscription.
        </div>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">7</span>
        Limitazione di Responsabilità
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <p className="text-gray-700 mb-4">
          LinkBay-CMS fornisce il servizio "così com'è" e "come disponibile". 
          La nostra responsabilità è limitata come segue:
        </p>
        
        <h3 className="font-semibold text-[#343a4D] mb-3">7.1 Garanzie</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>Non forniamo garanzie di uninterrupted service</li>
          <li>Non garantiamo che il servizio sia esente da errori</li>
          <li>Le prestazioni possono variare in base a fattori esterni</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">7.2 Limiti di Responsabilità</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>La responsabilità massima è limitata all'importo pagato negli ultimi 12 mesi</li>
          <li>Esclusi danni indiretti, consequenziali o lucro cessante</li>
          <li>Non siamo responsabili per contenuti di terze parti</li>
          <li>Esclusi eventi di forza maggiore</li>
        </ul>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">8</span>
        Durata e Risoluzione
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-[#343a4D] mb-3">8.1 Durata del Contratto</h3>
        <p className="text-gray-700 mb-4">
          Il contratto decorre dalla data di attivazione e si rinnova automaticamente per periodi 
          della stessa durata, salvo disdetta.
        </p>

        <h3 className="font-semibold text-[#343a4D] mb-3">8.2 Cause di Risoluzione</h3>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>Mancato pagamento dopo 15 giorni dal sollecito</li>
          <li>Violazione dei termini di utilizzo</li>
          <li>Attività illecite o fraudolente</li>
          <li>Richieste delle autorità competenti</li>
        </ul>

        <h3 className="font-semibold text-[#343a4D] mb-3">8.3 Effetti della Risoluzione</h3>
        <p className="text-gray-700">
          Alla scadenza o risoluzione, l'accesso alla piattaforma sarà disabilitato. 
          I dati saranno conservati per 30 giorni, durante i quali è possibile richiedere l'export.
        </p>
      </div>
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-semibold text-[#343a4D] mb-4 flex items-center">
        <span className="w-6 h-6 bg-[#ff5758] rounded-full mr-3 flex items-center justify-center text-white text-sm">9</span>
        Disposizioni Generali
      </h2>
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Legge Applicabile</h3>
            <p className="text-gray-700 text-sm">
              Questi Termini sono regolati dalla legge italiana. 
              Eventuali controversie saranno di competenza del Foro di Milano.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Modifiche ai Termini</h3>
            <p className="text-gray-700 text-sm">
              Ci riserviamo il diritto di modificare questi Termini. 
              Le modifiche sostanziali saranno comunicate con 30 giorni di preavviso.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Trasferimento del Contratto</h3>
            <p className="text-gray-700 text-sm">
              L'Agenzia Partner non può cedere il contratto senza il nostro consenso scritto.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-[#343a4D] mb-2">Comunicazioni</h3>
            <p className="text-gray-700 text-sm">
              Le comunicazioni avvengono via email all'indirizzo registrato. 
              Si considerano ricevute entro 24 ore dall'invio.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section className="bg-[#343a4D] text-white rounded-lg p-8 text-center">
      <h2 className="text-2xl font-semibold mb-4">Hai Domande sui Termini?</h2>
      <p className="mb-4">Il nostro team legale è a disposizione per chiarimenti</p>
      <a href="mailto:legal@linkbay-cms.com" className="inline-block bg-[#ff5758] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors">
        Contatta l'Ufficio Legale
      </a>
      <p className="text-sm mt-4 text-gray-300">
        LinkBay-CMS • P.IVA: In fase di registrazione • Email: legal@linkbay-cms.com
      </p>
    </section>

    <div className="mt-8 text-center text-gray-500 text-sm">
      <p>Documento aggiornato al 21 Luglio 2025 • Versione 1.0</p>
    </div>
  </main>
  );
};

export default TermsPage;