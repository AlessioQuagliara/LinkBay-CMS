import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import ClientsPage from './pages/clients/ClientsPage'
import WebsitesPage from './pages/websites/WebsitesPage'
import BillingPage from './pages/billing/BillingPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected routes */}
          <Route path="/" element={<ProtectedRoute><Layout><DashboardPage /></Layout></ProtectedRoute>} />
          <Route path="/clients" element={<ProtectedRoute><Layout><ClientsPage /></Layout></ProtectedRoute>} />
          <Route path="/websites" element={<ProtectedRoute><Layout><WebsitesPage /></Layout></ProtectedRoute>} />
          <Route path="/billing" element={<ProtectedRoute><Layout><BillingPage /></Layout></ProtectedRoute>} />
          <Route path="*" element={<ProtectedRoute><Layout><NotFoundPage /></Layout></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App