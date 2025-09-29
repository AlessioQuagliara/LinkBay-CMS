import React from "react";

export const ApiDocsPage: React.FC = () => (
  <main className="max-w-4xl mx-auto py-12 px-4">
    <h1 className="text-4xl font-extrabold mb-3 text-gray-900 text-center">API Documentation</h1>
    <p className="mb-10 text-lg text-gray-700 text-center">
      Integra le funzionalità di <b>LinkBay-CMS</b> nei tuoi flussi aziendali, SaaS, marketplace e automazioni.<br/>
      Tutte le API sono basate su principi REST e secure-by-design.<br />
      <span className="italic">Contatta <a href="mailto:alessio@linkbay-cms.com" className="text-red-600">alessio@linkbay-cms.com</a> per onboarding e chiavi API ufficiali.</span>
    </p>

    {/* API Quickstart */}
    <section className="mb-12">
      <h2 className="text-2xl font-bold mb-3 text-gray-800">Quickstart</h2>
      <div className="bg-gray-900 rounded-lg px-5 py-4 mb-3">
        <pre className="text-green-200 text-sm whitespace-pre-line">
{`# Base URL
https://api.linkbay-cms.com/v1/

# Autenticazione (JWT)
Authorization: Bearer <your-token>`}
        </pre>
      </div>
      <p className="text-gray-600 text-sm">
        Accedi con le stesse credenziali agency/proprietario. I permessi sono segmentati per ruolo e tenant.<br />
        Per test avanzati richiedi una API sandbox dedicata.
      </p>
    </section>

    {/* Endpoint Examples */}
    <section className="mb-14">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Principali Endpoint REST</h2>
      <div className="space-y-7">
        <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
          <div className="flex justify-between items-center mb-1">
            <div className="font-mono font-semibold text-red-600">GET /v1/websites</div>
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">All tenants</span>
          </div>
          <p className="text-gray-700 mb-1">Restituisce la lista dei siti/e-commerce dell’agenzia con dati multitenant e paginazione.</p>
          <pre className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-900 mb-0">curl -X GET "https://api.linkbay-cms.com/v1/websites" -H "Authorization: Bearer &lt;token&gt;"</pre>
        </div>
        <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
          <div className="flex justify-between items-center mb-1">
            <div className="font-mono font-semibold text-red-600">POST /v1/products</div>
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Tenant-specific</span>
          </div>
          <p className="text-gray-700 mb-1">Crea un nuovo prodotto nello spazio del tenant. Richiede permesso editor/admin.</p>
          <pre className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-900 mb-0">{`curl -X POST "https://api.linkbay-cms.com/v1/products" -H "Authorization: Bearer <token>" -d '{"name":"T-shirt","price":19.90}'`}</pre>
        </div>
        <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
          <div className="flex justify-between items-center mb-1">
            <div className="font-mono font-semibold text-red-600">PATCH /v1/orders/{'{orderId}'}</div>
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Tenant-specific</span>
          </div>
          <p className="text-gray-700 mb-1">Aggiorna stato ordine (es. spedito, evaso, annullato).</p>
        </div>
        <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
          <div className="flex justify-between items-center mb-1">
            <div className="font-mono font-semibold text-red-600">POST /v1/domains/verify</div>
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Agency</span>
          </div>
          <p className="text-gray-700 mb-1">Lancia la verifica DNS e il provisioning automatizzato SSL di un nuovo dominio.</p>
        </div>
      </div>
    </section>

    {/* Webhooks and Integrations */}
    <section className="mb-14">
      <h2 className="text-xl font-bold mb-3 text-gray-900">Webhook & Integrazioni</h2>
      <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
        <li>Webhook pagamenti completati per sincronizzazione con CRM/contabilità</li>
        <li>Integrazione marketplace LinkBay per la gestione plugin e temi</li>
        <li>Notifiche via webhook per eventi e-commerce (ordine completato, prodotto esaurito, registrazione cliente…)</li>
      </ul>
      <div className="text-xs text-gray-500">
        Presto disponibili anche <b>API GraphQL</b> (alpha, solo per clienti enterprise su richiesta).
      </div>
    </section>

    {/* Ruoli & Sicurezza */}
    <section className="mb-14">
      <h2 className="text-xl font-bold mb-3 text-gray-900">Sicurezza & Ruoli</h2>
      <ul className="list-disc list-inside text-gray-700 space-y-1">
        <li>Autenticazione JWT per ogni chiamata (Access/Refresh Token)</li>
        <li>Scope e ruoli: superadmin, agency admin, editor, entwickler, viewer</li>
        <li>Ogni endpoint è audit-logged e rate-limited</li>
        <li>RBAC e full data isolation multitenant</li>
      </ul>
    </section>

    {/* CTA */}
    <section className="py-10 text-center">
      <a
        href="mailto:alessio@linkbay-cms.com?subject=API%20access"
        className="inline-block px-8 py-4 text-lg font-bold rounded-lg bg-red-600 text-white hover:bg-red-700 shadow">
        Chiedi la tua API key personalizzata
      </a>
    </section>
  </main>
);

export default ApiDocsPage;
