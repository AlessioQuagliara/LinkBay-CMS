/**
 * LinkBay CMS - Agency Model
 * 
 * @author Alessio Quagliara
 * @description Modello agenzia - gestisce i clienti e i siti web
 * Ogni agenzia appartiene a un utente
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import User from '#models/user'
import Website from '#models/website'
import Customer from '#models/customer'

export default class Agency extends BaseModel {
  // ===== PRIMARY KEY =====
  @column({ isPrimary: true })
  declare id: string

  // ===== BASIC FIELDS =====
  @column()
  declare name: string

  @column()
  declare description: string | null

  @column()
  declare logo: string | null

  @column()
  declare isActive: boolean

  // ===== FOREIGN KEYS =====
  @column()
  declare userId: string

  // ===== TIMESTAMPS =====
  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  // ===== RELATIONSHIPS =====
  @belongsTo(() => User)
  declare user: BelongsTo<typeof User>

  @hasMany(() => Website)
  declare websites: HasMany<typeof Website>

  @hasMany(() => Customer)
  declare customers: HasMany<typeof Customer>
}