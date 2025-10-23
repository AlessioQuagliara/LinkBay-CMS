import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'user_manager'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('manager_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.integer('user_id').unsigned().references('user_id').inTable('users').onDelete('CASCADE')
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.enum('role', ['owner', 'admin', 'manager', 'staff']).defaultTo('staff')
      table.jsonb('permissions').nullable()
      table.jsonb('assigned_websites').nullable()
      table.boolean('is_active').defaultTo(true)

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['user_id'])
      table.index(['agency_id'])
      table.index(['role'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}