import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'navigation'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('nav_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.string('name').notNullable()
      table.enum('type', ['header', 'footer', 'sidebar', 'custom']).defaultTo('header')
      table.jsonb('menu_items').nullable()
      table.integer('position').defaultTo(0)
      table.boolean('is_active').defaultTo(true)
      table.string('breakpoint').nullable()
      table.text('content_html').nullable()
      table.text('content_css').nullable()
      table.text('content_js').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['website_id'])
      table.index(['type'])
      table.index(['is_active'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}