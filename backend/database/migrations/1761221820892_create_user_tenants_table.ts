import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'user_tenant'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.uuid('tenant_user_id').primary().defaultTo(this.raw('gen_random_uuid()'))
      table.uuid('website_id').references('website_id').inTable('websites').onDelete('CASCADE')
      table.string('email').notNullable().unique()
      table.string('password_hash').notNullable()
      table.string('first_name').notNullable()
      table.string('last_name').notNullable()
      table.enum('role', ['owner', 'admin', 'editor', 'viewer', 'customer']).defaultTo('customer')
      table.jsonb('permissions').nullable()
      table.boolean('email_verified').defaultTo(false)
      table.timestamp('last_login', { useTz: true }).nullable()
      table.string('timezone').defaultTo('Europe/Rome')
      table.string('language').defaultTo('it')

      table.timestamp('created_at', { useTz: true }).defaultTo(this.now())
      table.timestamp('updated_at', { useTz: true }).defaultTo(this.now())

      table.index(['website_id'])
      table.index(['email'])
      table.index(['role'])
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}