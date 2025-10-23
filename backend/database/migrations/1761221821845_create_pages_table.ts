import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'pages'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('page_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.string('slug').notNullable()
      table.string('title').notNullable()
      table.text('content_html').nullable()
      table.text('content_css').nullable()
      table.text('content_js').nullable()
      table.enum('page_type', ['standard', 'homepage', 'blog', 'product', 'contact', 'custom']).defaultTo('standard')
      table.string('language').defaultTo('it')
      table.boolean('is_published').defaultTo(false)
      table.timestamp('published_at', { useTz: true }).nullable()
      table.integer('sort_order').defaultTo(0)
      table.uuid('parent_page_id').nullable()
      table.string('template_used').nullable()
      table.jsonb('seo_settings').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['website_id'])
      table.index(['slug'])
      table.index(['page_type'])
      table.index(['is_published'])
      table.foreign('parent_page_id').references('page_id').inTable('pages').onDelete('SET NULL')
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}