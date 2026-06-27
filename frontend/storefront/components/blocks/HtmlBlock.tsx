interface HtmlSettings {
  html?: string
}

/** Renders raw HTML content from the CMS. Only used for trusted agency-authored content. */
export default function HtmlBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as HtmlSettings
  if (!s.html) return null

  return (
    <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* biome-ignore lint/security/noDangerouslySetInnerHtml: CMS content authored by trusted agency users */}
      <div dangerouslySetInnerHTML={{ __html: s.html }} />
    </section>
  )
}
