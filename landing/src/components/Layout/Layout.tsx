import React from 'react';
import { Header } from '../Header';
import { Footer } from '../Footer';
import  Cookie  from '../Cookie';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      {/* aggiunto padding-top per evitare che l'header fisso copra il contenuto */}
      <main className="flex-1 pt-16 md:pt-20">
        {children}
      </main>
      <Cookie />
      <Footer />
    </div>
  );
};