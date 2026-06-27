import Link from 'next/link'
import Image from 'next/image'

interface HeroSettings {
  title?: string
  subtitle?: string
  cta_label?: string
  cta_url?: string
  image_url?: string
  overlay_opacity?: number
  text_color?: 'light' | 'dark'
  min_height?: string
}

export default function HeroBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as HeroSettings
  const textClass = s.text_color === 'dark' ? 'text-gray-900' : 'text-white'

  return (
    <section
      className="relative flex items-center justify-center overflow-hidden"
      style={{ minHeight: s.min_height ?? '70vh' }}
      aria-label={s.title ?? 'Hero'}
    >
      {s.image_url && (
        <Image
          src={s.image_url}
          alt=""
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
      )}
      {s.image_url && (
        <div
          className="absolute inset-0 bg-black"
          style={{ opacity: s.overlay_opacity ?? 0.4 }}
          aria-hidden="true"
        />
      )}
      <div className={`relative z-10 px-6 text-center ${textClass}`}>
        {s.title && (
          <h1 className="text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            {s.title}
          </h1>
        )}
        {s.subtitle && (
          <p className="mx-auto mt-4 max-w-2xl text-lg opacity-90">{s.subtitle}</p>
        )}
        {s.cta_label && s.cta_url && (
          <Link
            href={s.cta_url}
            className="mt-8 inline-block rounded-xl bg-[var(--color-primary,#111)] px-8 py-3.5 text-sm font-semibold text-white shadow-lg transition-opacity hover:opacity-90"
          >
            {s.cta_label}
          </Link>
        )}
      </div>
    </section>
  )
}
