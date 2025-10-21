// Controller per utenti
// Gestisce request/response per user endpoints

import { Response, NextFunction } from 'express';
import { UserService } from '../services/user.service';
import { AuthRequest, ApiResponse } from '../types';

const userService = new UserService();

export class UserController {
  // GET /users/me - Profilo utente corrente
  async getProfile(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user!.userId;
      
      const profile = await userService.getUserProfile(userId);
      
      const response: ApiResponse = {
        success: true,
        data: profile
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }

  // PUT /users/me - Aggiorna profilo
  async updateProfile(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user!.userId;
      const { name, email } = req.body;
      
      const updatedUser = await userService.updateProfile(userId, { name, email });
      
      const response: ApiResponse = {
        success: true,
        data: updatedUser,
        message: 'Profilo aggiornato'
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }

  // GET /users - Lista utenti (admin)
  async listUsers(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;
      
      const result = await userService.listUsers(page, limit);
      
      const response: ApiResponse = {
        success: true,
        data: result
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }

  // GET /users/:id - Dettaglio utente
  async getUserById(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { id } = req.params;
      
      const user = await userService.getUserById(id);
      
      const response: ApiResponse = {
        success: true,
        data: user
      };
      
      res.status(200).json(response);
    } catch (error) {
      next(error);
    }
  }
}
