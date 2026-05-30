import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Features — LinkBay",
  description:
    "Agency control deck, white-label branding, client subscriptions, reusable layouts, AI agents, and the technical foundation behind LinkBay.",
  keywords:
    "agency dashboard, white-label commerce, client subscriptions, reusable layouts, AI content agents",
};

const WaveTop = () => (
  <div className="left-0 w-full overflow-hidden" id="top">
    <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
      <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" className="fill-red-500" />
      <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" className="fill-red-500" />
      <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-red-600" />
    </svg>
  </div>
);

export default function FeaturesPage() {
  return (
    <main className="min-h-screen overflow-hidden">
      <WaveTop />

      {/* ── Page header ──────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-16">
        <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
          <div className="mb-6">
            <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
              What LinkBayCMS does
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Features built around how agencies actually work
          </h1>
          <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
            Every feature in LinkBayCMS exists to answer one question: how do we help agencies
            deliver more client stores, more consistently, with a better business model underneath?
          </p>
        </div>
      </section>

      {/* ── A. Agency control deck ───────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-14 items-center">
            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
                Agency control deck
              </span>
              <h2 className="text-3xl font-bold text-gray-900 mb-5">
                All your client stores. One place.
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-6">
                The agency dashboard gives you a clear, searchable overview of every client and every store
                under your account. No more switching between logins or tools.
              </p>
              <ul className="space-y-3">
                {[
                  "See every client store at a glance — status, plan, activity.",
                  "Open any store to configure it without leaving your main panel.",
                  "Manage client records, contacts, and store associations from one view.",
                  "Everything scoped to your agency — no data from other agencies visible.",
                ].map((t) => (
                  <li key={t} className="flex items-start">
                    <div className="w-5 h-5 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-0.5 shrink-0">
                      <span className="text-red-600 text-xs">✓</span>
                    </div>
                    <span className="text-gray-700">{t}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-200">
              <div className="space-y-3">
                {[
                  { label: "Acme Corp", stores: 3, status: "active" },
                  { label: "Beta Studio", stores: 1, status: "active" },
                  { label: "Gamma Foods", stores: 2, status: "active" },
                  { label: "Delta Brand", stores: 1, status: "suspended" },
                ].map((c) => (
                  <div key={c.label} className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-100">
                    <div>
                      <span className="font-semibold text-gray-900">{c.label}</span>
                      <span className="text-gray-400 text-sm ml-2">{c.stores} store{c.stores > 1 ? "s" : ""}</span>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${c.status === "active" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {c.status}
                    </span>
                  </div>
                ))}
                <div className="text-center text-sm text-gray-400 pt-2">All inside your agency panel</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── B. White-label & branding ────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
              White-label &amp; branding
            </span>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Your agency&rsquo;s identity, end to end
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Clients experience your brand at every step. LinkBayCMS is invisible when you need it to be.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: "🌐", title: "Custom domains", body: "Each client store can live on its own domain or subdomain. Your agency panel lives on your own domain." },
              { icon: "🎨", title: "Logos & colours", body: "Upload your agency logo, define primary brand colours, and apply them across the panel and client-facing surfaces." },
              { icon: "📧", title: "Email templates", body: "Transactional emails — order confirmations, invitations, notifications — carry your agency&rsquo;s name and domain." },
              { icon: "👁️", title: "Hidden platform branding", body: "On Pro and Business plans, all LinkBayCMS branding is removed. Your clients see only what you want them to see." },
              { icon: "🏷️", title: "Per-client branding", body: "Give each client their own logo, colours, and store name within your agency. One platform, many identities." },
              { icon: "🔐", title: "Scoped access", body: "Clients only ever see their own store. No accidental exposure across your portfolio." },
            ].map((c) => (
              <div key={c.title} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <div className="text-3xl mb-3">{c.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{c.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: c.body }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── C. Client subscriptions & recurring revenue ──────────────────────── */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-14 items-start">
            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
                Client subscriptions &amp; recurring revenue
              </span>
              <h2 className="text-3xl font-bold text-gray-900 mb-5">
                Charge clients on your own terms
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-6">
                LinkBayCMS doesn&rsquo;t dictate what you charge your clients. You create plans, set prices,
                and assign them to client stores. Clients pay you; you keep the portion after the platform share.
              </p>
              <ul className="space-y-3">
                {[
                  "Create as many subscription plans as you need, with any price you choose.",
                  "Assign plans to individual client stores.",
                  "Billing is handled by Stripe. You collect payments under your own account.",
                  "LinkBay&rsquo;s platform share is calculated transparently on what clients pay you — the exact % is shown on the Pricing page per plan.",
                  "A separate transaction fee applies to sales made within each store.",
                ].map((t) => (
                  <li key={t} className="flex items-start">
                    <div className="w-5 h-5 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-0.5 shrink-0">
                      <span className="text-red-600 text-xs">✓</span>
                    </div>
                    <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: t }} />
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link href="/pricing" className="text-red-600 font-semibold hover:underline">
                  See exact platform shares per plan →
                </Link>
              </div>
            </div>

            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200">
              <h3 className="font-bold text-gray-900 mb-5">How the money flows</h3>
              <div className="space-y-4">
                {[
                  { step: "1", text: "Client pays the agency monthly (subscription you set)." },
                  { step: "2", text: "Agency pays LinkBayCMS a platform share on that amount (varies by plan: 10–30%)." },
                  { step: "3", text: "Agency also pays their own LinkBayCMS plan (€29–€199/mo)." },
                  { step: "4", text: "A transaction fee applies on sales within each store (0.5–2.5%)." },
                ].map((s) => (
                  <div key={s.step} className="flex gap-4 items-start">
                    <div className="w-7 h-7 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">
                      {s.step}
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">{s.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── D. Reusable layouts ──────────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-14 items-center">
            <div className="bg-white rounded-2xl p-8 border border-gray-100">
              <div className="space-y-4">
                {[
                  { icon: "📐", label: "Save layout", text: "Finalise a design for one client, save it as a reusable layout." },
                  { icon: "♻️", label: "Apply to new store", text: "When the next client onboards, start from that layout instead of blank." },
                  { icon: "✏️", label: "Customise per client", text: "Adjust colours, logo, content — the structure is already done." },
                  { icon: "🚀", label: "Ship faster", text: "Less time per store. More capacity for new clients." },
                ].map((s) => (
                  <div key={s.label} className="flex items-start gap-4">
                    <span className="text-2xl">{s.icon}</span>
                    <div>
                      <span className="font-semibold text-gray-900 text-sm">{s.label} — </span>
                      <span className="text-gray-600 text-sm">{s.text}</span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-6 border-t pt-4">Layout manager available on the Business plan.</p>
            </div>

            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
                Reusable layouts
              </span>
              <h2 className="text-3xl font-bold text-gray-900 mb-5">
                Design once. Deliver many times.
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-4">
                Every time you build a store layout from scratch, you&rsquo;re spending time on solved problems.
                LinkBay&rsquo;s layout manager lets you save what works and reuse it across your client portfolio.
              </p>
              <p className="text-gray-600 text-lg leading-relaxed">
                Maintain consistent quality without the maintenance overhead. New client? Start from a
                template, not from zero.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── E. AI agents ─────────────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-14">
            <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
              AI agents
            </span>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Handle the volume without adding headcount
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              AI in LinkBayCMS is an assistant for the tedious parts of store management — not a replacement for
              your editorial judgement.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: "✍️", title: "Draft product copy", body: "Generate initial descriptions for products and collections. Edit, approve, or discard." },
              { icon: "📋", title: "Duplicate patterns", body: "Clone sections, page structures, and component arrangements across stores." },
              { icon: "🗂️", title: "Bulk content fill", body: "Fill multiple fields in one pass — names, tags, descriptions — based on a short brief." },
              { icon: "✅", title: "Always under your control", body: "AI suggests; you decide. Nothing publishes without your approval." },
            ].map((c) => (
              <div key={c.title} className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                <div className="text-3xl mb-3">{c.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{c.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{c.body}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-sm text-gray-400 mt-8">
            AI credits included on Pro (5,000/mo) and Business (20,000/mo) plans.
          </p>
        </div>
      </section>

      {/* ── F. Technical architecture ────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 bg-gray-200 text-gray-600 rounded-full text-sm font-semibold mb-4">
              For technical readers
            </span>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What&rsquo;s running underneath
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Under the hood, LinkBayCMS uses a multi-tenant architecture to keep each client&rsquo;s data
              fully isolated while your agency operates from a single control deck.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 border border-gray-200 max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="font-bold text-gray-900 mb-4">Backend &amp; data</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  {[
                    "PHP / Laravel — application core",
                    "PostgreSQL — central and per-tenant schemas",
                    "Redis — caching and queue backend",
                    "Stripe — billing, Connect, webhooks",
                    "stancl/tenancy — schema-level data isolation",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-red-400 rounded-full shrink-0" />
                      {t}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-4">Frontend &amp; infrastructure</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  {[
                    "Next.js — marketing site and frontend layer",
                    "Filament — agency and admin panels",
                    "Tailwind CSS — UI styling",
                    "Docker + Traefik — containerised deployment, routing",
                    "Nginx — web server",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-red-400 rounded-full shrink-0" />
                      {t}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-6">
              <p className="text-gray-600 text-sm leading-relaxed">
                Each client store runs in its own PostgreSQL schema, completely isolated from every other store.
                The agency&rsquo;s central data (clients, billing, branding config) lives in a separate central database.
                Traefik handles domain routing so each store and each agency panel resolves to the right tenant automatically.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-r from-gray-900 to-red-900 text-white py-20">
        <div className="absolute top-0 left-0 w-full overflow-hidden">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
            <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-white" />
          </svg>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            See how it fits your agency
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Talk to us about your current setup and we&rsquo;ll walk through what a white-label rollout would look like.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/pricing" className="px-8 py-4 text-lg font-bold rounded-xl bg-white text-red-600 hover:bg-gray-100 shadow-lg transition-all duration-300">
              See plans &amp; pricing
            </Link>
            <Link href="/contact" className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-white text-white hover:bg-white hover:text-red-600 transition-all duration-300">
              Talk to our team
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
