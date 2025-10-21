// Service per gestione autenticazione
// Single Responsibility: gestisce SOLO logica di autenticazione

import bcrypt from 'bcrypt';
import { prisma } from '../config/database';
import { generateAccessToken, generateRefreshToken, verifyToken, getRefreshTokenExpiry } from '../config/jwt';
import { AppError } from '../types';

export class AuthService {
  // Registrazione nuovo utente
  async register(email: string, password: string, name: string) {
    // Verifica se utente esiste
    const existingUser = await prisma.user.findUnique({ where: { email } });
    if (existingUser) {
      throw new AppError('Email già registrata', 400);
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Crea utente
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        role: 'AGENCY'
      },
      select: {
        id: true,
        email: true,
        name: true,
        role: true
      }
    });

    // Genera tokens
    const accessToken = generateAccessToken({
      userId: user.id,
      email: user.email,
      role: user.role
    });

    const refreshToken = generateRefreshToken({
      userId: user.id,
      email: user.email,
      role: user.role
    });

    // Salva refresh token
    await prisma.refreshToken.create({
      data: {
        token: refreshToken,
        userId: user.id,
        expiresAt: getRefreshTokenExpiry()
      }
    });

    return { user, accessToken, refreshToken };
  }

  // Login utente
  async login(email: string, password: string) {
    // Trova utente
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user || !user.isActive) {
      throw new AppError('Credenziali non valide', 401);
    }

    // Verifica password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      throw new AppError('Credenziali non valide', 401);
    }

    // Genera tokens
    const accessToken = generateAccessToken({
      userId: user.id,
      email: user.email,
      role: user.role
    });

    const refreshToken = generateRefreshToken({
      userId: user.id,
      email: user.email,
      role: user.role
    });

    // Salva refresh token
    await prisma.refreshToken.create({
      data: {
        token: refreshToken,
        userId: user.id,
        expiresAt: getRefreshTokenExpiry()
      }
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      },
      accessToken,
      refreshToken
    };
  }

  // Refresh access token
  async refreshAccessToken(refreshToken: string) {
    // Verifica refresh token nel database
    const tokenRecord = await prisma.refreshToken.findUnique({
      where: { token: refreshToken },
      include: { user: true }
    });

    if (!tokenRecord || tokenRecord.expiresAt < new Date()) {
      throw new AppError('Refresh token non valido o scaduto', 401);
    }

    // Verifica JWT
    const payload = verifyToken(refreshToken);

    // Genera nuovo access token
    const accessToken = generateAccessToken({
      userId: payload.userId,
      email: payload.email,
      role: payload.role
    });

    return { accessToken };
  }

  // Logout (invalida refresh token)
  async logout(refreshToken: string) {
    await prisma.refreshToken.deleteMany({ where: { token: refreshToken } });
  }
}
