import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'audit_logs'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('log_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.integer('user_id').nullable().unsigned().references('user_id').inTable('users').onDelete('SET NULL')
      table.uuid('agency_id').nullable()
      table.string('action').notNullable()
      table.string('resource_type').nullable()
      table.string('resource_id').nullable()
      table.jsonb('old_values').nullable()
      table.jsonb('new_values').nullable()
      table.specificType('ip_address', 'inet').nullable()
      table.string('user_agent').nullable()
      table.timestamp('timestamp', { useTz: true }).defaultTo(this.now())

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['user_id'])
      table.index(['agency_id'])
      table.index(['action'])
      table.index(['resource_type'])
      table.index(['timestamp'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}