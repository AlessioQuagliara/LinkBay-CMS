import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'workspaces'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('workspace_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('agency_id').references('agency_id').inTable('agency_tenants').onDelete('CASCADE')
      table.string('slug').unique().notNullable()
      table.string('name').notNullable()
      table.jsonb('config').nullable()

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['agency_id'])
      table.index(['slug'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}