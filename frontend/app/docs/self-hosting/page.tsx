import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Self-Hosting',
  description:
    'Deploy LinkBay-CMS on your own infrastructure with Docker and Traefik. Step-by-step guide for prerequisites, configuration, and first-run setup.',
};

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="mb-10">
    <h2 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-100">{title}</h2>
    <div className="text-sm text-gray-600 leading-relaxed space-y-3">{children}</div>
  </section>
);

const Code = ({ children }: { children: React.ReactNode }) => (
  <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-xs font-mono">
    {children}
  </code>
);

const ShellBlock = ({ children }: { children: string }) => (
  <pre className="bg-gray-900 text-green-400 rounded-xl px-5 py-4 overflow-x-auto text-sm font-mono my-3 whitespace-pre">
    <code>{children}</code>
  </pre>
);

const EnvBlock = ({ children }: { children: string }) => (
  <pre className="bg-gray-900 text-amber-300 rounded-xl px-5 py-4 overflow-x-auto text-sm font-mono my-3 whitespace-pre">
    <code>{children}</code>
  </pre>
);

const Warning = ({ children }: { children: React.ReactNode }) => (
  <div className="bg-amber-50 border border-amber-200 rounded-xl px-5 py-4 text-sm text-gray-700 leading-relaxed">
    <span className="font-semibold text-amber-700">⚠ Important: </span>
    {children}
  </div>
);

const Callout = ({ children }: { children: React.ReactNode }) => (
  <div className="bg-red-50 border border-red-100 rounded-xl px-5 py-4 text-sm text-gray-700 leading-relaxed">
    {children}
  </div>
);

