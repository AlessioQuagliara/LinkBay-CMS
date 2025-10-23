import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'tenants_config'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('tenant_config_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('tenant_user_id').references('tenant_user_id').inTable('user_tenant').onDelete('CASCADE')
      table.uuid('billing_info_id').nullable().references('billing_info_id').inTable('billing_info').onDelete('SET NULL')
      table.integer('max_products').defaultTo(100)
      table.integer('max_users').defaultTo(10)
      table.jsonb('features_allowed').nullable()
      table.integer('api_rate_limit').defaultTo(1000)
      table.integer('storage_limit_mb').defaultTo(1000)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['tenant_user_id'])
      table.index(['billing_info_id'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}