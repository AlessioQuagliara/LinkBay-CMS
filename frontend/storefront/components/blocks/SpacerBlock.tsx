interface SpacerSettings {
  height?: string
}

export default function SpacerBlock({ settings }: { settings: Record<string, unknown> }) {
  const s = settings as SpacerSettings
  return <div style={{ height: s.height ?? '3rem' }} aria-hidden="true" />
}
