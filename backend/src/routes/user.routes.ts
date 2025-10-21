// Routes per utenti
// Definisce endpoints protetti per user management

import { Router } from 'express';
import { UserController } from '../controllers/user.controller';
import { authenticate, requireAdmin } from '../middlewares/auth.middleware';
import { validate } from '../middlewares/validate.middleware';
import { updateProfileSchema } from '../validators/schemas';

const router = Router();
const userController = new UserController();

// Tutte le routes richiedono autenticazione
router.use(authenticate);

// GET /api/v1/users/me - Profilo corrente
router.get('/me', (req, res, next) => 
  userController.getProfile(req as any, res, next)
);

// PUT /api/v1/users/me - Aggiorna profilo
router.put('/me', validate(updateProfileSchema), (req, res, next) => 
  userController.updateProfile(req as any, res, next)
);

// Routes solo per admin
router.get('/', requireAdmin, (req, res, next) => 
  userController.listUsers(req as any, res, next)
);

router.get('/:id', requireAdmin, (req, res, next) => 
  userController.getUserById(req as any, res, next)
);

export default router;
