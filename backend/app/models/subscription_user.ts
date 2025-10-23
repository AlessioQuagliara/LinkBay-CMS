/**
 * LinkBay CMS - SubscriptionUser Model
 * @author Alessio Quagliara
 * @description Sottoscrizioni attive degli utenti end-user
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import UserTenant from '#models/user_tenant'
import Subscription from '#models/subscription'

export default class SubscriptionUser extends BaseModel {
  static table = 'subscription_user'

  @column({ isPrimary: true, columnName: 'subscription_user_id' })
  declare subscriptionUserId: string

  @column({ columnName: 'tenant_user_id' })
  declare tenantUserId: string

  @column({ columnName: 'subscription_id' })
  declare subscriptionId: string

  @column({ columnName: 'billing_cycle' })
  declare billingCycle: 'monthly' | 'yearly'

  @column()
  declare status: 'active' | 'canceled' | 'past_due' | 'trialing' | 'expired'

  @column()
  declare price: number

  @column()
  declare currency: string

  @column({ columnName: 'stripe_subscription_id' })
  declare stripeSubscriptionId: string | null

  @column({ columnName: 'paypal_subscription_id' })
  declare paypalSubscriptionId: string | null

  @column.dateTime({ columnName: 'current_period_start' })
  declare currentPeriodStart: DateTime | null

  @column.dateTime({ columnName: 'current_period_end' })
  declare currentPeriodEnd: DateTime | null

  @column.dateTime({ columnName: 'trial_end' })
  declare trialEnd: DateTime | null

  @column.dateTime({ columnName: 'canceled_at' })
  declare canceledAt: DateTime | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => UserTenant, { foreignKey: 'tenantUserId' })
  declare tenantUser: BelongsTo<typeof UserTenant>

  @belongsTo(() => Subscription, { foreignKey: 'subscriptionId' })
  declare subscription: BelongsTo<typeof Subscription>
}