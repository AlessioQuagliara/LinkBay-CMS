export interface RobotsConfig {
  allowAll?: boolean;
  disallowPaths?: string[];
  sitemapUrl?: string;
  crawlDelay?: number;
}

export const generateRobotsTxt = (config: RobotsConfig = {}): string => {
  const {
    allowAll = process.env.NODE_ENV === 'production',
    disallowPaths = [],
    sitemapUrl = `${window.location.origin}/sitemap.xml`,
    crawlDelay
  } = config;

  let robotsContent = 'User-agent: *\n';

  if (allowAll) {
    robotsContent += 'Allow: /\n';
  } else {
    robotsContent += 'Disallow: /\n';
  }

  // Aggiungi percorsi specifici da bloccare anche in produzione
  const defaultDisallowPaths = [
    '/api/*',
    '/admin/*',
    '/*.json',
    '/*.xml',
    '/login',
    '/register'
  ];

  const allDisallowPaths = [...defaultDisallowPaths, ...disallowPaths];
  
  if (allowAll && allDisallowPaths.length > 0) {
    robotsContent += '\n# Percorsi riservati\n';
    allDisallowPaths.forEach(path => {
      robotsContent += `Disallow: ${path}\n`;
    });
  }

  if (crawlDelay) {
    robotsContent += `\nCrawl-delay: ${crawlDelay}\n`;
  }

  robotsContent += `\nSitemap: ${sitemapUrl}\n`;

  // Aggiungi regole specifiche per bot comuni
  if (allowAll) {
    robotsContent += `
# Googlebot
User-agent: Googlebot
Allow: /

# Bingbot
User-agent: Bingbot
Allow: /

# Social Media Bots
User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /
`;
  }

  return robotsContent;
};

export const useRobots = () => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  const getDefaultConfig = (): RobotsConfig => ({
    allowAll: !isDevelopment,
    disallowPaths: isDevelopment ? ['/'] : ['/api/*', '/admin/*'],
    sitemapUrl: `${window.location.origin}/sitemap.xml`,
    crawlDelay: isDevelopment ? 86400 : undefined // 1 giorno in dev
  });

  return {
    generateRobotsTxt,
    getDefaultConfig,
    isDevelopment
  };
};