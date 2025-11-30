import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ChevronDown, Ship } from 'lucide-react';

export const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  const isActive = (path: string): boolean => location.pathname === path;

  const toggleMenu = (): void => setIsMenuOpen(!isMenuOpen);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/features', label: 'Features' },
    { path: '/pricing', label: 'Pricing' },
    { path: '/about', label: 'About' },
    { path: '/contact', label: 'Contact' },
  ];

  return (
    <header className={`fixed top-0 w-full z-50 transition-all duration-500 ${
      isScrolled 
        ? 'bg-white/95 backdrop-blur-lg shadow-xl py-2 border-b border-gray-100' 
        : 'bg-white py-4'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <img src="/logo.svg" alt="LinkBay CMS" className="h-12 w-auto" />
            <span className="sr-only">LinkBay-CMS - Innovative Content Management</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`relative px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-300 group no-underline ${
                  isActive(item.path)
                    ? 'text-[#ff5758]'
                    : 'text-[#343a4D] hover:text-[#ff5758]'
                }`}
              >
                {item.label}
                <span
                  className={`absolute inset-0 bg-red-50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 ${
                    isActive(item.path) ? 'opacity-100' : ''
                  }`}
                ></span>
              </Link>
            ))}
          </nav>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            <a
              href="http://localhost:3003/login"
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2.5 text-sm font-medium text-[#343a4D] hover:text-[#ff5758] transition-colors duration-300 hover:scale-105 transform no-underline"
            >
              Sign In
            </a>
            <a
              href="http://localhost:3003/register"
              target="_blank"
              rel="noopener noreferrer"
              className="relative px-6 py-2.5 text-sm font-medium text-white bg-[#ff5758] rounded-xl hover:bg-[#e04e4e] transition-all duration-300 transform hover:scale-105 hover:shadow-lg shadow-md group overflow-hidden no-underline"
            >
              <span className="relative z-10">Start Free Trial</span>
              <div className="absolute inset-0 bg-[#e04e4e] opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="absolute top-0 -inset-full w-full h-full bg-gradient-to-r from-transparent via-white to-transparent transform skew-x-12 group-hover:animate-shine transition-all duration-1000"></div>
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={toggleMenu}
            className={`md:hidden p-3 rounded-xl transition-all duration-300 ${
              isMenuOpen 
                ? 'bg-red-100 text-[#ff5758] rotate-90' 
                : 'text-[#343a4D] hover:bg-red-50 hover:text-[#ff5758]'
            }`}
          >
            {isMenuOpen ? (
              <X className="w-6 h-6 transition-transform duration-300" />
            ) : (
              <Menu className="w-6 h-6 transition-transform duration-300" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        <div
          className={`md:hidden overflow-hidden transition-all duration-500 ease-in-out ${
            isMenuOpen
              ? 'max-h-96 opacity-100 pt-4'
              : 'max-h-0 opacity-0'
          }`}
        >
          <div className="py-4 border-t border-gray-200/50 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-4 py-3 text-base font-medium rounded-xl transition-all duration-300 transform hover:translate-x-2 no-underline ${
                  isActive(item.path)
                    ? 'text-[#ff5758] bg-red-50 border-l-4 border-[#ff5758]'
                    : 'text-[#343a4D] hover:text-[#ff5758] hover:bg-red-50'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="pt-4 border-t border-gray-200/50 space-y-3">
              <a
                href="http://localhost:3003/login"
                target="_blank"
                rel="noopener noreferrer"
                className="block px-4 py-3 text-base font-medium text-[#343a4D] hover:text-[#ff5758] hover:bg-gray-50 rounded-xl transition-all duration-300 no-underline"
                onClick={() => setIsMenuOpen(false)}
              >
                Sign In
              </a>
              <a
                href="http://localhost:3003/register"
                target="_blank"
                rel="noopener noreferrer"
                className="block px-4 py-3 text-base font-medium text-center text-white bg-[#ff5758] rounded-xl hover:bg-[#e04e4e] transition-all duration-300 transform hover:scale-105 shadow-md no-underline"
                onClick={() => setIsMenuOpen(false)}
              >
                Start Free Trial
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};