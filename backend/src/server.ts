// Server principale Express
// Bootstrap applicazione con middleware e routes

import express, { Application } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import routes from './routes';
import { errorHandler, notFound } from './middlewares/error.middleware';
import { disconnectDatabase } from './config/database';

// Carica variabili d'ambiente
dotenv.config();

const app: Application = express();
const PORT = process.env.PORT || 3000;
const API_VERSION = process.env.API_VERSION || 'v1';

// CORS configuration
const corsOptions = {
  origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3001'],
  credentials: true,
  optionsSuccessStatus: 200
};

// Middleware globali
app.use(cors(corsOptions));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging (solo development)
if (process.env.NODE_ENV === 'development') {
  app.use((req, _res, next) => {
    console.log(`${req.method} ${req.path}`);
    next();
  });
}

// Root endpoint
app.get('/', (_req, res) => {
  res.json({
    name: 'LinkBay CMS API',
    version: '1.0.0',
    status: 'running',
    documentation: `/api/${API_VERSION}/health`
  });
});

// Mount API routes
app.use(`/api/${API_VERSION}`, routes);

// 404 handler
app.use(notFound);

// Error handler (deve essere l'ultimo)
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM ricevuto, chiusura graceful...');
  await disconnectDatabase();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT ricevuto, chiusura graceful...');
  await disconnectDatabase();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  console.log(`
┌─────────────────────────────────────────┐
│   🚀 LinkBay CMS API Server Running    │
├─────────────────────────────────────────┤
│   Port: ${PORT}                       │
│   Environment: ${process.env.NODE_ENV || 'development'}           │
│   API Version: ${API_VERSION}                   │
└─────────────────────────────────────────┘
  `);
});

export default app;
