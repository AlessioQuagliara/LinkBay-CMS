export interface ThemeData {
  key: string;
  name: string;
  tagline: string;
  useCase: string;
  palette: {
    primary: string;
    accent: string;
    surface: string;
    text: string;
  };
}

export function ThemeCard({ theme }: { theme: ThemeData }) {
  return (
    <article
      className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex flex-col"
      aria-label={`${theme.name} — premium theme`}
    >
      {/* Palette preview — communicates the theme's mood at a glance */}
      <div
        className="relative h-32 select-none"
        style={{ backgroundColor: theme.palette.surface }}
        aria-hidden="true"
      >
        {/* Header bar */}
        <div
          className="absolute inset-x-0 top-0 h-8"
          style={{ backgroundColor: theme.palette.primary }}
        />
        {/* Accent circle */}
        <div
          className="absolute top-12 left-5 h-14 w-14 rounded-full opacity-50"
          style={{ backgroundColor: theme.palette.accent }}
        />
        {/* Content line mockups */}
        <div
          className="absolute right-5 top-12 h-2.5 rounded-full opacity-20"
          style={{ backgroundColor: theme.palette.text, left: '5.5rem' }}
        />
        <div
          className="absolute right-10 h-2 rounded-full opacity-15"
          style={{ backgroundColor: theme.palette.text, top: '4.5rem', left: '5.5rem' }}
        />
        {/* Theme key watermark */}
        <span
          className="absolute bottom-2 right-3 font-mono text-[10px] uppercase tracking-widest opacity-30"
          style={{ color: theme.palette.text }}
        >
          {theme.key}
        </span>
      </div>

      {/* Card content */}
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h3 className="text-lg font-bold leading-tight text-gray-900">{theme.name}</h3>
          <span
            className="inline-flex shrink-0 items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700"
            aria-label="Premium"
          >
            <span aria-hidden="true">★</span> Premium
          </span>
        </div>
        <p className="mb-2 text-sm font-medium leading-snug text-gray-800">{theme.tagline}</p>
        <p className="text-sm leading-relaxed text-gray-500">{theme.useCase}</p>
      </div>
    </article>
  );
}
