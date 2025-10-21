import { useEffect } from 'react';

interface SEOConfig {
  title?: string;
  description?: string;
  keywords?: string;
  ogImage?: string;
  ogType?: 'website' | 'article';
  noindex?: boolean;
}

const updateMeta = (attr: string, value: string, content: string) => {
  const selector = attr === 'property' ? `meta[property="${value}"]` : `meta[name="${value}"]`;
  let meta = document.querySelector(selector) as HTMLMetaElement;
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute(attr, value);
    document.head.appendChild(meta);
  }
  meta.content = content;
};

export const useAdvancedSEO = ({
  title,
  description,
  keywords,
  ogImage = "/logo.svg",
  ogType = "website",
  noindex = false
}: SEOConfig = {}) => {
  useEffect(() => {
    const siteName = "LinkBay CMS";
    const fullTitle = title ? `${title} | ${siteName}` : siteName;

    if (title) document.title = fullTitle;
    if (description) {
      updateMeta('name', 'description', description);
      updateMeta('property', 'og:description', description);
    }
    if (keywords) updateMeta('name', 'keywords', keywords);

    updateMeta('property', 'og:title', fullTitle);
    updateMeta('property', 'og:type', ogType);
    updateMeta('property', 'og:site_name', siteName);
    updateMeta('property', 'og:url', window.location.href);
    updateMeta('property', 'og:image', `${window.location.origin}${ogImage}`);
    updateMeta('name', 'robots', noindex ? 'noindex, nofollow' : 'index, follow');

    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = 'canonical';
      document.head.appendChild(canonical);
    }
    canonical.href = window.location.href;
  }, [title, description, keywords, ogImage, ogType, noindex]);
};

export default useAdvancedSEO;