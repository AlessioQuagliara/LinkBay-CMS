// DashboardPage.tsx
import React from 'react';

const DashboardPage: React.FC = () => {
  const stats = [
    {
      title: 'Clienti Totali',
      value: '12',
      change: '+2',
      icon: '👥',
      color: 'bg-blue-500',
      href: '/clients'
    },
    {
      title: 'Siti Web',
      value: '8',
      change: '+1',
      icon: '🌐',
      color: 'bg-green-500',
      href: '/websites'
    },
    {
      title: 'Fatturato Mensile',
      value: '€2,450',
      change: '+12%',
      icon: '💰',
      color: 'bg-[#ff5758]',
      href: '/billing'
    },
    {
      title: 'Ordini Attivi',
      value: '24',
      change: '+5',
      icon: '📦',
      color: 'bg-purple-500',
      href: '/orders'
    }
  ];

  const quickActions = [
    {
      title: 'Nuovo Cliente',
      description: 'Aggiungi un nuovo cliente',
      icon: '➕',
      href: '/clients/new',
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      title: 'Crea Sito',
      description: 'Crea un nuovo sito web',
      icon: '🚀',
      href: '/websites/new',
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      title: 'Gestione Theme',
      description: 'Personalizza temi e layout',
      icon: '🎨',
      href: '/themes',
      color: 'bg-[#ff5758] hover:bg-[#e04e4e]'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Content */}
      <main className="p-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-[#343a4D] mt-1">{stat.value}</p>
                  <p className="text-xs text-green-500 font-medium mt-1">{stat.change} dall'ultimo mese</p>
                </div>
                <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <span className="text-white text-xl">{stat.icon}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {quickActions.map((action, index) => (
            <a
              key={index}
              href={action.href}
              className={`${action.color} text-white rounded-xl p-6 hover:shadow-lg transition-all transform hover:-translate-y-1`}
            >
              <div className="flex items-center space-x-4">
                <span className="text-2xl">{action.icon}</span>
                <div>
                  <h3 className="font-bold text-lg">{action.title}</h3>
                  <p className="text-white text-opacity-90 text-sm">{action.description}</p>
                </div>
              </div>
            </a>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-[#343a4D]">Attività Recente</h2>
            <a href="/activity" className="text-[#ff5758] hover:text-[#e04e4e] text-sm font-medium">
              Vedi tutto
            </a>
          </div>
          <div className="space-y-4">
            {[
              { action: 'Nuovo sito creato', client: 'Boutique Milano', time: '2 ore fa' },
              { action: 'Cliente aggiunto', client: 'Tech Solutions', time: '5 ore fa' },
              { action: 'Pagamento ricevuto', client: 'Fashion Store', time: '1 giorno fa' },
              { action: 'Theme aggiornato', client: 'Art Gallery', time: '2 giorni fa' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex items-center space-x-4">
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-gray-600 text-sm">📌</span>
                  </div>
                  <div>
                    <p className="font-medium text-[#343a4D]">{activity.action}</p>
                    <p className="text-sm text-gray-600">{activity.client}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;