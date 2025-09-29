// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Health Check Response
export interface HealthResponse {
  status: string;
  timestamp: string;
  environment: string;
  version: string;
}

// User Types
export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

export enum UserRole {
  ADMIN = 'admin',
  AGENCY = 'agency',
  CUSTOMER = 'customer'
}

// Project Types
export interface Project {
  id: number;
  name: string;
  description?: string;
  ownerId: number;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}

export enum ProjectStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

// Website Types
export interface Website {
  id: number;
  projectId: number;
  domain: string;
  subdomain?: string;
  templateId?: number;
  status: WebsiteStatus;
  settings: WebsiteSettings;
  createdAt: string;
  updatedAt: string;
}

export enum WebsiteStatus {
  DRAFT = 'draft',
  BUILDING = 'building',
  PUBLISHED = 'published',
  MAINTENANCE = 'maintenance'
}

export interface WebsiteSettings {
  theme: string;
  colors: {
    primary: string;
    secondary: string;
    accent?: string;
  };
  fonts: {
    heading: string;
    body: string;
  };
  seo: {
    title: string;
    description: string;
    keywords: string[];
  };
}

// Order Types
export interface Order {
  id: number;
  customerId: number;
  packageType: PackageType;
  status: OrderStatus;
  totalAmount: number;
  currency: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export enum PackageType {
  BASIC = 'basic',
  PREMIUM = 'premium',
  ENTERPRISE = 'enterprise'
}

export enum OrderStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// Form Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role?: UserRole;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

// Pagination
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}