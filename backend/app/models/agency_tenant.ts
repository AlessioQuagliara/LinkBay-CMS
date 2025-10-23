/**
 * LinkBay CMS - AgencyTenant Model
 * @author Alessio Quagliara
 * @description Tabella principale delle agenzie (tenant)
 */

import { DateTime } from 'luxon'
import { BaseModel, column, hasMany, hasOne } from '@adonisjs/lucid/orm'
import type { HasMany, HasOne } from '@adonisjs/lucid/types/relations'
import Workspace from '#models/workspace'
import Website from '#models/website'
import DomainMap from '#models/domain_map'

export default class AgencyTenant extends BaseModel {
  static table = 'agency_tenant'

  @column({ isPrimary: true, columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'workspace_id' })
  declare workspaceId: string

  @column()
  declare name: string

  @column()
  declare status: string

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'white_label_config'
  })
  declare whiteLabelConfig: Record<string, any> | null

  @column({ columnName: 'subscription_tier' })
  declare subscriptionTier: string

  @column({ columnName: 'max_websites' })
  declare maxWebsites: number

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @hasOne(() => Workspace, { foreignKey: 'agencyId' })
  declare workspace: HasOne<typeof Workspace>

  @hasMany(() => Website, { foreignKey: 'tenantId' })
  declare websites: HasMany<typeof Website>

  @hasMany(() => DomainMap, { foreignKey: 'agencyId' })
  declare domains: HasMany<typeof DomainMap>
}