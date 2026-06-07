interface LogoMarkProps {
  variant?: 'dark' | 'white';
  className?: string;
  /** Render ® after the CMS badge. Use only on the first visible occurrence per page. */
  registered?: boolean;
}

/**
 * Brand wordmark rendered in HTML/CSS so the Electrolize font
 * (loaded by layout.tsx via next/font) always applies correctly.
 * Avoids SVG font-loading limitations when used in <img> tags.
 */
export function LogoMark({ variant = 'dark', className = '', registered = false }: LogoMarkProps) {
  const textColor = variant === 'white' ? '#ffffff' : '#343a4D';

  return (
    <span
      className={`inline-flex items-center gap-[0.28em] select-none ${className}`}
      style={{ fontFamily: 'var(--font-electrolize), Electrolize, monospace' }}
      aria-label={registered ? 'LinkBay-CMS marchio registrato' : 'LinkBay-CMS'}
    >
      {/* Wordmark */}
      <span
        className="text-[1.5em] leading-none tracking-tight font-normal"
        style={{ color: textColor }}
      >
        LinkBay
      </span>

      {/* Product badge — mirrors the red blob from the SVG logo */}
      <span
        className="text-[0.62em] px-[0.55em] py-[0.3em] rounded font-normal leading-none"
        style={{
          background: '#ff5758',
          color: '#ffffff',
          letterSpacing: '0.06em',
        }}
      >
        CMS
      </span>

      {/* Registered trademark — self-start aligns to the top of the flex container */}
      {registered && (
        <sup
          aria-label="marchio registrato"
          className="self-start text-[0.45em] leading-none font-normal mt-[0.2em] opacity-70"
          style={{ color: textColor }}
        >
          ®
        </sup>
      )}
    </span>
  );
}
