import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'seo'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('seo_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('page_id').references('page_id').inTable('pages').onDelete('CASCADE')
      table.string('page_slug').notNullable()
      table.string('meta_title').nullable()
      table.string('meta_description').nullable()
      table.string('meta_keywords').nullable()
      table.string('og_title').nullable()
      table.string('og_description').nullable()
      table.string('og_image').nullable()
      table.jsonb('structured_data').nullable()
      table.string('canonical_url').nullable()
      table.string('robots_txt').nullable()
      table.decimal('sitemap_priority', 2, 1).defaultTo(0.5)
      table.string('sitemap_change_freq').nullable()
      table.boolean('noindex').defaultTo(false)
      table.boolean('nofollow').defaultTo(false)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['page_id'])
      table.index(['page_slug'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}