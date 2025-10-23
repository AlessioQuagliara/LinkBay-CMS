import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'agency_info'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('agency_info_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.string('legal_name').notNullable()
      table.string('trading_name').nullable()
      table.text('description').nullable()
      table.string('logo_url').nullable()
      table.string('website').nullable()
      table.string('industry').nullable()
      table.string('tax_id').nullable()
      table.string('support_email').nullable()
      table.string('support_phone').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}