import React from 'react'

const ClientsPage: React.FC = () => {
  // Mock data - in produzione verrebbe dal backend
  const clients = [
    { id: 1, name: 'Mario Rossi', email: 'mario@example.com', status: 'Attivo' },
    { id: 2, name: 'Laura Bianchi', email: 'laura@example.com', status: 'Attivo' },
    { id: 3, name: 'Giuseppe Verdi', email: 'giuseppe@example.com', status: 'Inattivo' },
  ]

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Gestione Clienti</h1>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Aggiungi Cliente
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {clients.map((client) => (
                <li key={client.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <span className="text-gray-700 font-medium">
                              {client.name.charAt(0)}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {client.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {client.email}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          client.status === 'Attivo'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {client.status}
                        </span>
                        <button className="ml-4 text-indigo-600 hover:text-indigo-900">
                          Modifica
                        </button>
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

export default ClientsPage