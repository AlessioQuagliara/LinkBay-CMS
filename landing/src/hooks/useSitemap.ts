import { useLocation } from 'react-router-dom';

export interface SitemapEntry {
  url: string;
  lastmod?: string;
  priority?: number;
  changefreq?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
}

export const useSitemap = () => {
  const baseUrl = window.location.origin;

  // Rotte statiche del landing con priorità SEO
  const staticRoutes: SitemapEntry[] = [
    { url: '/', priority: 1.0, changefreq: 'weekly' },
    { url: '/features', priority: 0.8, changefreq: 'monthly' },
    { url: '/pricing', priority: 0.8, changefreq: 'monthly' },
    { url: '/about', priority: 0.6, changefreq: 'monthly' },
    { url: '/contact', priority: 0.6, changefreq: 'monthly' },
    { url: '/api-docs', priority: 0.5, changefreq: 'weekly' },
    { url: '/blog', priority: 0.5, changefreq: 'daily' },
    { url: '/work-with-us', priority: 0.4, changefreq: 'monthly' },
    { url: '/marketplace', priority: 0.6, changefreq: 'weekly' },
    { url: '/login', priority: 0.3, changefreq: 'yearly' },
    { url: '/register', priority: 0.3, changefreq: 'yearly' },
    { url: '/privacy', priority: 0.2, changefreq: 'yearly' },
    { url: '/terms', priority: 0.2, changefreq: 'yearly' },
    { url: '/cookie-policy', priority: 0.2, changefreq: 'yearly' }
  ];

  const generateSitemapXml = (entries: SitemapEntry[]): string => {
    const urlElements = entries.map(entry => {
      const lastmod = entry.lastmod ? `    <lastmod>${entry.lastmod}</lastmod>` : '';
      const priority = entry.priority ? `    <priority>${entry.priority}</priority>` : '';
      const changefreq = entry.changefreq ? `    <changefreq>${entry.changefreq}</changefreq>` : '';
      
      return `  <url>
    <loc>${baseUrl}${entry.url}</loc>
${lastmod}
${changefreq}
${priority}
  </url>`;
    }).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlElements}
</urlset>`;
  };

  const getDynamicRoutes = async (): Promise<SitemapEntry[]> => {
    // TODO: Fetch da API backend per contenuti dinamici
    // Esempio: articoli blog, case studies, landing pages personalizzate
    try {
      // const response = await fetch('/api/sitemap-entries');
      // const dynamicEntries = await response.json();
      // return dynamicEntries;
      return [];
    } catch (error) {
      console.warn('Failed to fetch dynamic routes for sitemap:', error);
      return [];
    }
  };

  const generateFullSitemap = async (): Promise<string> => {
    const dynamicRoutes = await getDynamicRoutes();
    const allRoutes = [...staticRoutes, ...dynamicRoutes];
    
    // Aggiorna lastmod per tutte le rotte con data corrente
    const routesWithDate = allRoutes.map(route => ({
      ...route,
      lastmod: route.lastmod || new Date().toISOString().split('T')[0]
    }));

    return generateSitemapXml(routesWithDate);
  };

  return {
    staticRoutes,
    generateSitemapXml,
    getDynamicRoutes,
    generateFullSitemap
  };
};