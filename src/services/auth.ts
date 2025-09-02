import jwt, { SignOptions } from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
dotenv.config();

const JWT_SECRET = process.env.SESSION_SECRET || 'devsecret';

export function hashPassword(password: string) {
  return bcrypt.hash(password, 10);
}

export function comparePassword(password: string, hash: string) {
  return bcrypt.compare(password, hash);
}

export function signAccessToken(payload: object, expiresIn = '15m') {
  const opts: any = { expiresIn };
  return jwt.sign(payload as any, JWT_SECRET as any, opts);
}

export function signRefreshToken(payload: object, expiresIn = '30d') {
  const opts: any = { expiresIn };
  return jwt.sign(payload as any, JWT_SECRET as any, opts);
}

export function verifyToken(token: string) {
  return jwt.verify(token, JWT_SECRET);
}
