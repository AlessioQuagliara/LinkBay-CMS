import nodemailer from 'nodemailer';
import path from 'path';
import fs from 'fs/promises';
import ejs from 'ejs';

export async function sendMailTemplate(to: string, subject: string, templateName: string, data: any) {
  const { SMTP_HOST, SMTP_PORT = '587', SMTP_USER, SMTP_PASS, FROM_EMAIL = 'no-reply@example.com' } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) throw new Error('SMTP not configured');

  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: Number(SMTP_PORT),
    secure: Number(SMTP_PORT) === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });

  const templatePath = path.join(__dirname, '..', 'views', 'emails', `${templateName}.ejs`);
  const templateRaw = await fs.readFile(templatePath, 'utf-8');
  const html = ejs.render(templateRaw, data);

  const info = await transporter.sendMail({ from: FROM_EMAIL, to, subject, html });
  return info;
}
