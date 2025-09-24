import express, { Request, Response, NextFunction, Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app: Application = express();
const PORT: number = parseInt(process.env.PORT || '3000', 10);

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Types for API responses
interface HealthResponse {
  status: string;
  timestamp: string;
  environment: string;
  version: string;
}

interface ApiInfoResponse {
  message: string;
  version: string;
  endpoints: {
    health: string;
    api: string;
  };
}

interface ErrorResponse {
  error: string;
  message: string;
}

// Health check endpoint
app.get('/health', (req: Request, res: Response<HealthResponse>) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    version: '1.0.0'
  });
});

// API Routes
app.get('/', (req: Request, res: Response<ApiInfoResponse>) => {
  res.json({ 
    message: 'LinkBay CMS Backend API', 
    version: '1.0.0',
    endpoints: {
      health: '/health',
      api: '/api'
    }
  });
});

// API namespace
app.get('/api', (req: Request, res: Response) => {
  res.json({ message: 'API endpoints will be implemented here' });
});


// Error handling middleware
app.use((err: Error, req: Request, res: Response<ErrorResponse>, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal Server Error'
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 LinkBay CMS Backend running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app;