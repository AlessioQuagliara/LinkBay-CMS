import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "About — LinkBay",
  description:
    "Why LinkBayCMS exists, how we think about agencies, and the principles behind the product.",
  keywords: "about linkbay, founder, agency infrastructure, white-label commerce",
};

const WaveTop = () => (
  <div className="left-0 w-full overflow-hidden">
    <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
      <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" className="fill-red-500" />
      <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" className="fill-red-500" />
      <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-red-600" />
    </svg>
  </div>
);

export default function AboutPage() {
  return (
    <main className="min-h-screen overflow-hidden">
      <WaveTop />

      {/* ── Hero ─────────────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-16">
        <div className="max-w-3xl mx-auto px-4 text-center relative z-10">
          <div className="mb-6">
            <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
              About LinkBay
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Infrastructure agencies shouldn&rsquo;t have to build themselves
          </h1>
          <p className="text-lg text-gray-600 leading-relaxed">
            Every time an agency takes on a new commerce client, the same infrastructure problem appears.
            Somewhere in the process, someone rebuilds what someone else already built — or patches together
            tools that don&rsquo;t quite fit. LinkBayCMS exists so that doesn&rsquo;t have to happen.
          </p>
        </div>
      </section>

      {/* ── Why LinkBayCMS ──────────────────────────────────────────────────────── */}
      <section className="py-16 bg-white">
        <div className="max-w-5xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-5">Why LinkBay</h2>
              <p className="text-gray-600 leading-relaxed mb-4">
                Agencies are good at building relationships, understanding client needs, and delivering
                tailored solutions. They are not supposed to be database administrators or infrastructure
                engineers for each client they take on.
              </p>
              <p className="text-gray-600 leading-relaxed mb-4">
                The problem is that most commerce platforms are built for the end merchant, not for the
                agency behind them. There&rsquo;s no central view, no shared infrastructure, no sensible
                way to run 10 or 20 or 50 client stores without duct-taping things together.
              </p>
              <p className="text-gray-600 leading-relaxed">
                LinkBayCMS is built for the agency, not the merchant. The merchant is your client. The platform
                is yours.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-5">How we think about agencies</h2>
              <p className="text-gray-600 leading-relaxed mb-4">
                Your agency owns the client relationship. You set the prices, define the experience, and
                decide how much of the underlying platform to show or hide. That&rsquo;s not a feature — it&rsquo;s
                the foundational assumption.
              </p>
              <p className="text-gray-600 leading-relaxed mb-4">
                LinkBayCMS earns a share of what your clients pay you. That means our revenue grows when your
                agency grows. There is no scenario where we benefit from you stagnating.
              </p>
              <p className="text-gray-600 leading-relaxed">
                We keep platform fees transparent and published. No renegotiation, no surprises, no
                &ldquo;custom enterprise pricing&rdquo; that actually means &ldquo;we&rsquo;ll charge whatever we can get away with.&rdquo;
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Founder ──────────────────────────────────────────────────────────── */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">The person behind it</h2>

          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-red-200 rounded-full flex items-center justify-center shrink-0">
                <span className="text-3xl">👨‍💻</span>
              </div>
              <div className="text-center md:text-left">
                <h3 className="text-xl font-bold text-gray-900 mb-1">Alessio Quagliara</h3>
                <p className="text-red-600 font-semibold mb-3 text-sm">Founder &amp; Developer</p>
                <p className="text-gray-700 leading-relaxed">
                  LinkBayCMS is a solo-built, founder-led product. I design, build, and maintain it —
                  every line of code, every architecture decision. I built it because the problem is real
                  and the existing solutions didn&rsquo;t fit how agencies actually work.
                </p>
              </div>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-100">
              <p className="text-gray-500 text-sm italic text-center">
                &ldquo;My focus is on maintainability, transparency, and building a product that agencies can
                actually rely on for their business — not just demo on a slide deck.&rdquo;
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Values ───────────────────────────────────────────────────────────── */}
      <section className="py-16 bg-white">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">What drives the product decisions</h2>
            <p className="text-gray-600">Three principles that show up in every choice we make.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: "🔍",
                title: "Transparency",
                body: "Platform fees are published per plan, not negotiated per customer. You know exactly what you&rsquo;re paying and what LinkBayCMS earns before you sign up.",
              },
              {
                icon: "🔧",
                title: "Practical innovation",
                body: "We build features that solve real agency problems. If a feature looks impressive in a demo but doesn&rsquo;t help you deliver a better product to clients, it doesn&rsquo;t ship.",
              },
              {
                icon: "📈",
                title: "Shared growth",
                body: "Our revenue model is tied to yours. The more clients you grow and the more you charge them, the more we both earn. There&rsquo;s no conflict of interest built in.",
              },
            ].map((v) => (
              <div key={v.title} className="text-center p-6 bg-gray-50 rounded-2xl border border-gray-100">
                <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">{v.icon}</span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">{v.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: v.body }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-r from-gray-900 to-red-900 text-white py-20">
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl font-bold mb-5">See if it&rsquo;s a fit for your agency</h2>
          <p className="text-xl mb-8 opacity-90">
            Tell us how you run your client stores today. We&rsquo;ll be straightforward about what LinkBayCMS can and can&rsquo;t do for you.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/contact" className="px-8 py-4 text-lg font-bold rounded-xl bg-white text-red-600 hover:bg-gray-100 shadow-lg transition-all duration-300">
              Talk to our team
            </Link>
            <Link href="/pricing" className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-white text-white hover:bg-white hover:text-red-600 transition-all duration-300">
              See plans &amp; pricing
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
