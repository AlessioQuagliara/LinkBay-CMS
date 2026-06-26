import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Architecture',
  description:
    'How LinkBay-CMS is structured: multi-tenant isolation, domain routing, roles, and the central vs. tenant data model.',
};

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="mb-10">
    <h2 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-100">{title}</h2>
    <div className="text-sm text-gray-600 leading-relaxed space-y-3">{children}</div>
  </section>
);

const Badge = ({ label, color }: { label: string; color: string }) => (
  <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${color}`}>
    {label}
  </span>
);

const DiagramRow = ({
  domain,
  app,
  description,
}: {
  domain: string;
  app: string;
  description: string;
}) => (
  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 py-3 border-b border-gray-100 last:border-0">
    <code className="shrink-0 text-xs bg-gray-900 text-green-400 px-3 py-1.5 rounded-lg font-mono">
      {domain}
    </code>
    <span className="shrink-0 text-xs font-semibold text-[#ff5758]">{app}</span>
    <span className="text-xs text-gray-500">{description}</span>
  </div>
);

export default function ArchitecturePage() {
  return (
    <article className="prose-none">
      {/* Header */}
      <div className="mb-10">
        <span className="inline-block px-3 py-1 bg-red-100 text-[#ff5758] rounded-full text-xs font-semibold mb-4">
          Architecture
        </span>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Architecture overview</h1>
        <p className="text-gray-500 text-base leading-relaxed">
          LinkBay-CMS is a multi-tenant SaaS platform. Understanding how tenancy, domains, and roles
          interact helps you deploy and operate it confidently.
        </p>
      </div>

      <Section title="Domain layout">
        <p>The platform runs across three domain categories, each serving a distinct purpose:</p>

        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden my-4">
          <DiagramRow
            domain="linkbay-cms.com"
            app="Next.js (marketing)"
            description="Public marketing site — this is the site you are reading right now."
          />
          <DiagramRow
            domain="app.linkbay-cms.com"
            app="Laravel Filament (central)"
            description="All admin panels live here: super-admin, agency dashboard, client management."
          />
          <DiagramRow
            domain="{store}.linkbay-cms.com"
            app="Store storefront"
            description="Each provisioned store gets its own subdomain. The storefront is rendered by the backend and exposed via API."
          />
        </div>

        <p>
          <strong>Central domain</strong> (
          <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
            app.linkbay-cms.com
          </code>
          ) hosts every Filament panel. Authentication, billing, team management, store provisioning,
          layout templates, and theme configuration all happen here.
        </p>
        <p>
          <strong>Tenant subdomains</strong> are created dynamically when a store is provisioned.
          Traefik routes wildcard traffic (
          <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
            *.linkbay-cms.com
          </code>
          ) to the Laravel backend, which identifies the tenant from the subdomain and switches to
          the correct database before handling the request.
        </p>
      </Section>

      <Section title="Multi-tenant isolation">
        <p>
          LinkBay uses{' '}
          <a
            href="https://tenancyforlaravel.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#ff5758] hover:underline"
          >
            stancl/tenancy
          </a>{' '}
          for database-per-tenant isolation. Each store has its own PostgreSQL database — store
          products, orders, customers, and settings are completely isolated from every other store.
        </p>

        <div className="grid sm:grid-cols-2 gap-4 my-4">
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
              Central database
            </p>
            <ul className="space-y-1.5 text-xs text-gray-600">
              {[
                'Agencies and their plans',
                'Agency members and roles',
                'Agency clients',
                'Store (tenant) registry',
                'Billing events and payouts',
                'Layout templates and assignments',
                'Theme presets and assignments',
                'Plugin catalog and entitlements',
                'Usage events and health data',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2">
                  <span className="text-[#ff5758] font-bold mt-0.5">·</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
              Tenant database (per store)
            </p>
            <ul className="space-y-1.5 text-xs text-gray-600">
              {[
                'Store products and inventory',
                'Customer accounts',
                'Orders and transactions',
                'Store-specific settings',
                'Custom fields and extensions',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2">
                  <span className="text-[#ff5758] font-bold mt-0.5">·</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <p>
          The Laravel backend boots with the central database connection. When a request arrives on a
          tenant subdomain, the tenancy middleware resolves the tenant, switches the active
          database connection, and runs the request in the store&apos;s isolated context. No store
          data is ever accessible from another store&apos;s connection.
        </p>
      </Section>

      <Section title="Roles and access">
        <p>
          The platform has five distinct roles, separated across two scopes: the central (admin)
          context and the store (tenant) context.
        </p>

        <div className="space-y-3 my-4">
          {[
            {
              role: 'Super Admin',
              badge: { label: 'LinkBay only', color: 'bg-purple-100 text-purple-700' },
              description:
                'Full platform visibility. Manages agencies, plans, catalog items, billing events, and platform health. Accesses the super-admin Filament panel at app.linkbay-cms.com.',
            },
            {
              role: 'Agency Owner / Admin',
              badge: { label: 'Agency scope', color: 'bg-blue-100 text-blue-700' },
              description:
                'Manages the agency: creates and provisions stores, configures layouts and themes, manages team members, views billing and payout history, and accesses the agency Filament panel.',
            },
            {
              role: 'Agency Member',
              badge: { label: 'Agency scope', color: 'bg-blue-100 text-blue-700' },
              description:
                'Read-only or limited-write access to the agency panel. Cannot manage billing or invite other members. Exact capabilities are configurable per member.',
            },
            {
              role: 'Store Admin',
              badge: { label: 'Store scope', color: 'bg-green-100 text-green-700' },
              description:
                'Manages a single store: products, orders, customers, store-level settings. Receives a welcome email with access credentials when the store is provisioned.',
            },
            {
              role: 'Customer',
              badge: { label: 'Store scope', color: 'bg-gray-100 text-gray-700' },
              description:
                'End-user of a store. Has a customer-facing account within a single store context. Cannot cross store boundaries.',
            },
          ].map((row) => (
            <div
              key={row.role}
              className="flex flex-col sm:flex-row sm:items-start gap-3 p-4 bg-white border border-gray-200 rounded-xl"
            >
              <div className="sm:w-44 shrink-0">
                <p className="text-sm font-semibold text-gray-900 mb-1">{row.role}</p>
                <Badge label={row.badge.label} color={row.badge.color} />
              </div>
              <p className="text-xs text-gray-600 leading-relaxed">{row.description}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Request routing">
        <p>
          Traefik sits in front of the entire stack and handles routing based on the request
          subdomain:
        </p>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600 my-3">
          <li>A request arrives at the wildcard certificate (*.linkbay-cms.com).</li>
          <li>
            Traefik routes it to the appropriate container — the Next.js frontend for the root
            domain, or the Laravel backend for all subdomains.
          </li>
          <li>
            Laravel&apos;s tenancy middleware extracts the subdomain, resolves it to a tenant (store),
            and boots the tenant context.
          </li>
          <li>The request is handled within the store&apos;s isolated environment.</li>
        </ol>
        <p>
          For the central domain (
          <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
            app.linkbay-cms.com
          </code>
          ), no tenant context is initialized — all Filament panels operate on the central database.
        </p>
      </Section>

      {/* Next steps */}
      <div className="border-t border-gray-200 pt-8">
        <div className="grid sm:grid-cols-2 gap-4">
          <Link
            href="/docs/getting-started"
            className="group block p-5 bg-white border border-gray-200 rounded-xl hover:border-[#ff5758] transition-all duration-300 no-underline"
          >
            <p className="text-sm font-semibold text-gray-900 group-hover:text-[#ff5758] transition-colors duration-200 mb-1">
              ← Getting Started
            </p>
            <p className="text-xs text-gray-500">Register and set up your first store.</p>
          </Link>
          <Link
            href="/docs/self-hosting"
            className="group block p-5 bg-white border border-gray-200 rounded-xl hover:border-[#ff5758] transition-all duration-300 no-underline"
          >
            <p className="text-sm font-semibold text-gray-900 group-hover:text-[#ff5758] transition-colors duration-200 mb-1">
              Self-Hosting →
            </p>
            <p className="text-xs text-gray-500">Deploy on your own infrastructure.</p>
          </Link>
        </div>
      </div>
    </article>
  );
}
