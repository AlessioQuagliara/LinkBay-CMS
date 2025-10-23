/**
 * LinkBay CMS - WebsiteTheme Model
 * @author Alessio Quagliara
 * @description Temi installati sui siti web
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'
import ThemesMarket from '#models/themes_market'

export default class WebsiteTheme extends BaseModel {
  static table = 'website_themes'

  @column({ isPrimary: true, columnName: 'website_theme_id' })
  declare websiteThemeId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column({ columnName: 'market_theme_id' })
  declare marketThemeId: string | null

  @column({ columnName: 'custom_css' })
  declare customCss: string | null

  @column({ columnName: 'custom_js' })
  declare customJs: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'layout_overrides'
  })
  declare layoutOverrides: Record<string, any> | null

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

  @belongsTo(() => ThemesMarket, { foreignKey: 'marketThemeId' })
  declare marketTheme: BelongsTo<typeof ThemesMarket>
}