import React, { useEffect, useState } from 'react';
import { useSitemap } from '../hooks/useSitemap';

export const SitemapXml: React.FC = () => {
  const [sitemapContent, setSitemapContent] = useState<string>('');
  const { generateFullSitemap } = useSitemap();

  useEffect(() => {
    const generateSitemap = async () => {
      try {
        const xml = await generateFullSitemap();
        setSitemapContent(xml);
        
        // Imposta header Content-Type per XML
        document.querySelector('meta[name="content-type"]')?.setAttribute('content', 'application/xml');
      } catch (error) {
        console.error('Error generating sitemap:', error);
        setSitemapContent('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>');
      }
    };

    generateSitemap();
  }, [generateFullSitemap]);

  // Render come plain text invece che HTML
  useEffect(() => {
    if (sitemapContent) {
      // Sostituisci il contenuto della pagina con XML raw
      document.body.innerHTML = `<pre>${sitemapContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
      document.body.style.fontFamily = 'monospace';
      document.body.style.fontSize = '12px';
      document.body.style.margin = '0';
      document.body.style.padding = '10px';
    }
  }, [sitemapContent]);

  return null; // Il rendering avviene tramite DOM manipulation
};

export default SitemapXml;