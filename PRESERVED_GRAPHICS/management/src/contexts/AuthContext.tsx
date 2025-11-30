import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, AuthResponse } from '../services/api'

interface User {
  id: number
  name: string
  email: string
  role: string
  isActive: boolean
  tenant?: string // Add tenant info
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (data: { name: string; email: string; password: string }) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on app start
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Verify token by fetching profile
      authService.getProfile()
        .then((response) => {
          setUser(response.user)
        })
        .catch(() => {
          localStorage.removeItem('auth_token')
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response: AuthResponse = await authService.login({ email, password })
    localStorage.setItem('auth_token', response.token.value)
    setUser(response.user)
  }

  const register = async (data: { name: string; email: string; password: string }) => {
    const response: AuthResponse = await authService.register(data)
    localStorage.setItem('auth_token', response.token.value)
    setUser(response.user)
  }

  const logout = () => {
    authService.logout()
    setUser(null)
  }

  const value = {
    user,
    login,
    register,
    logout,
    isLoading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}