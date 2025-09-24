import React from 'react';
import { HelmetProvider } from 'react-helmet-async';

interface SEOProviderProps {
  children: React.ReactNode;
}

/**
 * Provider per react-helmet-async che gestisce la SEO dinamica
 * Deve wrappare l'intera app per funzionare correttamente
 */
export const SEOProvider: React.FC<SEOProviderProps> = ({ children }) => {
  return <HelmetProvider>{children}</HelmetProvider>;
};

export default SEOProvider;