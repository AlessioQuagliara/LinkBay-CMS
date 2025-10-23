import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'themes_market'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('market_theme_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('name').notNullable()
      table.text('description').nullable()
      table.string('version').notNullable()
      table.string('author').nullable()
      table.decimal('price', 10, 2).defaultTo(0)
      table.string('category').nullable()
      table.string('preview_image_url').nullable()
      table.jsonb('theme_files').nullable()
      table.jsonb('style_config').nullable()
      table.jsonb('supported_components').nullable()
      table.boolean('is_active').defaultTo(true)
      table.integer('download_count').defaultTo(0)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['is_active'])
      table.index(['category'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}