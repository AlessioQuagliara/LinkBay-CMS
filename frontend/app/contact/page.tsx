import { Mail, Send, ArrowRight } from "lucide-react";

export default function ContactPage() {
  const contactFormUrl =
    (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://app.linkbay-cms.test") + "/contact";

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <main className="max-w-5xl mx-auto py-16 px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="text-center mb-14">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-[#ff5758] rounded-2xl flex items-center justify-center shadow-lg">
              <Mail className="w-8 h-8 text-white" />
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-[#343a4D] mb-4">
            Talk to the <span className="font-linkbay">LinkBay-CMS</span> team
          </h1>

          <div className="w-16 h-1 bg-[#ff5758] mx-auto mb-6" />

          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Tell us about your agency and how you run client stores today.
            We&rsquo;ll see if <span className="font-linkbay">LinkBay-CMS</span> is a fit and what a
            white-label setup could look like for your portfolio.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">

          {/* Left: contact info */}
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold text-[#343a4D] mb-4">Get in touch</h2>
              <p className="text-gray-600 leading-relaxed">
                We respond within one business day. If you manage multiple client stores
                or are evaluating infrastructure for your agency, that&rsquo;s exactly the kind
                of conversation we want to have.
              </p>
            </div>

            <div className="flex items-start gap-4 p-5 bg-white rounded-2xl shadow-sm border border-gray-100">
              <div className="bg-[#ff5758] p-3 rounded-lg shrink-0">
                <Mail className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-[#343a4D] mb-0.5">Email</p>
                <a href="mailto:info@linkbay-cms.com" className="text-[#ff5758] hover:underline">
                  info@linkbay-cms.com
                </a>
                <p className="text-sm text-gray-500 mt-0.5">Response within one business day</p>
              </div>
            </div>

            {/* What to tell us */}
            <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
              <h3 className="font-bold text-[#343a4D] mb-4 text-sm uppercase tracking-wide">
                Useful things to include
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                {[
                  "How many client stores you manage today (or expect to)",
                  "Whether white-label delivery matters to you",
                  "How you currently charge clients (one-off, retainer, or subscription)",
                  "Any specific integrations or constraints we should know about",
                ].map((t) => (
                  <li key={t} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-[#ff5758] rounded-full mt-1.5 shrink-0" />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Right: CTA card linking to Laravel form */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 flex flex-col">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-[#ff5758] p-2 rounded-lg">
                <Send className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-xl font-bold text-[#343a4D]">Send a message</h2>
            </div>

            <p className="text-gray-600 mb-4 leading-relaxed">
              Fill in a short form — your name, agency, email, and what you&rsquo;d like to discuss.
              We&rsquo;ll get back to you directly.
            </p>

            <ul className="space-y-2 text-sm text-gray-500 mb-8">
              {[
                "No sales pressure — just a direct conversation",
                "Straightforward answers about pricing and fit",
                "We respond within one business day",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-[#ff5758] rounded-full mt-1.5 shrink-0" />
                  {t}
                </li>
              ))}
            </ul>

            <div className="mt-auto">
              <a
                href={contactFormUrl}
                className="w-full py-3.5 px-6 font-semibold rounded-xl bg-[#ff5758] text-white hover:bg-[#e04e4e] shadow-md transition-all duration-300 flex items-center justify-center gap-2 no-underline"
              >
                Open contact form
                <ArrowRight className="w-4 h-4" />
              </a>
              <p className="text-xs text-gray-400 text-center mt-4">
                We don&rsquo;t share your information with third parties.
              </p>
            </div>
          </div>
        </div>

        {/* Direct email fallback */}
        <div className="text-center mt-14 p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
          <p className="text-gray-600 mb-2">Prefer to write directly?</p>
          <a
            href="mailto:info@linkbay-cms.com"
            className="text-xl font-bold text-[#ff5758] hover:text-[#e04e4e] transition-colors"
          >
            info@linkbay-cms.com
          </a>
          <p className="text-gray-400 text-sm mt-1">Response guaranteed within one business day</p>
        </div>

      </main>
    </div>
  );
}
