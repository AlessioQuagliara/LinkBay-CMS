// Middleware di autenticazione JWT
// Verifica token e aggiunge user alla request

import { Response, NextFunction } from 'express';
import { verifyToken } from '../config/jwt';
import { AuthRequest, AppError } from '../types';

export const authenticate = (req: AuthRequest, _res: Response, next: NextFunction): void => {
  try {
    // Estrai token dall'header Authorization
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError('Token non fornito', 401);
    }

    const token = authHeader.split(' ')[1];
    
    // Verifica e decodifica token
    const payload = verifyToken(token);
    
    // Aggiungi user alla request
    req.user = payload;
    
    next();
  } catch (error) {
    if (error instanceof AppError) {
      next(error);
    } else {
      next(new AppError('Token non valido', 401));
    }
  }
};

// Middleware per verificare ruolo admin
export const requireAdmin = (req: AuthRequest, _res: Response, next: NextFunction): void => {
  if (req.user?.role !== 'ADMIN') {
    throw new AppError('Accesso negato: richiesti permessi admin', 403);
  }
  next();
};
