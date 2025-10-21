// Seed database con dati di esempio
// Utile per testing e development

import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Crea utente admin
  const adminPassword = await bcrypt.hash('admin123', 10);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@linkbaycms.com' },
    update: {},
    create: {
      email: 'admin@linkbaycms.com',
      password: adminPassword,
      name: 'Admin User',
      role: 'ADMIN'
    }
  });
  console.log('✅ Admin user created:', admin.email);

  // Crea utente agenzia demo
  const agencyPassword = await bcrypt.hash('demo123', 10);
  const agencyUser = await prisma.user.upsert({
    where: { email: 'demo@agency.com' },
    update: {},
    create: {
      email: 'demo@agency.com',
      password: agencyPassword,
      name: 'Demo Agency',
      role: 'AGENCY'
    }
  });
  console.log('✅ Agency user created:', agencyUser.email);

  // Crea agenzia demo
  const agency = await prisma.agency.create({
    data: {
      name: 'Demo Web Agency',
      description: 'Agenzia web di esempio per testing',
      userId: agencyUser.id
    }
  });
  console.log('✅ Agency created:', agency.name);

  // Crea clienti demo
  const customer1 = await prisma.customer.create({
    data: {
      name: 'Mario Rossi',
      email: 'mario.rossi@example.com',
      phone: '+39 333 1234567',
      company: 'Rossi SRL',
      agencyId: agency.id
    }
  });

  const customer2 = await prisma.customer.create({
    data: {
      name: 'Laura Bianchi',
      email: 'laura.bianchi@example.com',
      phone: '+39 333 7654321',
      company: 'Bianchi & Partners',
      agencyId: agency.id
    }
  });
  console.log('✅ Customers created:', customer1.name, customer2.name);

  // Crea siti web demo
  const website1 = await prisma.website.create({
    data: {
      name: 'Sito Rossi SRL',
      domain: 'www.rossisrl.com',
      description: 'Sito corporate per Rossi SRL',
      status: 'ACTIVE',
      agencyId: agency.id,
      customerId: customer1.id
    }
  });

  const website2 = await prisma.website.create({
    data: {
      name: 'Portfolio Bianchi',
      domain: 'www.laurabianchiphotography.com',
      description: 'Portfolio fotografico professionale',
      status: 'ACTIVE',
      agencyId: agency.id,
      customerId: customer2.id
    }
  });
  console.log('✅ Websites created:', website1.domain, website2.domain);

  console.log('\n🎉 Database seeding completed!\n');
  console.log('Login credentials:');
  console.log('  Admin: admin@linkbaycms.com / admin123');
  console.log('  Agency: demo@agency.com / demo123\n');
}

main()
  .catch((e) => {
    console.error('❌ Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
