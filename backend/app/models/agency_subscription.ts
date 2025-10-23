/**
 * LinkBay CMS - AgencySubscription Model
 * @author Alessio Quagliara
 * @description Piani di sottoscrizione per le agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class AgencySubscription extends BaseModel {
  static table = 'agency_subscriptions'

  @column({ isPrimary: true, columnName: 'agency_subscription_id' })
  declare agencySubscriptionId: string

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

  @column({ columnName: 'max_websites' })
  declare maxWebsites: number | null

  @column({ columnName: 'max_managers' })
  declare maxManagers: number | null

  @column({ columnName: 'storage_limit_gb' })
  declare storageLimitGb: number | null

  @column({ columnName: 'white_label_enabled' })
  declare whiteLabelEnabled: boolean

  @column({ columnName: 'custom_domain_enabled' })
  declare customDomainEnabled: boolean

  @column({ columnName: 'api_access_enabled' })
  declare apiAccessEnabled: boolean

  @column({ columnName: 'is_active' })
  declare isActive: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime
}