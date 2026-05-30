import React from "react";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Documentation — LinkBay-CMS",
  description: "Integrate LinkBay-CMS into your agency workflows, automations, and SaaS operations using our REST API.",
  keywords: "linkbay api, rest api, agency api, cms integration, store api, webhook"
};

export default function ApiDocsPage() {
  return (
    <main className="max-w-4xl mx-auto py-12 px-4">
      {/* Hero */}
      <h1 className="text-4xl font-extrabold mb-3 text-gray-900 text-center">API Documentation</h1>
      <p className="mb-10 text-lg text-gray-700 text-center max-w-2xl mx-auto">
        The <span className="font-linkbay">LinkBay-CMS</span> API lets you integrate agency and store operations
        into your own workflows, automations, and SaaS tools.<br />
        All endpoints follow REST conventions and require authenticated requests.<br />
        <span className="italic text-base text-gray-500 block mt-2">
          API access is currently available on request. Contact{" "}
          <a href="mailto:info@linkbay-cms.com" className="text-red-600">info@linkbay-cms.com</a>{" "}
          to get started.
        </span>
      </p>

      {/* Quickstart */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-3 text-gray-800">Quickstart</h2>
        <div className="bg-gray-900 rounded-lg px-5 py-4 mb-3">
          <pre className="text-green-200 text-sm whitespace-pre-line">
{`# Base URL
https://api.linkbay-cms.com/v1/

# Authentication header
Authorization: Bearer <your-api-token>`}
          </pre>
        </div>
        <p className="text-gray-600 text-sm">
          Authenticate using an API token issued for your agency account. Tokens are scoped by role
          and isolated per agency — one agency cannot access another agency&apos;s data or stores.
        </p>
      </section>

      {/* Authentication */}
      <section className="mb-12">
        <h2 className="text-xl font-bold mb-4 text-gray-900">Authentication</h2>
        <p className="text-gray-700 mb-3">
          Every request must include a Bearer token in the <code className="bg-gray-100 px-1 rounded text-sm">Authorization</code> header.
          Tokens are issued per agency and carry role-based permissions (agency admin, editor, viewer).
        </p>
        <div className="bg-gray-900 rounded-lg px-5 py-4">
          <pre className="text-green-200 text-sm whitespace-pre-line">
{`curl -X GET "https://api.linkbay-cms.com/v1/stores" \\
  -H "Authorization: Bearer <your-api-token>"`}
          </pre>
        </div>
      </section>

      {/* Core Endpoints */}
      <section className="mb-14">
        <h2 className="text-xl font-bold mb-4 text-gray-900">Core Endpoints</h2>
        <div className="space-y-7">

          <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
            <div className="flex justify-between items-center mb-1">
              <div className="font-mono font-semibold text-red-600">GET /v1/stores</div>
              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Agency-scoped</span>
            </div>
            <p className="text-gray-700 mb-2">Returns the list of stores managed by the authenticated agency, with pagination.</p>
            <pre className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-900">
{`curl -X GET "https://api.linkbay-cms.com/v1/stores" \\
  -H "Authorization: Bearer <token>"`}
            </pre>
          </div>

          <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
            <div className="flex justify-between items-center mb-1">
              <div className="font-mono font-semibold text-red-600">POST /v1/stores/{'{storeId}'}/products</div>
              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Store-scoped</span>
            </div>
            <p className="text-gray-700 mb-2">Creates a new product in the specified store. Requires editor or admin role.</p>
            <pre className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-900">
{`curl -X POST "https://api.linkbay-cms.com/v1/stores/abc/products" \\
  -H "Authorization: Bearer <token>" \\
  -d '{"name":"Product Name","price":29.90}'`}
            </pre>
          </div>

          <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
            <div className="flex justify-between items-center mb-1">
              <div className="font-mono font-semibold text-red-600">PATCH /v1/stores/{'{storeId}'}/orders/{'{orderId}'}</div>
              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Store-scoped</span>
            </div>
            <p className="text-gray-700 mb-2">Updates an order status (e.g. shipped, fulfilled, cancelled).</p>
          </div>

          <div className="bg-white border-l-4 border-red-500 rounded shadow p-5">
            <div className="flex justify-between items-center mb-1">
              <div className="font-mono font-semibold text-red-600">POST /v1/domains/verify</div>
              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">Agency-scoped</span>
            </div>
            <p className="text-gray-700 mb-2">Triggers DNS verification and SSL provisioning for a custom domain attached to a store.</p>
          </div>

        </div>
      </section>

      {/* Webhooks */}
      <section className="mb-14">
        <h2 className="text-xl font-bold mb-3 text-gray-900">Webhooks & Integrations</h2>
        <p className="text-gray-700 mb-3">
          LinkBay-CMS can send webhook events to an endpoint of your choice. Useful for syncing data
          with CRMs, accounting tools, or custom automations.
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>Payment completed — sync with external accounting or CRM</li>
          <li>Order status changed — trigger fulfillment or notification flows</li>
          <li>Store provisioned — run post-setup scripts or onboarding automations</li>
          <li>Customer registered — add to mailing list or CRM pipeline</li>
        </ul>
        <p className="text-xs text-gray-500">
          Webhook configuration is available via the agency dashboard. A full event reference
          will be published alongside the public API release.
        </p>
      </section>

      {/* Security */}
      <section className="mb-14">
        <h2 className="text-xl font-bold mb-3 text-gray-900">Security & Access Control</h2>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          <li>All requests require a valid Bearer token</li>
          <li>Role-based access: agency admin, editor, viewer</li>
          <li>Each agency is fully isolated — no cross-agency data access</li>
          <li>All API calls are rate-limited and logged</li>
          <li>HTTPS only — plain HTTP requests are rejected</li>
        </ul>
      </section>

      {/* CTA */}
      <section className="py-10 text-center">
        <p className="text-gray-600 mb-4">API access is available on request during the current access period.</p>
        <a
          href="mailto:info@linkbay-cms.com?subject=API%20access%20request"
          className="inline-block px-8 py-4 text-lg font-bold rounded-lg bg-red-600 text-white hover:bg-red-700 shadow">
          Request API Access
        </a>
      </section>
    </main>
  );
}
