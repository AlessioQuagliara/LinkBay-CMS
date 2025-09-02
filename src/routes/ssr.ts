import { Router } from 'express';
import pageController from '../controllers/pageController';

const router = Router();

// catch-all for pages: marketing or tenant
router.get('*', pageController.renderPage);

export default router;
