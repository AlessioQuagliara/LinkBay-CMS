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

  const defaultPaths = ['/api/*', '/admin/*', '/*.json', '/*.xml', '/login', '/register'];
  const allPaths = [...defaultPaths, ...disallowPaths];
  
  let content = `User-agent: *\n${allowAll ? 'Allow: /\n' : 'Disallow: /\n'}`;
  
  if (allowAll && allPaths.length > 0) {
    content += '\n# Percorsi riservati\n' + allPaths.map(p => `Disallow: ${p}`).join('\n') + '\n';
  }
  
  if (crawlDelay) content += `\nCrawl-delay: ${crawlDelay}\n`;
  content += `\nSitemap: ${sitemapUrl}\n`;
  
  if (allowAll) {
    content += '\n# Googlebot\nUser-agent: Googlebot\nAllow: /\n';
    content += '\n# Bingbot\nUser-agent: Bingbot\nAllow: /\n';
    content += '\n# Social Bots\nUser-agent: facebookexternalhit\nAllow: /\n';
    content += 'User-agent: Twitterbot\nAllow: /\n';
    content += 'User-agent: LinkedInBot\nAllow: /\n';
  }

  return content;
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