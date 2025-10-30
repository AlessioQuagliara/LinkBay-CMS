import { BaseSeeder } from '@adonisjs/lucid/seeders'
import User from '#models/user'
import UserManager from '#models/user_manager'
import AgencyTenant from '#models/agency_tenant'

export default class extends BaseSeeder {
  async run() {
    // Crea utente admin
    const adminUser = await User.create({
      name: 'Admin LinkBay',
      email: 'admin@linkbay.com',
      password: 'admin123',
      role: 'superadmin',
      isActive: true,
    })

    // Crea utente agenzia demo
    const demoUser = await User.create({
      name: 'Agenzia Demo',
      email: 'agenzia@demo.com',
      password: 'agenzia123',
      role: 'agency',
      isActive: true,
    })

    // Crea altri utenti demo
    const marioUser = await User.create({
      name: 'Mario Rossi',
      email: 'mario@example.com',
      password: 'password123',
      role: 'agency',
      isActive: true,
    })

    const lauraUser = await User.create({
      name: 'Laura Bianchi',
      email: 'laura@example.com',
      password: 'password123',
      role: 'agency',
      isActive: true,
    })

    await User.create({
      name: 'Giuseppe Verdi',
      email: 'giuseppe@example.com',
      password: 'password123',
      role: 'agency',
      isActive: false, // Utente disattivato
    })

    // Associa utenti alle agenzie
    const demoAgency = await AgencyTenant.findBy('name', 'demo')
    const defaultAgency = await AgencyTenant.findBy('name', 'default')

    if (demoAgency) {
      await UserManager.create({
        userId: demoUser.id,
        agencyId: demoAgency.agencyId,
        role: 'owner',
      })

      await UserManager.create({
        userId: marioUser.id,
        agencyId: demoAgency.agencyId,
        role: 'admin',
      })
    }

    if (defaultAgency) {
      await UserManager.create({
        userId: lauraUser.id,
        agencyId: defaultAgency.agencyId,
        role: 'manager',
      })
    }
  }
}