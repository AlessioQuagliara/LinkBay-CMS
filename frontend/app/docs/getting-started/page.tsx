import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Getting Started',
  description:
    'Complete onboarding guide for LinkBay-CMS agencies: registration, plans, first store, and panel access.',
};

const Step = ({
  number,
  title,
  children,
}: {
  number: number;
  title: string;
  children: React.ReactNode;
}) => (
  <div className="flex gap-5 group">
    <div className="shrink-0 flex flex-col items-center">
      <div className="w-9 h-9 rounded-full bg-[#ff5758] text-white flex items-center justify-center text-sm font-bold shadow-sm">
        {number}
      </div>
      <div className="flex-1 w-px bg-gray-200 mt-2 group-last:hidden" />
    </div>
    <div className="pb-10 group-last:pb-0">
      <h3 className="text-base font-semibold text-gray-900 mb-2">{title}</h3>
      <div className="text-sm text-gray-600 leading-relaxed space-y-2">{children}</div>
    </div>
  </div>
);

const CodeBlock = ({ children }: { children: string }) => (
  <pre className="bg-gray-900 text-green-400 rounded-xl px-5 py-4 overflow-x-auto text-sm font-mono my-3">
    <code>{children}</code>
  </pre>
);

const Callout = ({ children }: { children: React.ReactNode }) => (
  <div className="bg-red-50 border border-red-100 rounded-xl px-5 py-4 text-sm text-gray-700 leading-relaxed">
    {children}
  </div>
);

export default function GettingStartedPage() {
  return (
    <article className="prose-none">
      {/* Header */}
      <div className="mb-10">
        <span className="inline-block px-3 py-1 bg-red-100 text-[#ff5758] rounded-full text-xs font-semibold mb-4">
          Onboarding
        </span>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Getting Started</h1>
        <p className="text-gray-500 text-base leading-relaxed">
          From registration to your first live store — the complete flow for a new LinkBay agency.
        </p>
      </div>

      {/* Steps */}
      <div className="mb-12">
        <Step number={1} title="Register your agency">
          <p>
            Go to{' '}
            <a
              href="https://app.linkbay-cms.com/agency/register"
              className="text-[#ff5758] hover:underline font-medium"
              target="_blank"
              rel="noopener noreferrer"
            >
              app.linkbay-cms.com/agency/register
            </a>{' '}
            and fill in your agency name, slug, and billing information.
          </p>
          <p>
            Your <strong>agency slug</strong> becomes part of your subdomain and cannot be changed
            after registration — choose it carefully. It should be lowercase, URL-safe, and
            representative of your agency brand.
          </p>
          <Callout>
            LinkBay is currently in <strong>private beta</strong>. Registration may require an
            invite code.{' '}
            <Link href="/contact" className="text-[#ff5758] hover:underline">
              Contact us
            </Link>{' '}
            to request access.
          </Callout>
        </Step>

        <Step number={2} title="Choose your plan">
          <p>During or after registration you&apos;ll select one of three plans:</p>

          <div className="grid sm:grid-cols-3 gap-3 my-3">
            {[
              { name: 'Starter', price: '€29/mo', stores: '5 stores', fee: '2.5% transaction' },
              { name: 'Pro', price: '€79/mo', stores: '20 stores', fee: '1.5% transaction', highlight: true },
              { name: 'Business', price: '€199/mo', stores: 'Unlimited', fee: '0.5% transaction' },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-xl border p-4 ${
                  plan.highlight
                    ? 'border-[#ff5758] bg-red-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <p className={`text-sm font-bold mb-1 ${plan.highlight ? 'text-[#ff5758]' : 'text-gray-900'}`}>
                  {plan.name}
                </p>
                <p className="text-lg font-bold text-gray-900">{plan.price}</p>
                <p className="text-xs text-gray-500 mt-1">{plan.stores}</p>
                <p className="text-xs text-gray-500">{plan.fee}</p>
              </div>
            ))}
          </div>

          <p>
            You can upgrade at any time from the{' '}
            <strong>Billing</strong> section of your agency panel. See the full{' '}
            <Link href="/pricing" className="text-[#ff5758] hover:underline">
              pricing page
            </Link>{' '}
            for a complete feature comparison.
          </p>
        </Step>

        <Step number={3} title="Access your agency panel">
          <p>
            After registration you land on your agency dashboard at{' '}
            <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
              app.linkbay-cms.com
            </code>
            . This is your central control panel for everything: stores, layouts, themes, team
            members, clients, and billing.
          </p>
          <p>
            Your agency panel is shared with the rest of the LinkBay platform — it runs on the same
            domain but is fully scoped to your agency. Each agency sees only its own data.
          </p>
        </Step>

        <Step number={4} title="Create your first store">
          <p>
            From the dashboard, click <strong>New Store</strong> to open the provisioning wizard.
            The wizard will ask for:
          </p>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 my-2">
            <li>Store name and slug (used as the subdomain)</li>
            <li>Client assignment (optional — link to an existing Agency Client)</li>
            <li>Initial layout template (you can change this at any time)</li>
          </ul>
          <p>
            Once provisioned, a dedicated database is created for the store and a welcome email is
            sent to the store admin. The store becomes accessible at{' '}
            <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
              {'{store-slug}'}.linkbay-cms.com
            </code>
            .
          </p>
        </Step>

        <Step number={5} title="Build the storefront">
          <p>
            Inside the <strong>Layout Manager</strong>, create layout templates with drag-and-drop
            blocks (hero, rich text, CTA, testimonials, etc.). Assign a template to a page slot
            (e.g. <em>home</em>, <em>about</em>) on each store.
          </p>
          <p>
            Under <strong>Themes</strong>, pick a system theme or create a custom palette. Premium
            themes (Midnight, Noir, Atelier, Meridian) are available on Pro and Business plans.
          </p>
          <Callout>
            <strong>Tip:</strong> Themes support a <em>Fork</em> feature — you can derive a
            per-client variant from any system theme and customize its colors, typography, and
            spacing while keeping the parent structure in sync.
          </Callout>
        </Step>
      </div>

      {/* Next steps */}
      <div className="border-t border-gray-200 pt-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Next steps</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            {
              title: 'Architecture overview',
              description: 'Understand how multi-tenancy, domains, and roles are structured.',
              href: '/docs/architecture',
            },
            {
              title: 'Self-hosting guide',
              description: 'Deploy LinkBay on your own infrastructure with Docker and Traefik.',
              href: '/docs/self-hosting',
            },
          ].map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="group block p-5 bg-white border border-gray-200 rounded-xl hover:border-[#ff5758] transition-all duration-300 no-underline"
            >
              <p className="text-sm font-semibold text-gray-900 group-hover:text-[#ff5758] transition-colors duration-200 mb-1">
                {card.title} →
              </p>
              <p className="text-xs text-gray-500 leading-relaxed">{card.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </article>
  );
}
