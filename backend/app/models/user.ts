/**
 * LinkBay CMS - User Model
 * 
 * @author Alessio Quagliara
 * @description Modello utente principale del sistema (agenzie)
 * Gestisce autenticazione e relazioni con agenzie e token
 */

import { DateTime } from 'luxon'
import hash from '@adonisjs/core/services/hash'
import { compose } from '@adonisjs/core/helpers'
import { BaseModel, column, hasMany } from '@adonisjs/lucid/orm'
import { withAuthFinder } from '@adonisjs/auth/mixins/lucid'
import { DbAccessTokensProvider } from '@adonisjs/auth/access_tokens'
import type { HasMany } from '@adonisjs/lucid/types/relations'
import Agency from '#models/agency'

const AuthFinder = withAuthFinder(() => hash.use('scrypt'), {
  uids: ['email'],
  passwordColumnName: 'password',
})

export default class User extends compose(BaseModel, AuthFinder) {
  // ===== PRIMARY KEY =====
  @column({ isPrimary: true })
  declare id: string

  // ===== BASIC FIELDS =====
  @column()
  declare name: string

  @column()
  declare email: string

  @column({ serializeAs: null })
  declare password: string

  @column()
  declare role: 'AGENCY' | 'ADMIN'

  @column()
  declare isActive: boolean

  // ===== TIMESTAMPS =====
  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  // ===== RELATIONSHIPS =====
  @hasMany(() => Agency)
  declare agencies: HasMany<typeof Agency>

  // ===== AUTH TOKENS =====
  static accessTokens = DbAccessTokensProvider.forModel(User)
}