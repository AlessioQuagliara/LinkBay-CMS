import type { Metadata } from 'next';
import { DocsSidebar } from './DocsSidebar';

export const metadata: Metadata = {
  title: {
    template: '%s — LinkBay Docs',
    default: 'Documentation — LinkBay',
  },
  description:
    'LinkBay-CMS documentation: getting started, architecture, and self-hosting guide.',
};

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex gap-10 lg:gap-14 items-start">
        <DocsSidebar />
        <div className="flex-1 min-w-0">{children}</div>
      </div>
    </div>
  );
}
