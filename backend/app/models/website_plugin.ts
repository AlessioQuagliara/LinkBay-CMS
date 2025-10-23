/**
 * LinkBay CMS - WebsitePlugin Model
 * @author Alessio Quagliara
 * @description Plugin installati sui siti web
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'
import PluginsMarket from '#models/plugins_market'

export default class WebsitePlugin extends BaseModel {
  static table = 'website_plugins'

  @column({ isPrimary: true, columnName: 'website_plugin_id' })
  declare websitePluginId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column({ columnName: 'market_plugin_id' })
  declare marketPluginId: string

  @column()
  declare version: string

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare config: Record<string, any> | null

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column.dateTime({ columnName: 'installed_at' })
  declare installedAt: DateTime

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => Website, { foreignKey: 'websiteId' })
  declare website: BelongsTo<typeof Website>

  @belongsTo(() => PluginsMarket, { foreignKey: 'marketPluginId' })
  declare marketPlugin: BelongsTo<typeof PluginsMarket>
}