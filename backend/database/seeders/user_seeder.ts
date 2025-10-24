import { BaseSeeder } from '@adonisjs/lucid/seeders'
import User from '#models/user'

export default class extends BaseSeeder {
  async run() {
    // Crea utente admin
    await User.create({
      name: 'Admin LinkBay',
      email: 'admin@linkbay.com',
      password: 'admin123',
      role: 'superadmin',
      isActive: true,
    })

    // Crea utente agenzia demo
    await User.create({
      name: 'Agenzia Demo',
      email: 'agenzia@demo.com',
      password: 'agenzia123',
      role: 'agency',
      isActive: true,
    })

    // Crea altri utenti demo
    await User.createMany([
      {
        name: 'Mario Rossi',
        email: 'mario@example.com',
        password: 'password123',
        role: 'agency',
        isActive: true,
      },
      {
        name: 'Laura Bianchi',
        email: 'laura@example.com',
        password: 'password123',
        role: 'agency',
        isActive: true,
      },
      {
        name: 'Giuseppe Verdi',
        email: 'giuseppe@example.com',
        password: 'password123',
        role: 'agency',
        isActive: false, // Utente disattivato
      },
    ])
  }
}