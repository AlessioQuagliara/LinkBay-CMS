// Service per gestione utenti
// Single Responsibility: CRUD operazioni sugli utenti

import { prisma } from '../config/database';
import { AppError } from '../types';

export class UserService {
  // Ottieni utente per ID
  async getUserById(userId: string) {
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        isActive: true,
        createdAt: true
      }
    });

    if (!user) {
      throw new AppError('Utente non trovato', 404);
    }

    return user;
  }

  // Ottieni profilo utente con agenzie
  async getUserProfile(userId: string) {
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        createdAt: true,
        agencies: {
          select: {
            id: true,
            name: true,
            description: true,
            logo: true,
            isActive: true,
            _count: {
              select: {
                websites: true,
                customers: true
              }
            }
          }
        }
      }
    });

    if (!user) {
      throw new AppError('Utente non trovato', 404);
    }

    return user;
  }

  // Aggiorna profilo utente
  async updateProfile(userId: string, data: { name?: string; email?: string }) {
    // Verifica se email già usata
    if (data.email) {
      const existing = await prisma.user.findFirst({
        where: {
          email: data.email,
          id: { not: userId }
        }
      });

      if (existing) {
        throw new AppError('Email già in uso', 400);
      }
    }

    const user = await prisma.user.update({
      where: { id: userId },
      data,
      select: {
        id: true,
        email: true,
        name: true,
        role: true
      }
    });

    return user;
  }

  // Lista tutti gli utenti (solo admin)
  async listUsers(page: number = 1, limit: number = 10) {
    const skip = (page - 1) * limit;

    const [users, total] = await Promise.all([
      prisma.user.findMany({
        skip,
        take: limit,
        select: {
          id: true,
          email: true,
          name: true,
          role: true,
          isActive: true,
          createdAt: true,
          _count: {
            select: { agencies: true }
          }
        },
        orderBy: { createdAt: 'desc' }
      }),
      prisma.user.count()
    ]);

    return {
      data: users,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    };
  }

  // Disattiva utente
  async deactivateUser(userId: string) {
    return prisma.user.update({
      where: { id: userId },
      data: { isActive: false }
    });
  }
}
