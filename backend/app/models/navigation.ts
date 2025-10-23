/**
 * LinkBay CMS - Navigation Model
 * @author Alessio Quagliara
 * @description Menu di navigazione dei siti web
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'

export default class Navigation extends BaseModel {
  static table = 'navigation'

  @column({ isPrimary: true, columnName: 'nav_id' })
  declare navId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column()
  declare name: string

  @column()
  declare type: 'header' | 'footer' | 'sidebar' | 'custom'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'menu_items'
  })
  declare menuItems: Record<string, any> | null

  @column()
  declare position: number

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column()
  declare breakpoint: string | null

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