import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'agency_addresses'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('address_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.enum('address_type', ['billing', 'shipping', 'registered', 'other']).defaultTo('billing')
      table.string('address_line1').notNullable()
      table.string('address_line2').nullable()
      table.string('city').notNullable()
      table.string('state').nullable()
      table.string('postal_code').notNullable()
      table.string('country').notNullable()
      table.boolean('is_primary').defaultTo(false)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
      table.index(['address_type'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}