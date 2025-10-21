import { useEffect } from 'react';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
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

export const useSEO = ({ title, description, keywords }: SEOProps = {}) => {
  useEffect(() => {
    if (title) document.title = `${title} | LinkBay CMS`;
    if (description) updateMeta('description', description);
    if (keywords) updateMeta('keywords', keywords);
  }, [title, description, keywords]);
};

export default useSEO;