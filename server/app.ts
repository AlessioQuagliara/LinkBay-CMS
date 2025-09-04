import express from 'express';
import path from 'path';
import dotenv from 'dotenv';

import tenantResolver from './middleware/tenantResolver';
import authController from './controllers/authController';
import expressLayouts from 'express-ejs-layouts';
import landingRouter from './routes/landing';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');
app.use(expressLayouts);
// Do not set a global layout here; landing routes specify their own layout.

// Serve public assets and docs index
app.use(express.static(path.join(__dirname, '..', 'public')));
app.use('/docs', express.static(path.join(__dirname, '..', 'docs')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Attach tenant resolver early
app.use(tenantResolver);

// Routes
// Landing pages (use per-route layout)
app.use('/', landingRouter);

// API / other controllers
app.post('/api/register', authController.register);

export default app;

if (require.main === module) {
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`Server listening on http://localhost:${port}`);
  });
}
