import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useSEO } from "../hooks/useSimpleSEO";

type BlogPost = {
  id: number;
  title: string;
  excerpt: string;
  date: string;
  author: string;
  category: string;
  readTime: string;
  image: string;
  featured?: boolean;
};

const blogPosts: BlogPost[] = [
  {
    id: 1,
    title: "Architettura Multitenant: Perché è il Futuro dell'E-commerce B2B",
    excerpt: "Scopri come l'architettura schema-per-tenant di LinkBay-CMS rivoluziona la gestione di multiple piattaforme e-commerce per le agenzie digitali.",
    date: "15 Luglio 2025",
    author: "Alessio Quagliara",
    category: "Tecnologia",
    readTime: "8 min",
    image: "🌊",
    featured: true
  },
  {
    id: 2,
    title: "White-Labeling: Come Aumentare il Valore del Tuo Brand Agency",
    excerpt: "Guida completa per implementare soluzioni white-label che fidelizzano i clienti e aumentano le revenue ricorrenti.",
    date: "12 Luglio 2025",
    author: "Nicola Pavan",
    category: "Business",
    readTime: "6 min",
    image: "⚓"
  },
  {
    id: 3,
    title: "GDPR e E-commerce: Tutto ciò che le Agenzie Devono Sapere",
    excerpt: "Normative privacy, cookie policy e compliance europea per piattaforme e-commerce multitenant.",
    date: "8 Luglio 2025",
    author: "Team Legal",
    category: "Compliance",
    readTime: "10 min",
    image: "🛡️"
  },
  {
    id: 4,
    title: "Dashboard Centralizzata: Gestire 100+ Store Senza Sforzo",
    excerpt: "Case study su come un'agenzia ha ridotto del 70% il tempo di gestione tecnica migrando su LinkBay-CMS.",
    date: "5 Luglio 2025",
    author: "Juan Romero",
    category: "Case Study",
    readTime: "7 min",
    image: "📊"
  },
  {
    id: 5,
    title: "Marketplace Interno: Nuova Fonte di Revenue per le Agency",
    excerpt: "Come monetizzare vendendo temi e plugin ai clienti attraverso il marketplace integrato.",
    date: "2 Luglio 2025",
    author: "Alessio Quagliara",
    category: "Monetizzazione",
    readTime: "5 min",
    image: "💼"
  },
  {
    id: 6,
    title: "Automazione SSL e Domini: Zero Configurazione Manuale",
    excerpt: "Tecnologie e processi dietro la gestione automatica di certificati e domini per migliaia di store.",
    date: "28 Giugno 2025",
    author: "Team Sviluppo",
    category: "Tecnologia",
    readTime: "4 min",
    image: "🔒"
  }
];

const categories = ["Tutti", "Tecnologia", "Business", "Case Study", "Monetizzazione", "Compliance"];

