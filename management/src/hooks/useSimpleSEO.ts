import { useEffect } from 'react';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  noindex?: boolean;
}

const updateMeta = (name: string, content: string) => {
  let meta = document.querySelector(`meta[name="${name}"]`) as HTMLMetaElement;
  if (!meta) {
    meta = document.createElement('meta');
    meta.name = name;
    document.head.appendChild(meta);
  }
  meta.content = content;
};

const updateRobots = (content: string) => {
  let meta = document.querySelector('meta[name="robots"]') as HTMLMetaElement;
  if (!meta) {
    meta = document.createElement('meta');
    meta.name = 'robots';
    document.head.appendChild(meta);
  }
  meta.content = content;
};

export const useSEO = ({ title, description, keywords, noindex = false }: SEOProps = {}) => {
  useEffect(() => {
    if (title) document.title = `${title} | LinkBay CMS`;
    if (description) updateMeta('description', description);
    if (keywords) updateMeta('keywords', keywords);

    // Per pagine riservate (login/register), impedisci indicizzazione
    if (noindex) {
      updateRobots('noindex, nofollow');
    } else {
      updateRobots('index, follow');
    }
  }, [title, description, keywords, noindex]);
};

export default useSEO;