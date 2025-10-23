/**
 * LinkBay CMS - Page Model
 * @author Alessio Quagliara
 * @description Pagine dei siti web
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasOne } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasOne } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'
import Seo from '#models/seo'

export default class Page extends BaseModel {
  static table = 'pages'

  @column({ isPrimary: true, columnName: 'page_id' })
  declare pageId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column()
  declare slug: string

  @column()
  declare title: string

  @column({ columnName: 'content_html' })
  declare contentHtml: string | null

  @column({ columnName: 'content_css' })
  declare contentCss: string | null

  @column({ columnName: 'content_js' })
  declare contentJs: string | null

  @column({ columnName: 'page_type' })
  declare pageType: 'standard' | 'homepage' | 'blog' | 'product' | 'contact' | 'custom'

  @column()
  declare language: string

  @column({ columnName: 'is_published' })
  declare isPublished: boolean

  @column({ columnName: 'published_at' })
  declare publishedAt: DateTime | null

  @column({ columnName: 'sort_order' })
  declare sortOrder: number

  @column({ columnName: 'parent_page_id' })
  declare parentPageId: string | null

  @column({ columnName: 'template_used' })
  declare templateUsed: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'seo_settings'
  })
  declare seoSettings: Record<string, any> | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => Website, { foreignKey: 'websiteId' })
  declare website: BelongsTo<typeof Website>

  @hasOne(() => Seo, { foreignKey: 'pageId' })
  declare seo: HasOne<typeof Seo>
}