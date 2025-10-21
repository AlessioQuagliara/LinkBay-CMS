// Controller per autenticazione
// Gestisce request/response per auth endpoints

import { Request, Response, NextFunction } from 'express';
import { AuthService } from '../services/auth.service';
import { ApiResponse } from '../types';

const authService = new AuthService();

export class AuthController {
  // POST /auth/register
  async register(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { email, password, name } = req.body;
      
      const result = await authService.register(email, password, name);
      
      const response: ApiResponse = {
        success: true,
        data: result,
        message: 'Registrazione completata con successo'
      };
      
      res.status(201).json(response);
    } catch (error) {
      next(error);
    }
  }

  // POST /auth/login
  async login(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { email, password } = req.body;
      
      const result = await authService.login(email, password);
      
      const response: ApiResponse = {
        success: true,
        data: result,
        message: 'Login effettuato con successo'
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }

  // POST /auth/refresh
  async refresh(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { refreshToken } = req.body;
      
      const result = await authService.refreshAccessToken(refreshToken);
      
      const response: ApiResponse = {
        success: true,
        data: result,
        message: 'Token aggiornato'
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }

  // POST /auth/logout
  async logout(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { refreshToken } = req.body;
      
      await authService.logout(refreshToken);
      
      const response: ApiResponse = {
        success: true,
        message: 'Logout effettuato'
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }
}
