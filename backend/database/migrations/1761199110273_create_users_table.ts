/**
 * LinkBay CMS - Users Migration
 * 
 * @author Alessio Quagliara
 * @description Tabella utenti - agenzie e admin del sistema
 */

import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'users'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      // Primary Key
      table.uuid('id').primary().defaultTo(this.raw('gen_random_uuid()'))

      // Fields
      table.string('email').notNullable().unique()
      table.string('password').notNullable()
      table.string('name').notNullable()
      table.enum('role', ['AGENCY', 'ADMIN']).defaultTo('AGENCY')
      table.boolean('is_active').defaultTo(true)

      // Timestamps
      table.timestamp('created_at').notNullable()
      table.timestamp('updated_at').notNullable()
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}