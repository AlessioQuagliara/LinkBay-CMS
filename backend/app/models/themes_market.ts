/**
 * LinkBay CMS - ThemesMarket Model
 * @author Alessio Quagliara
 * @description Temi del marketplace
 */

import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class ThemesMarket extends BaseModel {
  static table = 'themes_market'

  @column({ isPrimary: true, columnName: 'market_theme_id' })
  declare marketThemeId: string

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

  @column({ columnName: 'preview_image_url' })
  declare previewImageUrl: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'theme_files'
  })
  declare themeFiles: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'style_config'
  })
  declare styleConfig: Record<string, any> | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'supported_components'
  })
  declare supportedComponents: Record<string, any> | null

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column({ columnName: 'download_count' })
  declare downloadCount: number

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime
}