export const BlogPage: React.FC = () => {
  // SEO per il blog
  useSEO({
    title: "Blog",
    description: "Guide, tutorial e insights per agenzie web. Scopri come ottimizzare la gestione dei siti dei tuoi clienti con LinkBay CMS.",
    keywords: "blog cms, guide agenzia web, tutorial gestione siti, insights digitali, best practices"
  });

  const [selectedCategory, setSelectedCategory] = useState("Tutti");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredPosts = blogPosts.filter(post => {
    const matchesCategory = selectedCategory === "Tutti" || post.category === selectedCategory;
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const featuredPost = blogPosts.find(post => post.featured);

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">
      {/* Header Hero Section */}
      <div className="relative bg-[#343a4D] text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,0 V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
          </svg>
        </div>
        
        <section className="relative py-16 max-w-4xl mx-auto text-center px-4">
          <div className="inline-flex items-center mb-4 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold">
            <span className="mr-2">📚</span> BLOG LINKBAY-CMS
          </div>
          
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
            Naviga tra le <span className="text-[#ff5758]">Idee</span> per il Tuo Successo
          </h1>
          
          <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-6">
            Approfondimenti tecnici, strategie business e best practice per agenzie che vogliono dominare il mercato e-commerce.
          </p>
          
          {/* Search Bar */}
          <div className="max-w-md mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Cerca articoli, guide, tutorial..."
                className="w-full px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <span className="absolute right-3 top-3 text-gray-400">🔍</span>
            </div>
          </div>
        </section>
      </div>

      {/* Featured Post */}
      {featuredPost && (
        <section className="max-w-6xl mx-auto px-4 py-12">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
            <div className="md:flex">
              <div className="md:w-2/3 p-8">
                <div className="inline-flex items-center bg-[#ff5758] text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
                  <span className="mr-2">⭐</span> IN EVIDENZA
                </div>
                <h2 className="text-3xl font-bold text-[#343a4D] mb-4">{featuredPost.title}</h2>
                <p className="text-gray-700 mb-6 text-lg">{featuredPost.excerpt}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>{featuredPost.author}</span>
                    <span>•</span>
                    <span>{featuredPost.date}</span>
                    <span>•</span>
                    <span>{featuredPost.readTime} lettura</span>
                  </div>
                  <Link 
                    to={`/blog/${featuredPost.id}`}
                    className="bg-[#343a4D] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#ff5758] transition-colors"
                  >
                    Leggi Articolo →
                  </Link>
                </div>
              </div>
              <div className="md:w-1/3 bg-gradient-to-br from-[#343a4D] to-[#ff5758] flex items-center justify-center p-8">
                <span className="text-6xl">{featuredPost.image}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Categories Filter */}
      <section className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-2 justify-center">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full font-semibold transition-colors ${
                selectedCategory === category
                  ? "bg-[#ff5758] text-white"
                  : "bg-white text-gray-700 hover:bg-gray-100"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      {/* Blog Posts Grid */}
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredPosts.map(post => (
            <article key={post.id} className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
              <div className="bg-gradient-to-br from-[#343a4D] to-[#ff5758] h-32 flex items-center justify-center">
                <span className="text-4xl">{post.image}</span>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-semibold text-[#ff5758]">{post.category}</span>
                  <span className="text-sm text-gray-500">{post.readTime}</span>
                </div>
                <h3 className="text-xl font-bold text-[#343a4D] mb-3 line-clamp-2">{post.title}</h3>
                <p className="text-gray-600 mb-4 line-clamp-3">{post.excerpt}</p>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    <div>{post.author}</div>
                    <div>{post.date}</div>
                  </div>
                  <Link 
                    to={`/blog/${post.id}`}
                    className="text-[#ff5758] font-semibold hover:text-[#343a4D] transition-colors"
                  >
                    Leggi →
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>

        {filteredPosts.length === 0 && (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block">🔍</span>
            <h3 className="text-xl font-bold text-gray-700 mb-2">Nessun articolo trovato</h3>
            <p className="text-gray-600">Prova a modificare i filtri o la ricerca</p>
          </div>
        )}
      </section>

      {/* Newsletter CTA */}
      <section className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">⚓ Non Perdere Nemmeno un Articolo</h2>
          <p className="mb-6 text-blue-100">Iscriviti alla newsletter per ricevere gli ultimi contenuti direttamente nella tua inbox</p>
          
          <div className="max-w-md mx-auto flex flex-col sm:flex-row gap-4">
            <input 
              type="email" 
              placeholder="La tua email professionale" 
              className="flex-1 px-4 py-3 rounded-lg text-gray-900"
            />
            <button className="px-6 py-3 bg-white text-[#343a4D] font-bold rounded-lg hover:bg-gray-100 transition-colors">
              Iscriviti
            </button>
          </div>
          
          <p className="text-sm text-blue-200 mt-4">
            Niente spam, solo contenuti di valore. Cancellazione sempre possibile.
          </p>
        </div>
      </section>

      {/* Popular Tags */}
      <section className="max-w-4xl mx-auto px-4 py-8 text-center">
        <h3 className="text-lg font-semibold text-[#343a4D] mb-4">🔖 Argomenti Popolari</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {["Multitenancy", "White-label", "GDPR", "Dashboard", "Automazione", "Marketplace", "Sicurezza", "API", "Scalabilità", "B2B"].map(tag => (
            <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 cursor-pointer">
              #{tag}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
};

export default BlogPage;