/**
 * LinkBay CMS - Users Controller
 * @author Alessio Quagliara
 * @description Gestione utenti agenzia
 */

import type { HttpContext } from '@adonisjs/core/http'
import User from '#models/user'
import { createUserValidator, updateUserValidator } from '#validators/user'

export default class UsersController {
  /**
   * Lista tutti gli utenti
   */
  async index({ request, response }: HttpContext) {
    const page = request.input('page', 1)
    const limit = request.input('limit', 20)

    const users = await User.query()
      .preload('managerRoles')
      .paginate(page, limit)

    return response.ok(users)
  }

  /**
   * Mostra singolo utente
   */
  async show({ params, response }: HttpContext) {
    const user = await User.findOrFail(params.id)
    await user.load('managerRoles')

    return response.ok(user)
  }

  /**
   * Crea nuovo utente
   */
  async store({ request, response }: HttpContext) {
    const payload = await request.validateUsing(createUserValidator)

    const user = await User.create({
      name: payload.name,
      email: payload.email,
      password: payload.password,
      role: payload.role || 'agency',
      isActive: payload.isActive ?? true,
    })

    await user.load('managerRoles')

    return response.created(user)
  }

  /**
   * Aggiorna utente esistente
   */
  async update({ params, request, response }: HttpContext) {
    const user = await User.findOrFail(params.id)
    const payload = await request.validateUsing(updateUserValidator)

    const filteredPayload = Object.fromEntries(
      Object.entries(payload).filter(([_, value]) => value !== undefined)
    )

    user.merge(filteredPayload)
    await user.save()

    await user.load('managerRoles')

    return response.ok(user)
  }

  /**
   * Elimina utente
   */
  async destroy({ params, response }: HttpContext) {
    const user = await User.findOrFail(params.id)

    await user.delete()

    return response.noContent()
  }

  /**
   * Attiva/disattiva utente
   */
  async toggleActive({ params, response }: HttpContext) {
    const user = await User.findOrFail(params.id)

    user.isActive = !user.isActive
    await user.save()

    return response.ok({
      user,
      message: `Utente ${user.isActive ? 'attivato' : 'disattivato'} con successo`,
    })
  }
}