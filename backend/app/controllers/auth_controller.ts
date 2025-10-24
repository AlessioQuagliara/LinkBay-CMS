/**
 * LinkBay CMS - Auth Controller
 * @author Alessio Quagliara
 * @description Gestione autenticazione utenti agenzia
 */

import type { HttpContext } from '@adonisjs/core/http'
import User from '#models/user'
import { loginValidator, registerValidator } from '#validators/auth'

export default class AuthController {
  /**
   * Registrazione nuovo utente agenzia
   */
  async register({ request, response }: HttpContext) {
    const payload = await request.validateUsing(registerValidator)

    const user = await User.create({
      name: payload.name,
      email: payload.email,
      password: payload.password,
      role: 'agency',
      isActive: true,
    })

    // Crea token di accesso
    const token = await User.accessTokens.create(user, ['*'], {
      expiresIn: '7 days',
    })

    return response.created({
      user: user.serialize(),
      token: token.toJSON(),
      message: 'Registrazione completata con successo',
    })
  }

  /**
   * Login utente
   */
  async login({ request, response }: HttpContext) {
    const { email, password } = await request.validateUsing(loginValidator)

    // Verifica credenziali
    const user = await User.verifyCredentials(email, password)

    // Controlla se utente è attivo
    if (!user.isActive) {
      return response.forbidden({
        message: 'Account disabilitato. Contatta il supporto.',
      })
    }

    // Crea token di accesso
    const token = await User.accessTokens.create(user, ['*'], {
      expiresIn: '7 days',
    })

    return response.ok({
      user: user.serialize(),
      token: token.toJSON(),
      message: 'Login effettuato con successo',
    })
  }

  /**
   * Logout utente (revoca token)
   */
  async logout({ auth, response }: HttpContext) {
    const user = auth.user!
    await User.accessTokens.delete(user, auth.user!.currentAccessToken.identifier)

    return response.ok({
      message: 'Logout effettuato con successo',
    })
  }

  /**
   * Ottieni profilo utente corrente
   */
  async profile({ auth, response }: HttpContext) {
    const user = auth.user!
    await user.load('managerRoles')

    return response.ok({
      user: user.serialize(),
    })
  }

  /**
   * Refresh token di accesso
   */
  async refresh({ auth, response }: HttpContext) {
    const user = auth.user!

    // Revoca token corrente
    await User.accessTokens.delete(user, auth.user!.currentAccessToken.identifier)

    // Crea nuovo token
    const token = await User.accessTokens.create(user, ['*'], {
      expiresIn: '7 days',
    })

    return response.ok({
      token: token.toJSON(),
      message: 'Token aggiornato con successo',
    })
  }
}