import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'marketplace_transactions'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('transaction_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.string('stripe_payment_intent_id').notNullable()
      table.string('stripe_transfer_id').nullable()
      table.decimal('amount', 10, 2).notNullable()
      table.string('currency').defaultTo('EUR')
      table.decimal('commission_rate', 5, 2).notNullable()
      table.decimal('commission_amount', 10, 2).notNullable()
      table.decimal('net_amount', 10, 2).notNullable()
      table.enum('status', ['pending', 'succeeded', 'failed', 'refunded']).defaultTo('pending')
      table.string('connected_account_id').nullable()
      table.jsonb('metadata').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
      table.index(['status'])
      table.index(['stripe_payment_intent_id'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}