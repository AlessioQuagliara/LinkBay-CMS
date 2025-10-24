/**
 * LinkBay CMS - Workspace Model
 * @author Alessio Quagliara
 * @description Configurazione workspace per agenzia
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'

export default class Workspace extends BaseModel {
  static table = 'workspaces'

  @column({ isPrimary: true, columnName: 'workspace_id' })
  declare workspaceId: string

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column()
  declare slug: string

  @column()
  declare name: string

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
  })
  declare config: Record<string, any> | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}