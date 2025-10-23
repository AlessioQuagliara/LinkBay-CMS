/**
 * LinkBay CMS - UserManager Model
 * @author Alessio Quagliara
 * @description Manager/staff delle agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import User from '#models/user'
import AgencyTenant from '#models/agency_tenant'

export default class UserManager extends BaseModel {
  static table = 'user_manager'

  @column({ isPrimary: true, columnName: 'manager_id' })
  declare managerId: string

  @column({ columnName: 'user_id' })
  declare userId: number

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column()
  declare role: 'owner' | 'admin' | 'manager' | 'staff'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare permissions: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'assigned_websites'
  })
  declare assignedWebsites: string[] | null

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => User, { foreignKey: 'userId' })
  declare user: BelongsTo<typeof User>

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}