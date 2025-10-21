// Middleware per gestione errori centralizzata
// Intercetta tutti gli errori e risponde in formato standard

import { Request, Response, NextFunction } from 'express';
import { AppError, ApiResponse } from '../types';

export const errorHandler = (
  err: Error | AppError,
  _req: Request,
  res: Response,
  _next: NextFunction
): void => {
  // Log errore
  console.error('Error:', err);

  // Gestisci AppError custom
  if (err instanceof AppError) {
    const response: ApiResponse = {
      success: false,
      error: err.message
    };
    res.status(err.statusCode).json(response);
    return;
  }

  // Errori non gestiti
  const response: ApiResponse = {
    success: false,
    error: process.env.NODE_ENV === 'development' 
      ? err.message 
      : 'Errore interno del server'
  };
  
  res.status(500).json(response);
};

// Middleware per route non trovate
export const notFound = (req: Request, res: Response): void => {
  const response: ApiResponse = {
    success: false,
    error: `Route ${req.originalUrl} non trovata`
  };
  res.status(404).json(response);
};
