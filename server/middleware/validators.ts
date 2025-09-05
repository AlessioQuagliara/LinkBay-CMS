import { body, validationResult, ValidationChain } from 'express-validator';
import { Request, Response, NextFunction } from 'express';

const allowedProviders = ['google', 'github', 'microsoft'];
const allowedRoles = ['owner', 'admin', 'member'];
const emailWhitelist = (process.env.EMAIL_WHITELIST || '').split(',').map(s => s.trim()).filter(Boolean); // domains

export const tenantNameValidator: ValidationChain = body('tenantName')
  .isString()
  .isLength({ min: 3 })
  .matches(/^[a-zA-Z0-9\-\_ ]+$/)
  .withMessage('tenantName must be alphanumeric and at least 3 chars');

export const emailValidator: ValidationChain = body('email')
  .isEmail()
  .withMessage('Invalid email')
  .custom((value) => {
    if (!emailWhitelist.length) return true; // if no whitelist, accept all
    const domain = value.split('@')[1];
    if (!domain) return false;
    return emailWhitelist.includes(domain);
  })
  .withMessage('Email domain not allowed');

export const providerValidator: ValidationChain = body('provider')
  .isString()
  .custom((v) => allowedProviders.includes(v))
  .withMessage('Invalid provider');

export const roleValidator: ValidationChain = body('role')
  .optional()
  .isString()
  .custom((v) => allowedRoles.includes(v))
  .withMessage('Invalid role');

export function validate(req: Request, res: Response, next: NextFunction) {
  const errors = validationResult(req);
  if (errors.isEmpty()) return next();
  return res.status(400).json({ ok: false, errors: errors.array() });
}
