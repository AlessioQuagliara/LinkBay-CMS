// Configurazione database con Prisma Client
// Singleton pattern per ottimizzare le connessioni

import { PrismaClient } from '@prisma/client';

// Estendi il tipo NodeJS.Global per includere prisma
declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Crea istanza Prisma (singleton in development per evitare troppe connessioni)
export const prisma = global.prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

// Gestione graceful shutdown
export const disconnectDatabase = async (): Promise<void> => {
  await prisma.$disconnect();
};
