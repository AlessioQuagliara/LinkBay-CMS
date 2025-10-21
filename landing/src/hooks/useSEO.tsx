import { Helmet } from 'react-helmet-async';

export interface SEOConfig {
  title?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  url?: string;
  type?: 'website' | 'article' | 'product' | 'profile';
  siteName?: string;
  locale?: string;
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  section?: string;
  tags?: string[];
  noindex?: boolean;
  nofollow?: boolean;
  canonical?: string;
  jsonLd?: object;
}

interface SEODefaults {
  siteName: string;
  defaultTitle: string;
  defaultDescription: string;
  defaultImage: string;
  defaultUrl: string;
  twitterHandle: string;
  locale: string;
}

const SEO_DEFAULTS: SEODefaults = {
  siteName: 'LinkBay CMS',
  defaultTitle: 'LinkBay CMS - La Piattaforma per Agenzie Web',
  defaultDescription: 'Gestisci tutti i siti web dei tuoi clienti da un\'unica dashboard. CMS multi-tenant progettato per agenzie web moderne.',
  defaultImage: '/logo.svg',
  defaultUrl: process.env.VITE_SITE_URL || 'http://localhost:3001',
  twitterHandle: '@linkbaycms',
  locale: 'it_IT'
};

export const useSEO = (config: SEOConfig = {}) => {
  const {
    title,
    description = SEO_DEFAULTS.defaultDescription,
    keywords = [],
    image = SEO_DEFAULTS.defaultImage,
    url,
    type = 'website',
    siteName = SEO_DEFAULTS.siteName,
    locale = SEO_DEFAULTS.locale,
    author,
    publishedTime,
    modifiedTime,
    section,
    tags = [],
    noindex = false,
    nofollow = false,
    canonical,
    jsonLd
  } = config;

  const finalTitle = title ? `${title} | ${siteName}` : SEO_DEFAULTS.defaultTitle;
  const fullUrl = url ? `${SEO_DEFAULTS.defaultUrl}${url}` : SEO_DEFAULTS.defaultUrl;
  const fullImage = image.startsWith('http') ? image : `${SEO_DEFAULTS.defaultUrl}${image}`;
  const canonicalUrl = canonical ? `${SEO_DEFAULTS.defaultUrl}${canonical}` : fullUrl;
  const robotsContent = `${noindex ? 'noindex' : 'index'}, ${nofollow ? 'nofollow' : 'follow'}`;
  const keywordsString = keywords.join(', ') || undefined;

  return (
    <Helmet>
      {/* Basic meta tags */}
      <title>{finalTitle}</title>
      <meta name="description" content={description} />
      {keywordsString && <meta name="keywords" content={keywordsString} />}
      {author && <meta name="author" content={author} />}
      <meta name="robots" content={robotsContent} />
      <link rel="canonical" href={canonicalUrl} />
      
      {/* Open Graph meta tags */}
      <meta property="og:title" content={finalTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={fullImage} />
      <meta property="og:url" content={fullUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content={siteName} />
      <meta property="og:locale" content={locale} />
      
      {/* Article specific meta tags */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && author && (
        <meta property="article:author" content={author} />
      )}
      {type === 'article' && section && (
        <meta property="article:section" content={section} />
      )}
      {type === 'article' && tags.map((tag, index) => (
        <meta key={index} property="article:tag" content={tag} />
      ))}
      
      {/* Twitter Card meta tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content={SEO_DEFAULTS.twitterHandle} />
      <meta name="twitter:title" content={finalTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={fullImage} />
      
      {/* JSON-LD structured data */}
      {jsonLd && (
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      )}
    </Helmet>
  );
};

export const useOrganizationJsonLd = () => ({
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "LinkBay CMS",
  "url": SEO_DEFAULTS.defaultUrl,
  "logo": `${SEO_DEFAULTS.defaultUrl}/logo.svg`,
  "description": SEO_DEFAULTS.defaultDescription,
  "sameAs": []
});

export const useWebsiteJsonLd = () => ({
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": SEO_DEFAULTS.siteName,
  "url": SEO_DEFAULTS.defaultUrl,
  "description": SEO_DEFAULTS.defaultDescription,
  "potentialAction": {
    "@type": "SearchAction",
    "target": `${SEO_DEFAULTS.defaultUrl}/search?q={search_term_string}`,
    "query-input": "required name=search_term_string"
  }
});

export const useBreadcrumbJsonLd = (items: Array<{ name: string; url: string }>) => ({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": items.map((item, index) => ({
    "@type": "ListItem",
    "position": index + 1,
    "name": item.name,
    "item": `${SEO_DEFAULTS.defaultUrl}${item.url}`
  }))
});

export default useSEO;