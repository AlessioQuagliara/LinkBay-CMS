import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'billing_info'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('billing_info_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.string('company_name').nullable()
      table.string('vat_number').nullable()
      table.string('fiscal_code').nullable()
      table.string('address_line1').notNullable()
      table.string('address_line2').nullable()
      table.string('city').notNullable()
      table.string('state').nullable()
      table.string('postal_code').notNullable()
      table.string('country').notNullable()
      table.string('email').nullable()
      table.string('phone').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}