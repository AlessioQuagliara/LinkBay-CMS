/**
 * LinkBay CMS - Footing Model
 * @author Alessio Quagliara
 * @description Sezioni footer dei siti web
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'

export default class Footing extends BaseModel {
  static table = 'footing'

  @column({ isPrimary: true, columnName: 'footer_id' })
  declare footerId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column()
  declare name: string

  @column()
  declare type: 'main' | 'secondary' | 'minimal' | 'custom'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare content: Record<string, any> | null

  @column()
  declare position: number

  @column()
  declare columns: number

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column({ columnName: 'content_html' })
  declare contentHtml: string | null

  @column({ columnName: 'content_css' })
  declare contentCss: string | null

  @column({ columnName: 'content_js' })
  declare contentJs: string | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => Website, { foreignKey: 'websiteId' })
  declare website: BelongsTo<typeof Website>
}