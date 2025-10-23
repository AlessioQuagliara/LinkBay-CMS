/**
 * LinkBay CMS - Customer Model
 * 
 * @author Alessio Quagliara
 * @description Modello cliente - cliente finale di un'agenzia
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import Agency from '#models/agency'
import Website from '#models/website'

export default class Customer extends BaseModel {
  // ===== PRIMARY KEY =====
  @column({ isPrimary: true })
  declare id: string

  // ===== BASIC FIELDS =====
  @column()
  declare name: string

  @column()
  declare email: string

  @column()
  declare phone: string | null

  @column()
  declare company: string | null

  @column()
  declare isActive: boolean

  // ===== FOREIGN KEYS =====
  @column()
  declare agencyId: string

  // ===== TIMESTAMPS =====
  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  // ===== RELATIONSHIPS =====
  @belongsTo(() => Agency)
  declare agency: BelongsTo<typeof Agency>

  @hasMany(() => Website)
  declare websites: HasMany<typeof Website>
}