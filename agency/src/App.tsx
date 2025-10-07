import React, { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
// Layout and Home are exported with different names in their files
// DashboardLayout is exported from components/Layout/Layout.tsx
// Dashboard is exported from pages/Home.tsx
import { DashboardLayout as Layout } from './components/Layout/Layout'
import { Dashboard as Home } from './pages/Home'
import './App.css'

function App(): React.ReactElement {
  const [count, setCount] = useState<number>(0)

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App