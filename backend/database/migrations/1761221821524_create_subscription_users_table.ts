import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'subscription_user'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('subscription_user_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('tenant_user_id').references('tenant_user_id').inTable('user_tenant').onDelete('CASCADE')
      table.uuid('subscription_id').references('subscription_id').inTable('subscriptions').onDelete('CASCADE')
      table.enum('billing_cycle', ['monthly', 'yearly']).defaultTo('monthly')
      table.enum('status', ['active', 'canceled', 'past_due', 'trialing', 'expired']).defaultTo('trialing')
      table.decimal('price', 10, 2).notNullable()
      table.string('currency').defaultTo('EUR')
      table.string('stripe_subscription_id').nullable()
      table.string('paypal_subscription_id').nullable()
      table.timestamp('current_period_start', { useTz: true }).nullable()
      table.timestamp('current_period_end', { useTz: true }).nullable()
      table.timestamp('trial_end', { useTz: true }).nullable()
      table.timestamp('canceled_at', { useTz: true }).nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['tenant_user_id'])
      table.index(['subscription_id'])
      table.index(['status'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}