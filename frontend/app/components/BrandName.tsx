import React from 'react';

interface BrandNameProps {
  /** Render ® superscript after the name. Use only on first occurrence per page. */
  registered?: boolean;
  /** HTML tag to use as wrapper. Defaults to span. */
  as?: keyof React.JSX.IntrinsicElements;
  className?: string;
}

/**
 * Renders the brand name "LinkBay-CMS" with optional registered trademark symbol.
 *
 * Use `registered={true}` only on the first visible occurrence per page
 * (navbar logo, hero heading, footer logo). Never in buttons, badges, or repeated copy.
 */
export function BrandName({ registered = false, as: Tag = 'span', className }: BrandNameProps) {
  const El = Tag as React.ElementType;

  return (
    <El className={className}>
      LinkBay-CMS
      {registered && (
        <sup
          aria-label="marchio registrato"
          className="text-[0.5em] align-super leading-none ml-px font-normal opacity-60"
        >
          ®
        </sup>
      )}
    </El>
  );
}
