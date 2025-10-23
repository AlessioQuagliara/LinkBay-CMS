/**
 * LinkBay CMS - BillingInfo Model
 * @author Alessio Quagliara
 * @description Informazioni di fatturazione
 */

import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class BillingInfo extends BaseModel {
  static table = 'billing_info'

  @column({ isPrimary: true, columnName: 'billing_info_id' })
  declare billingInfoId: string

  @column({ columnName: 'company_name' })
  declare companyName: string | null

  @column({ columnName: 'vat_number' })
  declare vatNumber: string | null

  @column({ columnName: 'fiscal_code' })
  declare fiscalCode: string | null

  @column({ columnName: 'address_line1' })
  declare addressLine1: string

  @column({ columnName: 'address_line2' })
  declare addressLine2: string | null

  @column()
  declare city: string

  @column()
  declare state: string | null

  @column({ columnName: 'postal_code' })
  declare postalCode: string

  @column()
  declare country: string

  @column()
  declare email: string | null

  @column()
  declare phone: string | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime
}