import { useEffect } from 'react';

interface SEOConfig {
  title?: string;
  description?: string;
  keywords?: string;
  ogImage?: string;
  ogType?: 'website' | 'article';
  noindex?: boolean;
}

/**
 * Hook completo ma semplice per SEO dinamica
 * Include: title, description, keywords, Open Graph, robots
 * 
 * @example
 * ```tsx
 * function ProductPage() {
 *   useAdvancedSEO({
 *     title: "Prodotto - Il Meglio",
 *     description: "Descrizione dettagliata del prodotto",
 *     keywords: "prodotto, vendita, qualità",
 *     ogImage: "/product-image.jpg",
 *     ogType: "article"
 *   });
 * 
 *   return <div>Product content...</div>;
 * }
 * ```
 */
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
    const baseUrl = window.location.origin;
    
    // Helper per creare/aggiornare meta tag
    const updateMetaTag = (selector: string, content: string) => {
      let element = document.querySelector(selector) as HTMLMetaElement;
      if (!element) {
        element = document.createElement('meta');
        if (selector.includes('property=')) {
          element.setAttribute('property', selector.match(/property="([^"]+)"/)?.[1] || '');
        } else {
          element.setAttribute('name', selector.match(/name="([^"]+)"/)?.[1] || '');
        }
        document.head.appendChild(element);
      }
      element.setAttribute('content', content);
    };

    // Titolo
    if (title) {
      document.title = `${title} | ${siteName}`;
      updateMetaTag('meta[property="og:title"]', `${title} | ${siteName}`);
    }

    // Descrizione
    if (description) {
      updateMetaTag('meta[name="description"]', description);
      updateMetaTag('meta[property="og:description"]', description);
    }

    // Keywords
    if (keywords) {
      updateMetaTag('meta[name="keywords"]', keywords);
    }

    // Open Graph
    updateMetaTag('meta[property="og:type"]', ogType);
    updateMetaTag('meta[property="og:site_name"]', siteName);
    updateMetaTag('meta[property="og:url"]', window.location.href);
    updateMetaTag('meta[property="og:image"]', `${baseUrl}${ogImage}`);

    // Robots
    updateMetaTag('meta[name="robots"]', noindex ? 'noindex, nofollow' : 'index, follow');

    // Canonical URL
    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', window.location.href);
    
  }, [title, description, keywords, ogImage, ogType, noindex]);
};

export default useAdvancedSEO;