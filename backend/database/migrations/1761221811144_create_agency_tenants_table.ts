import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'agency_tenants'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('agency_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('workspace_id').nullable()
      table.string('name').notNullable()
      table.enum('status', ['active', 'suspended', 'pending']).defaultTo('pending')
      table.jsonb('white_label_config').nullable()
      table.string('subscription_tier').defaultTo('starter')
      table.integer('max_websites').defaultTo(1)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['status'])
      table.index(['subscription_tier'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}