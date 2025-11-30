import axios from 'axios'

// Funzione per estrarre tenant dal subdomain
const getTenantFromSubdomain = (): string | null => {
  const hostname = window.location.hostname;
  
  // Per localhost o IP, usa un tenant di default
  if (hostname === 'localhost' || hostname === '127.0.0.1' || /^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
    return 'default';
  }
  
  // Per app.linkbay-cms.local, non impostare tenant (è il dominio principale)
  if (hostname === 'app.linkbay-cms.local') {
    return null;
  }
  
  // Per altri sottodomini tipo nomeagenzia.linkbay-cms.local
  const parts = hostname.split('.');
  if (parts.length >= 3 && parts[parts.length - 2] === 'linkbay-cms') {
    return parts[0]; // nomeagenzia
  }
  
  return null;
};

// Configurazione base dell'API
const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor per aggiungere il token JWT e tenant
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Aggiungi tenant header
  const tenant = getTenantFromSubdomain()
  if (tenant) {
    config.headers['X-Tenant-ID'] = tenant
  }
  
  return config
})

// Interceptor per gestire errori di autenticazione
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
  role?: string
  isActive?: boolean
}

export interface AuthResponse {
  user: {
    id: number
    name: string
    email: string
    role: string
    isActive: boolean
  }
  token: {
    value: string
    type: string
  }
}

export const authService = {
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  async getProfile() {
    const response = await api.get('/auth/profile')
    return response.data
  },

  async logout() {
    await api.post('/auth/logout')
    localStorage.removeItem('auth_token')
  }
}

export default api