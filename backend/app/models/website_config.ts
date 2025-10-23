/**
 * LinkBay CMS - WebsiteConfig Model
 * @author Alessio Quagliara
 * @description Configurazione generale dei website
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import DomainMap from '#models/domain_map'
import WebsiteTheme from '#models/website_theme'

export default class WebsiteConfig extends BaseModel {
  static table = 'website_config'

  @column({ isPrimary: true, columnName: 'website_config_id' })
  declare websiteConfigId: string

  @column({ columnName: 'domain_map_id' })
  declare domainMapId: string | null

  @column({ columnName: 'website_theme_id' })
  declare websiteThemeId: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'web_settings'
  })
  declare webSettings: Record<string, any> | null

  @column()
  declare status: 'suspended' | 'active' | 'maintenance'

  @column({ columnName: 'theme_selected' })
  declare themeSelected: string | null

  @column({ columnName: 'theme_market_id' })
  declare themeMarketId: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'seo_settings'
  })
  declare seoSettings: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'payment_gateways'
  })
  declare paymentGateways: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'shipping_config'
  })
  declare shippingConfig: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'tax_config'
  })
  declare taxConfig: Record<string, any> | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => DomainMap, { foreignKey: 'domainMapId' })
  declare domain: BelongsTo<typeof DomainMap>

  @hasMany(() => WebsiteTheme)
  declare themes: HasMany<typeof WebsiteTheme>
}