/**
 * LinkBay CMS - UserTenant Model
 * @author Alessio Quagliara
 * @description Utenti end-user (clienti delle agenzie)
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo, hasOne, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasOne, HasMany } from '@adonisjs/lucid/types/relations'
import Website from '#models/website'
import TenantsConfig from '#models/tenants_config'
import SubscriptionUser from '#models/subscription_user'

export default class UserTenant extends BaseModel {
  static table = 'user_tenant'

  @column({ isPrimary: true, columnName: 'tenant_user_id' })
  declare tenantUserId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string

  @column()
  declare email: string

  @column({ serializeAs: null, columnName: 'password_hash' })
  declare passwordHash: string

  @column({ columnName: 'first_name' })
  declare firstName: string

  @column({ columnName: 'last_name' })
  declare lastName: string

  @column()
  declare role: 'owner' | 'admin' | 'editor' | 'viewer' | 'customer'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare permissions: Record<string, any> | null

  @column({ columnName: 'email_verified' })
  declare emailVerified: boolean

  @column.dateTime({ columnName: 'last_login' })
  declare lastLogin: DateTime | null

  @column()
  declare timezone: string | null

  @column()
  declare language: string

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => Website, { foreignKey: 'websiteId' })
  declare website: BelongsTo<typeof Website>

  @hasOne(() => TenantsConfig, { foreignKey: 'tenantUserId' })
  declare config: HasOne<typeof TenantsConfig>

  @hasMany(() => SubscriptionUser, { foreignKey: 'tenantUserId' })
  declare subscriptions: HasMany<typeof SubscriptionUser>
}