import { Request, Response } from 'express';
import speakeasy from 'speakeasy';
import path from 'path';
import fs from 'fs/promises';
import ejs from 'ejs';
import { initDb } from '../../src/db';
import nodemailer from 'nodemailer';

const home = (req: Request, res: Response) => {
  res.render('landing/home', { title: 'LinkBay CMS' });
};

async function sendVerificationEmail(to: string, tenantName: string, mfaSecret: string) {
  // load SMTP config from env
  const { SMTP_HOST, SMTP_PORT = '587', SMTP_USER, SMTP_PASS, FROM_EMAIL = 'no-reply@example.com' } = process.env;

  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
    throw new Error('SMTP not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASS');
  }

  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: Number(SMTP_PORT),
    secure: Number(SMTP_PORT) === 465, // true for 465, false for other ports
    auth: {
      user: SMTP_USER,
      pass: SMTP_PASS,
    },
  });

  // render template
  const templatePath = path.join(__dirname, '..', '..', 'views', 'email', 'mfa_verify.ejs');
  const templateRaw = await fs.readFile(templatePath, 'utf-8');
  const verifyLink = `${process.env.APP_URL || 'http://localhost:3001'}/verify-mfa?secret=${encodeURIComponent(mfaSecret)}&tenant=${encodeURIComponent(tenantName)}`;
  const html = ejs.render(templateRaw, { tenantName, verifyLink });

  const info = await transporter.sendMail({
    from: FROM_EMAIL,
    to,
    subject: `Verify your account for ${tenantName}`,
    html,
  });

  return info;
}

import { tenantNameValidator, emailValidator, validate } from '../middleware/validators';

const register = [tenantNameValidator, emailValidator, validate, async (req: Request, res: Response) => {
  const { tenantName, email } = req.body as { tenantName?: string; email?: string };

  // generate MFA secret
  const secret = speakeasy.generateSecret({ length: 20 });

  try {
    const db = await initDb();

    // create tenant and user inside a transaction
    const result = await db.transaction(async (trx) => {
      const [tenant] = await trx('tenants').insert({ name: tenantName }).returning('*');
      const [user] = await trx('users')
        .insert({ tenant_id: tenant.id, email, mfa_secret: secret.base32, role: 'owner' })
        .returning('*');
      return { tenant, user };
    });

  // send verification email
  await sendVerificationEmail(email!, tenantName!, secret.base32);

    return res.json({ ok: true, tenantId: result.tenant.id, userId: result.user.id });
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('Registration error:', err);
    return res.status(500).json({ ok: false, error: err.message || 'Internal error' });
  }
}];

export default { home, register };
