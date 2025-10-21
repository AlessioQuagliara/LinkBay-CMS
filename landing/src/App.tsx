import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout/Layout'
import ScrollToTop from './components/ScrollToTop'
import { HomePage } from './pages/HomePage'
import { PricingPage } from './pages/PricingPage'
import { FeaturesPage } from './pages/FeaturesPage'
import { AboutPage } from './pages/AboutPage'
import { ContactPage } from './pages/ContactPage'
import { PrivacyPage } from './pages/PrivacyPage'
import { TermsPage } from './pages/TermsPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ApiDocsPage } from './pages/ApiDocsPage'
import { BlogPage } from './pages/BlogPage'
import { WorkWithUsPage } from './pages/WorkWithUsPage'
import MarketplacePage from './pages/MarketplacePage'
import { CookiePolicyPage } from './pages/CookiePolicyPage'
import './App.css'

function App() {
  return (
    <Router>
      <ScrollToTop />
      <Layout>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/api-docs" element={<ApiDocsPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/work-with-us" element={<WorkWithUsPage />} />
          <Route path="/marketplace" element={<MarketplacePage />} />

          {/* Legal Routes */}
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/cookie-policy" element={<CookiePolicyPage />} />

          {/* 404 Route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App