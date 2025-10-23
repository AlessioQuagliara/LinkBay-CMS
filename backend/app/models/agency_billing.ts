/**
 * LinkBay CMS - AgencyBilling Model
 * @author Alessio Quagliara
 * @description Configurazione di fatturazione delle agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'

export default class AgencyBilling extends BaseModel {
  static table = 'agency_billing'

  @column({ isPrimary: true, columnName: 'billing_id' })
  declare billingId: string

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'payment_method' })
  declare paymentMethod: 'credit_card' | 'paypal' | 'bank_transfer' | 'other'

  @column({ columnName: 'billing_cycle' })
  declare billingCycle: 'monthly' | 'yearly'

  @column({ columnName: 'stripe_customer_id' })
  declare stripeCustomerId: string | null

  @column({ columnName: 'paypal_email' })
  declare paypalEmail: string | null

  @column({ columnName: 'invoice_prefix' })
  declare invoicePrefix: string | null

  @column({ columnName: 'tax_rate' })
  declare taxRate: number

  @column.dateTime({ columnName: 'next_billing_date' })
  declare nextBillingDate: DateTime | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}