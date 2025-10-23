/**
 * LinkBay CMS - Website Model
 * @author Alessio Quagliara  
 * @description Website effettivi gestiti dalle agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'
import Workspace from '#models/workspace'
import WebsiteConfig from '#models/website_config'
import UserTenant from '#models/user_tenant'
import Page from '#models/page'

export default class Website extends BaseModel {
  static table = 'websites'

  @column({ isPrimary: true, columnName: 'website_id' })
  declare websiteId: string

  @column({ columnName: 'tenant_id' })
  declare tenantId: string

  @column({ columnName: 'workspace_id' })
  declare workspaceId: string

  @column({ columnName: 'website_config_id' })
  declare websiteConfigId: string

  @column()
  declare name: string

  @column()
  declare description: string | null

  @column()
  declare industry: string | null

  @column()
  declare currency: string

  @column()
  declare language: string

  @column()
  declare timezone: string

  @column({ columnName: 'subscription_user_id' })
  declare subscriptionUserId: string | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'tenantId' })
  declare agency: BelongsTo<typeof AgencyTenant>

  @belongsTo(() => Workspace, { foreignKey: 'workspaceId' })
  declare workspace: BelongsTo<typeof Workspace>

  @belongsTo(() => WebsiteConfig, { foreignKey: 'websiteConfigId' })
  declare config: BelongsTo<typeof WebsiteConfig>

  @hasMany(() => UserTenant, { foreignKey: 'websiteId' })
  declare users: HasMany<typeof UserTenant>

  @hasMany(() => Page, { foreignKey: 'websiteId' })
  declare pages: HasMany<typeof Page>
}