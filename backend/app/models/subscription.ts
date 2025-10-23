/**
 * LinkBay CMS - Subscription Model
 * @author Alessio Quagliara
 * @description Piani di sottoscrizione disponibili per end-user
 */

import { DateTime } from 'luxon'
import { BaseModel, column, hasMany } from '@adonisjs/lucid/orm'
import type { HasMany } from '@adonisjs/lucid/types/relations'
import SubscriptionUser from '#models/subscription_user'

export default class Subscription extends BaseModel {
  static table = 'subscriptions'

  @column({ isPrimary: true, columnName: 'subscription_id' })
  declare subscriptionId: string

  @column()
  declare name: string

  @column()
  declare description: string | null

  @column()
  declare price: number

  @column()
  declare currency: string

  @column({ columnName: 'billing_cycle' })
  declare billingCycle: 'monthly' | 'yearly'

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare features: Record<string, any> | null

  @column({ columnName: 'max_products' })
  declare maxProducts: number | null

  @column({ columnName: 'max_users' })
  declare maxUsers: number | null

  @column({ columnName: 'storage_limit_mb' })
  declare storageLimitMb: number | null

  @column({ columnName: 'api_rate_limit' })
  declare apiRateLimit: number | null

  @column({ columnName: 'stripe_price_id' })
  declare stripePriceId: string | null

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @hasMany(() => SubscriptionUser, { foreignKey: 'subscriptionId' })
  declare subscriptionUsers: HasMany<typeof SubscriptionUser>
}