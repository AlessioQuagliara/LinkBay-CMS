import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'websites'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('website_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('tenant_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.uuid('workspace_id').references('workspace_id').inTable('workspaces').onDelete('CASCADE')
      table.uuid('website_config_id').references('website_config_id').inTable('website_config').onDelete('SET NULL')
      table.string('name').notNullable()
      table.text('description').nullable()
      table.string('industry').nullable()
      table.string('currency').defaultTo('EUR')
      table.string('language').defaultTo('it')
      table.string('timezone').defaultTo('Europe/Rome')
      table.uuid('subscription_user_id').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['tenant_id'])
      table.index(['workspace_id'])
      table.index(['website_config_id'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}