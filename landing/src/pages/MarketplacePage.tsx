import React, { useState } from 'react';
import { useSEO } from "../hooks/useSimpleSEO";

// Tipo per gli item del marketplace
interface MarketplaceItem {
  id: number;
  title: string;
  description: string;
  price: number;
  category: 'theme' | 'plugin';
  rating: number;
  imageUrl: string;
}

const MarketplacePage: React.FC = () => {
  // SEO per il marketplace
  useSEO({
    title: "Marketplace",
    description: "Esplora temi e plugin per LinkBay CMS. Estendi le funzionalità del tuo CMS con componenti professionali sviluppati dalla community.",
    keywords: "marketplace cms, temi linkbay, plugin agenzia, estensioni web, componenti cms"
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'theme' | 'plugin'>('all');

  // Dummy data - sostituire con dati reali
  const marketplaceItems: MarketplaceItem[] = [
    {
      id: 1,
      title: 'Theme Moderno E-Commerce',
      description: 'Template responsive con focus sulla conversione',
      price: 89,
      category: 'theme',
      rating: 4.8,
      imageUrl: '/placeholder-theme.jpg'
    },
    {
      id: 2,
      title: 'Plugin Pagamenti Avanzati',
      description: 'Estensione per gateway pagamenti multipli',
      price: 49,
      category: 'plugin',
      rating: 4.5,
      imageUrl: '/placeholder-plugin.jpg'
    },
    // Aggiungi altri item qui...
  ];

  const filteredItems = marketplaceItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-[#343a4D] mb-4">
            Marketplace LinkBay-CMS
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Scopri temi e plugin premium per potenziare i tuoi e-commerce. 
            Tutti i prodotti sono testati e ottimizzati per la piattaforma.
          </p>
        </div>

        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
            <div className="w-full md:w-1/2">
              <input
                type="text"
                placeholder="Cerca temi o plugin..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff5758]"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="flex gap-4">
              <button
                className={`px-4 py-2 rounded-lg ${
                  selectedCategory === 'all' 
                    ? 'bg-[#ff5758] text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
                onClick={() => setSelectedCategory('all')}
              >
                Tutti
              </button>
              <button
                className={`px-4 py-2 rounded-lg ${
                  selectedCategory === 'theme' 
                    ? 'bg-[#ff5758] text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
                onClick={() => setSelectedCategory('theme')}
              >
                Temi
              </button>
              <button
                className={`px-4 py-2 rounded-lg ${
                  selectedCategory === 'plugin' 
                    ? 'bg-[#ff5758] text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
                onClick={() => setSelectedCategory('plugin')}
              >
                Plugin
              </button>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            {filteredItems.length} prodotti trovati
          </p>
        </div>

        {/* Marketplace Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredItems.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-400">Anteprima</span>
                {/* <img src={item.imageUrl} alt={item.title} className="w-full h-full object-cover" /> */}
              </div>
              
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-semibold text-[#343a4D]">{item.title}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    item.category === 'theme' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {item.category === 'theme' ? 'Tema' : 'Plugin'}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4">{item.description}</p>
                
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <span className="text-yellow-400">★</span>
                    <span className="ml-1 text-gray-700">{item.rating}</span>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-2xl font-bold text-[#ff5758]">€{item.price}</p>
                    <button className="mt-2 bg-[#ff5758] text-white px-4 py-2 rounded-lg hover:bg-[#e04e4e] transition-colors">
                      Acquista Ora
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Nessun prodotto trovato con i filtri attuali.</p>
            <button 
              className="mt-4 text-[#ff5758] hover:underline"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
            >
              Ripristina filtri
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketplacePage;