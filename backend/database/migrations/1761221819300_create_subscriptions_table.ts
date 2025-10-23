import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'subscriptions'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('subscription_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('name').notNullable()
      table.text('description').nullable()
      table.decimal('price', 10, 2).notNullable()
      table.string('currency').defaultTo('EUR')
      table.enum('billing_cycle', ['monthly', 'yearly']).defaultTo('monthly')
      table.jsonb('features').nullable()
      table.integer('max_products').nullable()
      table.integer('max_users').nullable()
      table.integer('storage_limit_mb').nullable()
      table.integer('api_rate_limit').nullable()
      table.string('stripe_price_id').nullable()
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