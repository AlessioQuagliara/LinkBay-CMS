/**
 * LinkBay CMS - AuditLog Model
 * @author Alessio Quagliara
 * @description Log di audit per tracciare azioni degli utenti
 */

import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class AuditLog extends BaseModel {
  static table = 'audit_logs'

  @column({ isPrimary: true, columnName: 'log_id' })
  declare logId: string

  @column({ columnName: 'user_id' })
  declare userId: number | null

  @column({ columnName: 'agency_id' })
  declare agencyId: string | null

  @column()
  declare action: string

  @column({ columnName: 'resource_type' })
  declare resourceType: string | null

  @column({ columnName: 'resource_id' })
  declare resourceId: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'old_values'
  })
  declare oldValues: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'new_values'
  })
  declare newValues: Record<string, any> | null

  @column({ columnName: 'ip_address' })
  declare ipAddress: string | null

  @column({ columnName: 'user_agent' })
  declare userAgent: string | null

  @column.dateTime({ autoCreate: true })
  declare timestamp: DateTime

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime
}