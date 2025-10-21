// Tipi comuni condivisi nell'applicazione
// Mantiene consistenza dei tipi tra layers

import { Request } from 'express';
import { JWTPayload } from '../config/jwt';

// Request estesa con user autenticato
export interface AuthRequest extends Request {
  user?: JWTPayload;
}

// Risposta API standardizzata
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Errore applicazione custom
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

// Risultato paginato
export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
