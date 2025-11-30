// Sidebar.tsx
import React from 'react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const menuItems = [
    { name: 'Dashboard', icon: 'fas fa-chart-bar', href: '/' },
    { name: 'Clienti', icon: 'fas fa-users', href: '/clients' },
    { name: 'Siti Web', icon: 'fas fa-globe', href: '/websites' },
    { name: 'Content', icon: 'fas fa-edit', href: '/content' },
    { name: 'Media', icon: 'fas fa-images', href: '/media' },
    { name: 'Fatturazione', icon: 'fas fa-money-bill-alt', href: '/billing' },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50
        w-full lg:w-64 h-screen bg-[#343a4D] text-white
        transform transition-transform duration-300 ease-in-out
        flex flex-col overflow-hidden
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-gray-600 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#ff5758] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">LB</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">LinkBay CMS</h1>
              <p className="text-xs text-gray-400">Your E-commerce Arsenal</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-6 flex-1">
          <ul className="space-y-2 px-4">
            {menuItems.map((item) => (
              <li key={item.name}>
                <a
                  href={item.href}
                  className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-[#ff5758] transition-colors duration-200 group"
                >
                  <i className={`${item.icon} text-lg w-5 text-center`}></i>
                  <span className="font-medium">{item.name}</span>
                </a>
              </li>
            ))}
          </ul>

          {/* Settings - Non cliccabile come separatore */}
          <div className="mt-8 px-4">
            <div className="flex items-center space-x-3 px-4 py-3 text-gray-400">
              <i className="fas fa-cog text-lg w-5 text-center"></i>
              <span className="font-medium">Impostazioni</span>
            </div>
          </div>
        </nav>

        {/* User section - Fixed at bottom */}
        <div className="flex-shrink-0 p-4 border-t border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-[#ff5758] rounded-full flex items-center justify-center">
              <i className="fas fa-user text-white text-xs"></i>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">Alessio Quagliara</p>
              <p className="text-xs text-gray-400 truncate">Admin</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};