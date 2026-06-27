interface TextSettings {
  content?: string
  align?: 'left' | 'center' | 'right'
  max_width?: string
}

export default function TextBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as TextSettings
  const alignClass = { left: 'text-left', center: 'text-center', right: 'text-right' }[s.align ?? 'left']

  return (
    <section className="mx-auto px-4 py-12 sm:px-6 lg:px-8" style={{ maxWidth: s.max_width ?? '800px' }}>
      {s.content && (
        <div
          className={`prose prose-gray max-w-none ${alignClass}`}
          dangerouslySetInnerHTML={{ __html: s.content }}
        />
      )}
    </section>
  )
}
