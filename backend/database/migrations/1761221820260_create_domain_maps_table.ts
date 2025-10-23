import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'domain_map'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('domain_map_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('domain_name').notNullable()
      table.string('subdomain').nullable()
      table.enum('domain_type', ['primary', 'alias', 'redirect']).defaultTo('primary')
      table.enum('status', ['active', 'pending', 'failed']).defaultTo('pending')
      table.enum('ssl_status', ['none', 'pending', 'active', 'failed']).defaultTo('none')
      table.text('ssl_certificate').nullable()
      table.text('ssl_private_key').nullable()
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
      table.index(['website_id'])
      table.index(['domain_name'])
      table.index(['status'])
      table.index(['ssl_status'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}