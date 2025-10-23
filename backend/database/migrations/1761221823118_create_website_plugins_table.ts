import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'website_plugin'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('website_plugin_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.uuid('plugin_id').references('market_plugin_id').inTable('plugins_market').onDelete('CASCADE')
      table.string('version').notNullable()
      table.jsonb('config').nullable()
      table.boolean('is_active').defaultTo(true)
      table.timestamp('installed_at', { useTz: true }).defaultTo(this.now())

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['website_id'])
      table.index(['plugin_id'])
      table.index(['is_active'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}