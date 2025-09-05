import { Request, Response, NextFunction } from 'express';

interface AppError extends Error {
  status?: number;
  code?: string;
}

export default function errorHandler(err: AppError, req: Request, res: Response, next: NextFunction) {
  // Log technical details
  // eslint-disable-next-line no-console
  console.error('Error:', { message: err.message, status: err.status || 500, stack: err.stack, code: err.code });

  // Map known OAuth/provider errors to user-friendly messages
  if (err.code && err.code.startsWith('EAUTH')) {
    return res.status(502).render('error/tenant-not-found', { message: 'Errore durante la comunicazione con il provider OAuth. Riprova più tardi.' });
  }

  const status = err.status && Number.isInteger(err.status) ? err.status : 500;

  // User-friendly messages per status
  const messages: { [key: number]: string } = {
    400: 'Richiesta non valida.',
    401: 'Non autorizzato. Effettua il login.',
    403: 'Accesso negato.',
    404: 'Risorsa non trovata.',
    502: 'Errore di comunicazione con servizio esterno.',
    500: 'Si è verificato un errore interno. Riprova più tardi.',
  };

  const userMessage = messages[status] || messages[500];

  // If request expects JSON, send JSON
  if (req.xhr || req.headers.accept?.includes('application/json') || req.path.startsWith('/api') ) {
    return res.status(status).json({ ok: false, error: userMessage });
  }

  return res.status(status).render('error/tenant-not-found', { message: userMessage });
}
