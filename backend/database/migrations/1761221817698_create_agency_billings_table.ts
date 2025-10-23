import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'agency_billing'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('billing_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.enum('payment_method', ['credit_card', 'paypal', 'bank_transfer', 'other']).defaultTo('credit_card')
      table.enum('billing_cycle', ['monthly', 'yearly']).defaultTo('monthly')
      table.string('stripe_customer_id').nullable()
      table.string('paypal_email').nullable()
      table.string('invoice_prefix').nullable()
      table.decimal('tax_rate', 5, 2).defaultTo(0)
      table.timestamp('next_billing_date', { useTz: true }).nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}