export default function SelfHostingPage() {
  return (
    <article className="prose-none">
      {/* Header */}
      <div className="mb-10">
        <span className="inline-block px-3 py-1 bg-red-100 text-[#ff5758] rounded-full text-xs font-semibold mb-4">
          Self-Hosting
        </span>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Self-hosting guide</h1>
        <p className="text-gray-500 text-base leading-relaxed">
          Run LinkBay-CMS on your own server using Docker and Traefik. This guide covers
          prerequisites, environment configuration, and first-run commands.
        </p>
        <Callout>
          Self-hosting is intended for technical users and developers. The managed cloud version at{' '}
          <a
            href="https://app.linkbay-cms.com"
            className="text-[#ff5758] hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            app.linkbay-cms.com
          </a>{' '}
          requires no infrastructure work.
        </Callout>
      </div>

      <Section title="Prerequisites">
        <ul className="space-y-2">
          {[
            'Docker Engine 24+ and Docker Compose v2',
            'A domain name with wildcard DNS configured (e.g. *.linkbay-cms.com → your server IP)',
            'Ports 80 and 443 open on your server firewall',
            'A Stripe account for payment processing (test mode is fine to start)',
          ].map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="text-[#ff5758] font-bold mt-0.5 shrink-0">✓</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>

        <p>
          The wildcard DNS record is required because each store gets its own subdomain (e.g.{' '}
          <Code>{'{store}'}.yourdomain.com</Code>). Traefik handles TLS termination via Let&apos;s
          Encrypt automatically.
        </p>
      </Section>

      <Section title="1. Clone and configure">
        <p>Clone the repository and copy the root environment template:</p>

        <ShellBlock>{`$ git clone https://github.com/your-org/linkbay-cms.git
$ cd linkbay-cms
$ cp .env.example .env`}</ShellBlock>

        <p>
          Open <Code>.env</Code> and set the critical variables listed in the next section before
          running any containers.
        </p>
      </Section>

      <Section title="2. Critical environment variables">
        <p>
          The following variables <strong>must</strong> be set before the first boot. All are in the
          root <Code>.env</Code> file.
        </p>

        <EnvBlock>{`# Domain configuration
CENTRAL_DOMAIN=app.yourdomain.com
SESSION_DOMAIN=.yourdomain.com          # leading dot = wildcard for subdomains

# Application key (generate once with: php artisan key:generate)
APP_KEY=base64:...

# Database
DB_HOST=postgres
DB_DATABASE=linkbay
DB_USERNAME=linkbay
DB_PASSWORD=change_me_in_production

# Stripe — use sk_test_* for development, sk_live_* for production
STRIPE_SECRET=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Terms version — bump this to force users to re-accept updated terms
TERMS_VERSION=v1.0`}</EnvBlock>

        <Warning>
          Never commit <Code>.env</Code> to version control. Rotate <Code>APP_KEY</Code> before
          going to production — changing it after launch invalidates all encrypted values (sessions,
          cookies, encrypted DB fields).
        </Warning>
      </Section>

      <Section title="3. Start the stack">
        <ShellBlock>{`$ docker compose up -d`}</ShellBlock>

        <p>
          This starts Traefik, the Laravel backend, PostgreSQL, Redis, and the Next.js marketing
          frontend. On first boot, Traefik will request TLS certificates from Let&apos;s Encrypt —
          allow a minute for this to complete.
        </p>

        <p>Verify containers are healthy:</p>
        <ShellBlock>{`$ docker compose ps`}</ShellBlock>
      </Section>

      <Section title="4. Run migrations">
        <p>Run the central database migrations to create the schema:</p>

        <ShellBlock>{`$ docker compose exec backend php artisan migrate --force`}</ShellBlock>

        <p>
          This creates all central tables (agencies, tenants, billing events, layout templates,
          theme presets, etc.). Tenant databases are provisioned automatically when stores are
          created via the panel.
        </p>
      </Section>

      <Section title="5. Create the first super-admin">
        <p>
          The super-admin account is the root user for the entire platform. Create it with the
          following artisan command:
        </p>

        <ShellBlock>{`$ docker compose exec backend php artisan make:filament-user`}</ShellBlock>

        <p>
          You&apos;ll be prompted for a name, email, and password. This account will have access to
          the super-admin Filament panel at{' '}
          <Code>app.yourdomain.com</Code>.
        </p>

        <Warning>
          After creating the super-admin, log in and verify the <strong>Plugin Catalog</strong> is
          seeded with the default items. If it&apos;s empty, run:{' '}
          <Code>php artisan db:seed --class=PluginCatalogSeeder</Code>.
        </Warning>
      </Section>

      <Section title="6. Stripe webhook">
        <p>
          For billing to work, register a Stripe webhook pointing to:
        </p>
        <EnvBlock>{`https://app.yourdomain.com/stripe/webhook`}</EnvBlock>

        <p>
          In the Stripe dashboard, listen for these events:{' '}
          <Code>invoice.payment_succeeded</Code>,{' '}
          <Code>invoice.payment_failed</Code>,{' '}
          <Code>customer.subscription.updated</Code>,{' '}
          <Code>customer.subscription.deleted</Code>,{' '}
          <Code>payout.created</Code>,{' '}
          <Code>payout.paid</Code>.
        </p>
        <p>
          Copy the webhook signing secret into <Code>STRIPE_WEBHOOK_SECRET</Code> in your{' '}
          <Code>.env</Code>.
        </p>
      </Section>

      <Section title="Updating">
        <ShellBlock>{`$ git pull origin main
$ docker compose build backend
$ docker compose up -d
$ docker compose exec backend php artisan migrate --force`}</ShellBlock>

        <p>
          Migrations are backward-compatible within minor versions. Always read the CHANGELOG before
          updating across major versions.
        </p>
      </Section>

      <Section title="Variable reference">
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          {[
            {
              key: 'CENTRAL_DOMAIN',
              example: 'app.yourdomain.com',
              desc: 'The domain where all Filament panels are served.',
            },
            {
              key: 'SESSION_DOMAIN',
              example: '.yourdomain.com',
              desc: 'Cookie domain. The leading dot allows it to cover all subdomains.',
            },
            {
              key: 'APP_KEY',
              example: 'base64:...',
              desc: 'Laravel encryption key. Generate once with php artisan key:generate.',
            },
            {
              key: 'STRIPE_SECRET',
              example: 'sk_live_...',
              desc: 'Stripe secret key for API calls (subscriptions, payouts).',
            },
            {
              key: 'STRIPE_WEBHOOK_SECRET',
              example: 'whsec_...',
              desc: 'Signing secret for validating incoming Stripe webhook payloads.',
            },
            {
              key: 'TERMS_VERSION',
              example: 'v1.0',
              desc: 'Current T&C version. Changing this forces all users to re-accept.',
            },
          ].map((row, i) => (
            <div
              key={row.key}
              className={`flex flex-col sm:flex-row gap-2 sm:gap-4 px-4 py-3 text-xs ${
                i % 2 === 0 ? 'bg-gray-50' : 'bg-white'
              }`}
            >
              <Code>{row.key}</Code>
              <span className="text-gray-400 shrink-0 hidden sm:inline">·</span>
              <span className="text-gray-500 font-mono shrink-0">{row.example}</span>
              <span className="text-gray-600 sm:ml-auto">{row.desc}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* Prev/Next */}
      <div className="border-t border-gray-200 pt-8">
        <div className="grid sm:grid-cols-2 gap-4">
          <Link
            href="/docs/architecture"
            className="group block p-5 bg-white border border-gray-200 rounded-xl hover:border-[#ff5758] transition-all duration-300 no-underline"
          >
            <p className="text-sm font-semibold text-gray-900 group-hover:text-[#ff5758] transition-colors duration-200 mb-1">
              ← Architecture
            </p>
            <p className="text-xs text-gray-500">
              Understand the domain layout and role model before deploying.
            </p>
          </Link>
          <Link
            href="/contact"
            className="group block p-5 bg-white border border-gray-200 rounded-xl hover:border-[#ff5758] transition-all duration-300 no-underline"
          >
            <p className="text-sm font-semibold text-gray-900 group-hover:text-[#ff5758] transition-colors duration-200 mb-1">
              Need help? →
            </p>
            <p className="text-xs text-gray-500">Contact us if you run into issues.</p>
          </Link>
        </div>
      </div>
    </article>
  );
}
