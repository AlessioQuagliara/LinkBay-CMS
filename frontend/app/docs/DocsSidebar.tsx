'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, BookOpen, Layers, Server } from 'lucide-react';

const sections = [
  {
    label: 'Getting Started',
    href: '/docs/getting-started',
    icon: BookOpen,
  },
  {
    label: 'Architecture',
    href: '/docs/architecture',
    icon: Layers,
  },
  {
    label: 'Self-Hosting',
    href: '/docs/self-hosting',
    icon: Server,
  },
];

export const DocsSidebar: React.FC = () => {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + '/');

  return (
    <>
      {/* Mobile toggle */}
      <div className="lg:hidden mb-6">
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-[#343a4D] bg-white border border-gray-200 rounded-xl shadow-sm hover:border-[#ff5758] hover:text-[#ff5758] transition-all duration-300"
        >
          {open ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          Documentation menu
        </button>

        {open && (
          <nav className="mt-3 bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            {sections.map((section) => {
              const Icon = section.icon;
              const active = isActive(section.href);
              return (
                <Link
                  key={section.href}
                  href={section.href}
                  onClick={() => setOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all duration-200 no-underline border-l-4 ${
                    active
                      ? 'bg-red-50 text-[#ff5758] border-[#ff5758]'
                      : 'text-[#343a4D] border-transparent hover:bg-gray-50 hover:text-[#ff5758]'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {section.label}
                </Link>
              );
            })}
          </nav>
        )}
      </div>

      {/* Desktop sidebar */}
      <aside className="hidden lg:block w-56 shrink-0">
        <div className="sticky top-28">
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-4 px-3">
            Documentation
          </p>
          <nav className="space-y-1">
            {sections.map((section) => {
              const Icon = section.icon;
              const active = isActive(section.href);
              return (
                <Link
                  key={section.href}
                  href={section.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 no-underline ${
                    active
                      ? 'bg-red-50 text-[#ff5758]'
                      : 'text-[#343a4D] hover:bg-gray-100 hover:text-[#ff5758]'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-[#ff5758]' : 'text-gray-400'}`} />
                  {section.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-8 px-3">
            <div className="p-4 bg-red-50 rounded-xl border border-red-100">
              <p className="text-xs font-semibold text-[#ff5758] mb-1">Beta</p>
              <p className="text-xs text-gray-600 leading-relaxed">
                LinkBay is in private beta. Reach out on{' '}
                <a
                  href="/contact"
                  className="text-[#ff5758] hover:underline"
                >
                  the contact page
                </a>{' '}
                to request access.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
