import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'plugins_market'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('market_plugin_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('name').notNullable()
      table.text('description').nullable()
      table.string('version').notNullable()
      table.string('author').nullable()
      table.decimal('price', 10, 2).defaultTo(0)
      table.string('category').nullable()
      table.enum('plugin_type', ['widget', 'integration', 'analytics', 'seo', 'payment', 'other']).defaultTo('widget')
      table.jsonb('compatibility').nullable()
      table.string('download_url').nullable()
      table.decimal('rating', 3, 2).nullable()
      table.integer('download_count').defaultTo(0)
      table.boolean('is_active').defaultTo(true)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['is_active'])
      table.index(['plugin_type'])
      table.index(['category'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}