import { useEffect } from 'react';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
}

/**
 * Hook semplice per cambiare title, description e keywords dinamicamente
 * Utilizza l'API nativa del DOM (più veloce di react-helmet)
 * 
 * @example
 * ```tsx
 * function HomePage() {
 *   useSEO({
 *     title: "Home - LinkBay CMS",
 *     description: "La piattaforma per agenzie web",
 *     keywords: "cms, agenzia, web, gestione siti"
 *   });
 * 
 *   return <div>Homepage content...</div>;
 * }
 * ```
 */
export const useSEO = ({ title, description, keywords }: SEOProps = {}) => {
  useEffect(() => {
    // Cambia il titolo
    if (title) {
      document.title = `${title} | LinkBay CMS`;
    }

    // Cambia o crea meta description
    if (description) {
      let metaDescription = document.querySelector('meta[name="description"]');
      if (!metaDescription) {
        metaDescription = document.createElement('meta');
        metaDescription.setAttribute('name', 'description');
        document.head.appendChild(metaDescription);
      }
      metaDescription.setAttribute('content', description);
    }

    // Cambia o crea meta keywords
    if (keywords) {
      let metaKeywords = document.querySelector('meta[name="keywords"]');
      if (!metaKeywords) {
        metaKeywords = document.createElement('meta');
        metaKeywords.setAttribute('name', 'keywords');
        document.head.appendChild(metaKeywords);
      }
      metaKeywords.setAttribute('content', keywords);
    }
  }, [title, description, keywords]);
};

export default useSEO;