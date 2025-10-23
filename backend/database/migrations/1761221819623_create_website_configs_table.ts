import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'website_config'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('website_config_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.jsonb('web_settings').nullable()
      table.jsonb('seo_settings').nullable()
      table.jsonb('payment_gateways').nullable()
      table.jsonb('shipping_config').nullable()
      table.jsonb('tax_config').nullable()
      table.enum('status', ['active', 'draft', 'archived']).defaultTo('draft')

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['status'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}