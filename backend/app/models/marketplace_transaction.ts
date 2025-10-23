/**
 * LinkBay CMS - MarketplaceTransaction Model
 * @author Alessio Quagliara
 * @description Transazioni marketplace con Stripe Connect
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'

export default class MarketplaceTransaction extends BaseModel {
  static table = 'marketplace_transactions'

  @column({ isPrimary: true, columnName: 'transaction_id' })
  declare transactionId: string

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'stripe_payment_intent_id' })
  declare stripePaymentIntentId: string

  @column({ columnName: 'stripe_transfer_id' })
  declare stripeTransferId: string | null

  @column()
  declare amount: number

  @column()
  declare currency: string

  @column({ columnName: 'commission_rate' })
  declare commissionRate: number

  @column({ columnName: 'commission_amount' })
  declare commissionAmount: number

  @column({ columnName: 'net_amount' })
  declare netAmount: number

  @column()
  declare status: 'pending' | 'succeeded' | 'failed' | 'refunded'

  @column({ columnName: 'connected_account_id' })
  declare connectedAccountId: string | null

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value)
  })
  declare metadata: Record<string, any> | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}