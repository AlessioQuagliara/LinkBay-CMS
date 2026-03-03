import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://linkbay-cms.com';
  
  const routes = [
    '',
    '/features',
    '/pricing',
    '/about',
    '/contact',
    '/api-docs',
    '/blog',
    '/work-with-us',
    '/marketplace',
    '/privacy',
    '/terms',
    '/cookie-policy',
  ];

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: route === '' ? 'daily' : 'weekly',
    priority: route === '' ? 1.0 : 0.8,
  }));
}
