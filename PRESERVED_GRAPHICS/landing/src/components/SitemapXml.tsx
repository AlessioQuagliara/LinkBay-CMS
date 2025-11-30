import React, { useEffect, useState } from 'react';
import { useSitemap } from '../hooks/useSitemap';

export const SitemapXml: React.FC = () => {
  const [xml, setXml] = useState<string>('');
  const { generateFullSitemap } = useSitemap();

  useEffect(() => {
    generateFullSitemap().then(content => {
      setXml(content);
      // Mostra XML formattato
      document.body.innerHTML = `<pre style="font-family: monospace; font-size: 12px; margin: 0; padding: 10px;">${content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
    }).catch(() => {
      setXml('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>');
    });
  }, []);

  return null;
};

export default SitemapXml;