/**
 * LinkBay CMS - Website Model
 * 
 * @author Alessio Quagliara
 * @description Modello sito web - gestito da un'agenzia per un cliente
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Agency from '#models/agency'
import Customer from '#models/customer'

export default class Website extends BaseModel {
  // ===== PRIMARY KEY =====
  @column({ isPrimary: true })
  declare id: string

  // ===== BASIC FIELDS =====
  @column()
  declare name: string

  @column()
  declare domain: string

  @column()
  declare description: string | null

  @column()
  declare logo: string | null

  @column()
  declare status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE'

  // ===== FOREIGN KEYS =====
  @column()
  declare agencyId: string

  @column()
  declare customerId: string | null

  // ===== TIMESTAMPS =====
  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  // ===== RELATIONSHIPS =====
  @belongsTo(() => Agency)
  declare agency: BelongsTo<typeof Agency>

  @belongsTo(() => Customer)
  declare customer: BelongsTo<typeof Customer>
}