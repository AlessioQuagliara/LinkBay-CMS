import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'footing'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('footer_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.string('name').notNullable()
      table.enum('type', ['main', 'secondary', 'minimal', 'custom']).defaultTo('main')
      table.jsonb('content').nullable()
      table.integer('position').defaultTo(0)
      table.integer('columns').defaultTo(4)
      table.boolean('is_active').defaultTo(true)
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