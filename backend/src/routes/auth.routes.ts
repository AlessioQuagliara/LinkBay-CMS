// Routes per autenticazione
// Definisce endpoints pubblici per auth

import { Router } from 'express';
import { AuthController } from '../controllers/auth.controller';
import { validate } from '../middlewares/validate.middleware';
import { registerSchema, loginSchema, refreshTokenSchema } from '../validators/schemas';

const router = Router();
const authController = new AuthController();

// POST /api/v1/auth/register - Registrazione
router.post('/register', validate(registerSchema), (req, res, next) => 
  authController.register(req, res, next)
);

// POST /api/v1/auth/login - Login
router.post('/login', validate(loginSchema), (req, res, next) => 
  authController.login(req, res, next)
);

// POST /api/v1/auth/refresh - Refresh token
router.post('/refresh', validate(refreshTokenSchema), (req, res, next) => 
  authController.refresh(req, res, next)
);

// POST /api/v1/auth/logout - Logout
router.post('/logout', validate(refreshTokenSchema), (req, res, next) => 
  authController.logout(req, res, next)
);

export default router;
