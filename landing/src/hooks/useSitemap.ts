export interface SitemapEntry {
  url: string;
  lastmod?: string;
  priority?: number;
  changefreq?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
}

export const useSitemap = () => {
  // FIX: Usa sempre il dominio di produzione per Google
  const getBaseUrl = () => {
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      return window.location.origin;
    }
    return 'https://www.linkbay-cms.com';
  };

  const staticRoutes: SitemapEntry[] = [
    { url: '/', priority: 1.0, changefreq: 'weekly' },
    { url: '/features', priority: 0.8, changefreq: 'monthly' },
    { url: '/pricing', priority: 0.8, changefreq: 'monthly' },
    { url: '/about', priority: 0.6, changefreq: 'monthly' },
    { url: '/contact', priority: 0.6, changefreq: 'monthly' },
    { url: '/privacy', priority: 0.2, changefreq: 'yearly' },
    { url: '/terms', priority: 0.2, changefreq: 'yearly' }
  ];

  const generateSitemapXml = (entries: SitemapEntry[]): string => {
    const baseUrl = getBaseUrl();
    const today = new Date().toISOString().split('T')[0];
    
    const urlElements = entries.map(entry => `  <url>
    <loc>${baseUrl}${entry.url}</loc>
    <lastmod>${entry.lastmod || today}</lastmod>
    <changefreq>${entry.changefreq || 'monthly'}</changefreq>
    <priority>${entry.priority || 0.5}</priority>
  </url>`).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlElements}
</urlset>`;
  };

  const generateFullSitemap = async (): Promise<string> => {
    return generateSitemapXml(staticRoutes);
  };

  return {
    staticRoutes,
    generateSitemapXml,
    generateFullSitemap
  };
};