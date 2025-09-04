import express from 'express';
import path from 'path';
import dotenv from 'dotenv';

import tenantResolver from './middleware/tenantResolver';
import authController from './controllers/authController';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');

app.use(express.static(path.join(__dirname, '..', 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Attach tenant resolver early
app.use(tenantResolver);

// Routes
app.get('/', authController.home);
app.post('/api/register', authController.register);

export default app;

if (require.main === module) {
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`Server listening on http://localhost:${port}`);
  });
}
