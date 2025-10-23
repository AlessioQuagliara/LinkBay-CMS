/**
 * LinkBay CMS - PluginsMarket Model
 * @author Alessio Quagliara
 * @description Plugin del marketplace
 */

import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class PluginsMarket extends BaseModel {
  static table = 'plugins_market'

  @column({ isPrimary: true, columnName: 'market_plugin_id' })
  declare marketPluginId: string

  @column()
  declare name: string

  @column()
  declare description: string | null

  @column()
  declare version: string

  @column()
  declare author: string | null

  @column()
  declare price: number

  @column()
  declare category: string | null

  @column({ columnName: 'plugin_type' })
  declare pluginType: 'widget' | 'integration' | 'analytics' | 'seo' | 'payment' | 'other'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare compatibility: Record<string, any> | null

  @column({ columnName: 'download_url' })
  declare downloadUrl: string | null

  @column()
  declare rating: number | null

  @column({ columnName: 'download_count' })
  declare downloadCount: number

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime
}