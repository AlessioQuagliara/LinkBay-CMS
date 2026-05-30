"use client";

import { useState } from "react";
import Link from "next/link";

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
    title: "Managing Multiple Client Stores: How a Central Dashboard Changes the Game",
    excerpt: "How agencies running several client stores at once can reduce operational overhead and keep delivery consistent by working from a single control point.",
    date: "July 15, 2025",
    author: "Alessio Quagliara",
    category: "Business",
    readTime: "8 min",
    image: "🌊",
    featured: true
  },
  {
    id: 2,
    title: "White-Labeling for Agencies: Building Recurring Revenue Under Your Brand",
    excerpt: "A practical guide to delivering client stores under your own brand, setting up recurring subscriptions, and keeping the relationship in your hands.",
    date: "July 12, 2025",
    author: "Nicola Pavan",
    category: "Revenue",
    readTime: "6 min",
    image: "⚓"
  },
  {
    id: 3,
    title: "GDPR and E-commerce: What Agencies Need to Know",
    excerpt: "Privacy regulations, cookie compliance, and data handling requirements for agencies running stores on behalf of their clients.",
    date: "July 8, 2025",
    author: "Legal Team",
    category: "Compliance",
    readTime: "10 min",
    image: "🛡️"
  },
  {
    id: 4,
    title: "Central Dashboard: Managing Many Stores Without Operational Chaos",
    excerpt: "How centralising store management reduces the time spent on repetitive tasks and lets teams focus on delivery instead of coordination.",
    date: "July 5, 2025",
    author: "Juan Romero",
    category: "Case Study",
    readTime: "7 min",
    image: "📊"
  },
  {
    id: 5,
    title: "Building a Recurring Revenue Model for Your Agency",
    excerpt: "Moving from one-off builds to monthly client subscriptions: the operational and commercial logic behind running a store-as-a-service model.",
    date: "July 2, 2025",
    author: "Alessio Quagliara",
    category: "Revenue",
    readTime: "5 min",
    image: "💼"
  },
  {
    id: 6,
    title: "Automated SSL and Custom Domains: Less Manual Work Per Client",
    excerpt: "How automated domain verification and SSL provisioning removes a recurring setup burden when onboarding new client stores.",
    date: "June 28, 2025",
    author: "Dev Team",
    category: "Technology",
    readTime: "4 min",
    image: "🔒"
  }
];

const categories = ["All", "Technology", "Business", "Case Study", "Revenue", "Compliance"];

const renderTextWithLinkBayCMS = (text: string) => {
  const parts = text.split(/(LinkBay-CMS|LinkBay)/g);
  return parts.map((part, index) => {
    if (part === 'LinkBay-CMS' || part === 'LinkBay') {
      return <span key={index} className="font-linkbay">{part}</span>;
    }
    return part;
  });
};

export default function BlogPage() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredPosts = blogPosts.filter(post => {
    const matchesCategory = selectedCategory === "All" || post.category === selectedCategory;
    const matchesSearch =
      post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.excerpt.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const featuredPost = blogPosts.find(post => post.featured);

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-blue-50">

      {/* Hero */}
      <div className="relative bg-[#343a4D] text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,0 V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
          </svg>
        </div>

        <section className="relative py-16 max-w-4xl mx-auto text-center px-4">
          <div className="inline-flex items-center mb-4 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold">
            <span className="mr-2">📚</span> <span className="font-linkbay">LINKBAY-CMS</span> BLOG
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
            Guides and insights for <span className="text-[#ff5758]">agencies</span>
          </h1>

          <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-6">
            Practical content on running client stores, building recurring revenue, and delivering
            faster with the right infrastructure.
          </p>

          {/* Search */}
          <div className="max-w-md mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Search articles..."
                className="w-full px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <span className="absolute right-3 top-3 text-gray-400">🔍</span>
            </div>
          </div>
        </section>
      </div>

      {/* Featured post */}
      {featuredPost && (
        <section className="max-w-6xl mx-auto px-4 py-12">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
            <div className="md:flex">
              <div className="md:w-2/3 p-8">
                <div className="inline-flex items-center bg-[#ff5758] text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
                  <span className="mr-2">⭐</span> FEATURED
                </div>
                <h2 className="text-3xl font-bold text-[#343a4D] mb-4">{featuredPost.title}</h2>
                <p className="text-gray-700 mb-6 text-lg">{renderTextWithLinkBayCMS(featuredPost.excerpt)}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>{featuredPost.author}</span>
                    <span>•</span>
                    <span>{featuredPost.date}</span>
                    <span>•</span>
                    <span>{featuredPost.readTime} read</span>
                  </div>
                  <Link
                    href={`/blog/${featuredPost.id}`}
                    className="bg-[#343a4D] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#ff5758] transition-colors"
                  >
                    Read article →
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

      {/* Category filter */}
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

      {/* Posts grid */}
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
                <p className="text-gray-600 mb-4 line-clamp-3">{renderTextWithLinkBayCMS(post.excerpt)}</p>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    <div>{post.author}</div>
                    <div>{post.date}</div>
                  </div>
                  <Link
                    href={`/blog/${post.id}`}
                    className="text-[#ff5758] font-semibold hover:text-[#343a4D] transition-colors"
                  >
                    Read →
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>

        {filteredPosts.length === 0 && (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block">🔍</span>
            <h3 className="text-xl font-bold text-gray-700 mb-2">No articles found</h3>
            <p className="text-gray-600">Try adjusting your filters or search term.</p>
          </div>
        )}
      </section>

      {/* Newsletter */}
      <section className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Stay in the loop</h2>
          <p className="mb-6 text-blue-100">
            Get new articles on agency operations, store management, and platform updates delivered to your inbox.
          </p>

          <div className="max-w-md mx-auto flex flex-col sm:flex-row gap-4">
            <input
              type="email"
              placeholder="Your work email"
              className="flex-1 px-4 py-3 rounded-lg text-gray-900"
            />
            <button className="px-6 py-3 bg-white text-[#343a4D] font-bold rounded-lg hover:bg-gray-100 transition-colors">
              Subscribe
            </button>
          </div>

          <p className="text-sm text-blue-200 mt-4">
            No spam. Unsubscribe at any time.
          </p>
        </div>
      </section>

      {/* Tags */}
      <section className="max-w-4xl mx-auto px-4 py-8 text-center">
        <h3 className="text-lg font-semibold text-[#343a4D] mb-4">Popular topics</h3>
        <div className="flex flex-wrap gap-2 justify-center">
          {["White-label", "GDPR", "Dashboard", "Automation", "API", "Security", "Recurring Revenue", "B2B", "Compliance", "Onboarding"].map(tag => (
            <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 cursor-pointer">
              #{tag}
            </span>
          ))}
        </div>
      </section>

    </main>
  );
}
