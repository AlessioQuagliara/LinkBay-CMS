// Middleware di validazione con Zod
// Valida request body, params e query

import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';
import { AppError, ApiResponse } from '../types';

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message
        }));
        
        const response: ApiResponse = {
          success: false,
          error: 'Errori di validazione',
          data: errors
        };
        
        res.status(400).json(response);
        return;
      }
      next(new AppError('Errore di validazione', 400));
    }
  };
};
