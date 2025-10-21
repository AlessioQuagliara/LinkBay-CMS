import React from 'react'

const WebsitesPage: React.FC = () => {
  // Mock data - in produzione verrebbe dal backend
  const websites = [
    { id: 1, name: 'Sito Rossi SRL', domain: 'rossisrl.com', status: 'Pubblicato', client: 'Mario Rossi' },
    { id: 2, name: 'E-commerce Bianchi', domain: 'bianchi-shop.com', status: 'In Sviluppo', client: 'Laura Bianchi' },
    { id: 3, name: 'Portfolio Verdi', domain: 'giuseppeverdi.it', status: 'Pubblicato', client: 'Giuseppe Verdi' },
  ]

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Gestione Siti Web</h1>
            <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
              Nuovo Sito
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {websites.map((website) => (
                <li key={website.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-md bg-green-500 flex items-center justify-center">
                            <span className="text-white font-medium">W</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {website.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {website.domain} • Cliente: {website.client}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          website.status === 'Pubblicato'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {website.status}
                        </span>
                        <div className="ml-4 flex space-x-2">
                          <button className="text-indigo-600 hover:text-indigo-900">
                            Modifica
                          </button>
                          <button className="text-blue-600 hover:text-blue-900">
                            Anteprima
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default WebsitesPage