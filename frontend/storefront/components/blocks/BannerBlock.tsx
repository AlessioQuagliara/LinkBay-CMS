import Link from 'next/link'

interface BannerSettings {
  message?: string
  background_color?: string
  text_color?: string
  cta_label?: string
  cta_url?: string
}

export default function BannerBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as BannerSettings

  return (
    <div
      className="w-full py-3 text-center text-sm font-medium"
      style={{
        backgroundColor: s.background_color ?? 'var(--color-primary, #111)',
        color: s.text_color ?? '#fff',
      }}
      role="banner"
    >
      {s.message}
      {s.cta_label && s.cta_url && (
        <Link href={s.cta_url} className="ml-3 underline hover:no-underline">
          {s.cta_label}
        </Link>
      )}
    </div>
  )
}
