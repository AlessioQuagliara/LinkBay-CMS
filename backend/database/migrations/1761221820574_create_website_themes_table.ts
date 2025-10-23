import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'website_themes'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('website_theme_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.uuid('market_theme_id').nullable().references('market_theme_id').inTable('themes_market').onDelete('SET NULL')
      table.text('custom_css').nullable()
      table.text('custom_js').nullable()
      table.jsonb('layout_overrides').nullable()
      table.boolean('is_active').defaultTo(true)
      table.timestamp('installed_at', { useTz: true }).defaultTo(this.now())

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['website_id'])
      table.index(['market_theme_id'])
      table.index(['is_active'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}