import { Router, Request, Response } from 'express';
const router = Router();

// Use explicit layout for landing routes
const layout = 'landing/_layout';

router.get('/', (req: Request, res: Response) => {
  res.render('landing/home', { title: 'Home', layout });
});

router.get('/login', (req: Request, res: Response) => {
  res.render('landing/login', { title: 'Login', layout });
});

router.get('/signup', (req: Request, res: Response) => {
  res.render('landing/signup', { title: 'Sign up', layout });
});

router.get('/pricing', (req: Request, res: Response) => {
  res.render('landing/pricing', { title: 'Pricing', layout });
});

router.get('/features', (req: Request, res: Response) => {
  res.render('landing/features', { title: 'Features', layout });
});

router.get('/docs', (req: Request, res: Response) => {
  res.render('landing/docs', { title: 'Documentation', layout });
});

export default router;
