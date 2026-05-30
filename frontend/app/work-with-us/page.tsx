import RolesSection, { type JobPosition } from "./RolesSection";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://app.linkbay-cms.test";

async function fetchPublishedPositions(): Promise<JobPosition[]> {
  try {
    const res = await fetch(`${API_BASE}/api/careers/positions`, {
      next: { revalidate: 60 }, // cache for 60 seconds, revalidates in background
    });
    if (!res.ok) return [];
    const json = await res.json();
    return Array.isArray(json.data) ? json.data : [];
  } catch {
    return [];
  }
}

export default async function WorkWithUsPage() {
  const positions = await fetchPublishedPositions();

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">

      {/* Hero */}
      <div className="relative bg-[#343a4D] text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,0 V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor" />
          </svg>
        </div>

        <section className="relative py-20 max-w-4xl mx-auto text-center px-4">
          <div className="inline-flex items-center mb-5 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold tracking-wide">
            CAREERS AT <span className="font-linkbay ml-1">LINKBAY-CMS</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
            Build durable B2B software.<br />
            <span className="text-[#ff5758]">Ship things that matter.</span>
          </h1>

          <p className="text-lg text-blue-100 max-w-2xl mx-auto leading-relaxed">
            We are building commerce infrastructure for digital agencies — a platform they use to run
            every client store from one central place, under their own brand, on a subscription model.
            Early stage. Real product. Serious engineering direction.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
            <a
              href="#open-roles"
              className="bg-[#ff5758] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#e04e4f] transition-colors"
            >
              {positions.length > 0
                ? `${positions.length} open role${positions.length !== 1 ? "s" : ""}`
                : "See roles"}
            </a>
            <a
              href="#how-we-work"
              className="border-2 border-white/60 text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
            >
              How we work
            </a>
          </div>
        </section>
      </div>

      {/* Why join */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[#343a4D] mb-3">Why join LinkBay</h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            We are a small team building a product with a clear commercial purpose.
            Here is what that means in practice.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: "🎯",
              title: "Real product ownership",
              body: "You own what you build. No ticket factories. If something ships badly, you fix it. If it ships well, you see it in production.",
            },
            {
              icon: "⚙️",
              title: "Meaningful early-stage impact",
              body: "The platform is functional and used by real agencies. There is existing code to work with — and plenty left to build and improve.",
            },
            {
              icon: "🌍",
              title: "Remote-first",
              body: "The team works remotely. We care about clear async communication and reliable output, not presence in a specific timezone or city.",
            },
            {
              icon: "🔧",
              title: "Focus on durability",
              body: "We build things that last. Maintainability over shortcuts. Clarity over clever abstractions. We do not chase framework trends for their own sake.",
            },
          ].map((item) => (
            <div key={item.title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4 text-2xl">
                {item.icon}
              </div>
              <h3 className="font-semibold text-[#343a4D] mb-2">{item.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How we work */}
      <section id="how-we-work" className="bg-[#343a4D] text-white py-16">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-3">How we work</h2>
          <p className="text-blue-200 text-center mb-12 max-w-xl mx-auto">
            Our operating principles are simple and non-negotiable.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Clarity over noise",
                body: "We write clear tickets, have focused discussions, and document decisions. Ambiguity is a bug, not a feature.",
              },
              {
                title: "Maintainability over hype",
                body: "We pick the right tool for the job — not the fashionable one. The stack is Laravel, Next.js, PostgreSQL, Redis, Docker, and Traefik.",
              },
              {
                title: "Practical execution over vanity",
                body: "We ship things that agencies can use. We measure success by actual usage, not deployment counts or story points.",
              },
            ].map((item) => (
              <div key={item.title} className="border border-white/10 rounded-2xl p-6">
                <h3 className="font-semibold mb-3 text-[#ff5758]">{item.title}</h3>
                <p className="text-blue-100 text-sm leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>

          {/* Stack */}
          <div className="mt-12 border-t border-white/10 pt-10">
            <p className="text-center text-blue-200 text-sm mb-5 uppercase tracking-wide font-medium">
              Core technology stack
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {[
                "Laravel", "PHP", "PostgreSQL", "Redis",
                "Next.js", "React", "TypeScript", "Tailwind CSS",
                "Docker", "Traefik", "Stripe", "Filament",
              ].map((tech) => (
                <span
                  key={tech}
                  className="px-4 py-1.5 bg-white/10 rounded-full text-sm font-medium text-white/90"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Open roles — live from backend */}
      <section id="open-roles" className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-[#343a4D] mb-3">Open roles</h2>
          <p className="text-gray-600">
            All roles are remote. We value output over office hours.
          </p>
        </div>

        <RolesSection positions={positions} applyBaseUrl={API_BASE} />
      </section>

      {/* Hiring process */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-[#343a4D] text-center mb-3">
            Hiring process
          </h2>
          <p className="text-gray-600 text-center mb-12">
            Four steps. No surprises.
          </p>

          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-6">
            {[
              {
                step: "1",
                title: "Application",
                body: "Submit your CV and a short note on what you have built and why you are interested in this specific role.",
              },
              {
                step: "2",
                title: "Intro call",
                body: "A 30-minute conversation to understand your background, how you work, and answer questions about the product.",
              },
              {
                step: "3",
                title: "Technical review",
                body: "A practical exercise or code review relevant to the role. We do not ask you to solve whiteboard puzzles.",
              },
              {
                step: "4",
                title: "Founder call",
                body: "A direct conversation to align on expectations, working style, and what the role will look like day-to-day.",
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-11 h-11 bg-[#ff5758] rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">{item.step}</span>
                </div>
                <h3 className="font-semibold text-[#343a4D] mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-10 text-white">
          <h2 className="text-2xl font-bold mb-3">Don&rsquo;t see the right role?</h2>
          <p className="text-blue-100 mb-8 max-w-lg mx-auto">
            If you build serious B2B software and care about the problem we are solving,
            introduce yourself. We read every message.
          </p>
          <a
            href="mailto:info@linkbay-cms.com?subject=Spontaneous application"
            className="inline-block px-8 py-3 bg-white text-[#343a4D] font-bold rounded-lg hover:bg-gray-100 transition-colors"
          >
            Introduce yourself
          </a>
        </div>
      </section>

    </main>
  );
}
