// Validazione schemas con Zod
// Centralizza tutti gli schemi di validazione

import { z } from 'zod';

// Auth schemas
export const registerSchema = z.object({
  body: z.object({
    email: z.string().email('Email non valida'),
    password: z.string().min(6, 'Password minimo 6 caratteri'),
    name: z.string().min(2, 'Nome minimo 2 caratteri')
  })
});

export const loginSchema = z.object({
  body: z.object({
    email: z.string().email('Email non valida'),
    password: z.string().min(1, 'Password richiesta')
  })
});

export const refreshTokenSchema = z.object({
  body: z.object({
    refreshToken: z.string().min(1, 'Refresh token richiesto')
  })
});

// User schemas
export const updateProfileSchema = z.object({
  body: z.object({
    name: z.string().min(2, 'Nome minimo 2 caratteri').optional(),
    email: z.string().email('Email non valida').optional()
  })
});
