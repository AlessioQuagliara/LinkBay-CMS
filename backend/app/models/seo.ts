/**
 * LinkBay CMS - Seo Model
 * @author Alessio Quagliara
 * @description Configurazione SEO per pagine
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import Page from '#models/page'

export default class Seo extends BaseModel {
  static table = 'seo'

  @column({ isPrimary: true, columnName: 'seo_id' })
  declare seoId: string

  @column({ columnName: 'page_id' })
  declare pageId: string

  @column({ columnName: 'page_slug' })
  declare pageSlug: string

  @column({ columnName: 'meta_title' })
  declare metaTitle: string | null

  @column({ columnName: 'meta_description' })
  declare metaDescription: string | null

  @column({ columnName: 'meta_keywords' })
  declare metaKeywords: string | null

  @column({ columnName: 'og_title' })
  declare ogTitle: string | null

  @column({ columnName: 'og_description' })
  declare ogDescription: string | null

  @column({ columnName: 'og_image' })
  declare ogImage: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'structured_data'
  })
  declare structuredData: Record<string, any> | null

  @column({ columnName: 'canonical_url' })
  declare canonicalUrl: string | null

  @column({ columnName: 'robots_txt' })
  declare robotsTxt: string | null

  @column({ columnName: 'sitemap_priority' })
  declare sitemapPriority: number

  @column({ columnName: 'sitemap_change_freq' })
  declare sitemapChangeFreq: string | null

  @column()
  declare noindex: boolean

  @column()
  declare nofollow: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => Page, { foreignKey: 'pageId' })
  declare page: BelongsTo<typeof Page>
}