// Header.tsx
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface HeaderProps {
  onMenuToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Funzione per rilevare automaticamente il nome della pagina
  const getPageName = (pathname: string): string => {
    const pageMap: { [key: string]: string } = {
      '/': 'Dashboard',
      '/clients': 'Clienti',
      '/websites': 'Siti Web',
      '/content': 'Content',
      '/media': 'Media',
      '/billing': 'Fatturazione',
      '/settings': 'Impostazioni',
      '/login': 'Login',
      '/register': 'Registrazione'
    };

    return pageMap[pathname] || 'Dashboard';
  };

  const getPageDescription = (pathname: string): string => {
    const descriptionMap: { [key: string]: string } = {
      '/': 'Panoramica della tua piattaforma',
      '/clients': 'Gestisci i tuoi clienti',
      '/websites': 'Amministra i siti web',
      '/content': 'Gestisci contenuti e articoli',
      '/media': 'Libreria multimediale',
      '/billing': 'Fatturazione e pagamenti',
      '/settings': 'Configurazioni sistema',
      '/login': 'Accedi al sistema',
      '/register': 'Crea nuovo account'
    };

    return descriptionMap[pathname] || 'Panoramica della tua piattaforma';
  };

  const pageName = getPageName(location.pathname);
  const pageDescription = getPageDescription(location.pathname);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-40 lg:left-64">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuToggle}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <span className="text-2xl">☰</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold text-[#343a4D]">{pageName}</h1>
            <p className="text-sm text-gray-600">{pageDescription}</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <span className="text-xl">🔔</span>
          </button>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-700">{user?.name}</span>
            <button
              onClick={handleLogout}
              className="px-3 py-1 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};