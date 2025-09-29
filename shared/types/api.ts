// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    REFRESH: '/api/auth/refresh',
    LOGOUT: '/api/auth/logout',
  },
  USERS: {
    GET_ALL: '/api/users',
    GET_BY_ID: (id: number) => `/api/users/${id}`,
    UPDATE: (id: number) => `/api/users/${id}`,
    DELETE: (id: number) => `/api/users/${id}`,
  },
  PROJECTS: {
    GET_ALL: '/api/projects',
    GET_BY_ID: (id: number) => `/api/projects/${id}`,
    CREATE: '/api/projects',
    UPDATE: (id: number) => `/api/projects/${id}`,
    DELETE: (id: number) => `/api/projects/${id}`,
  },
  WEBSITES: {
    GET_ALL: '/api/websites',
    GET_BY_ID: (id: number) => `/api/websites/${id}`,
    CREATE: '/api/websites',
    UPDATE: (id: number) => `/api/websites/${id}`,
    DELETE: (id: number) => `/api/websites/${id}`,
  },
  ORDERS: {
    GET_ALL: '/api/orders',
    GET_BY_ID: (id: number) => `/api/orders/${id}`,
    CREATE: '/api/orders',
    UPDATE: (id: number) => `/api/orders/${id}`,
    DELETE: (id: number) => `/api/orders/${id}`,
  },
} as const;

// Environment Variables
export interface EnvVariables {
  NODE_ENV: 'development' | 'production' | 'test';
  PORT: string;
  DATABASE_URL: string;
  REDIS_URL: string;
  JWT_SECRET: string;
  JWT_REFRESH_SECRET: string;
  
  // OAuth
  GITHUB_CLIENT_ID?: string;
  GITHUB_CLIENT_SECRET?: string;
  GOOGLE_CLIENT_ID?: string;
  GOOGLE_CLIENT_SECRET?: string;
  
  // SMTP
  SMTP_HOST?: string;
  SMTP_PORT?: string;
  SMTP_USER?: string;
  SMTP_PASS?: string;
}

// Validation Schemas (runtime validation can be added later)
export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD: {
    MIN_LENGTH: 8,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/
  },
  DOMAIN: /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/,
} as const;