import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'agency_subscriptions'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('agency_subscription_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('name').notNullable()
      table.text('description').nullable()
      table.decimal('price', 10, 2).notNullable()
      table.string('currency').defaultTo('EUR')
      table.enum('billing_cycle', ['monthly', 'yearly']).defaultTo('monthly')
      table.jsonb('features').nullable()
      table.integer('max_websites').nullable()
      table.integer('max_managers').nullable()
      table.integer('storage_limit_gb').nullable()
      table.boolean('white_label_enabled').defaultTo(false)
      table.boolean('custom_domain_enabled').defaultTo(false)
      table.boolean('api_access_enabled').defaultTo(false)
      table.boolean('is_active').defaultTo(true)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['is_active'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}