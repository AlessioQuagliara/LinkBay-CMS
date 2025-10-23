/**
 * LinkBay CMS - AgencyInfo Model
 * @author Alessio Quagliara
 * @description Informazioni dettagliate delle agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'

export default class AgencyInfo extends BaseModel {
  static table = 'agency_info'

  @column({ isPrimary: true, columnName: 'agency_info_id' })
  declare agencyInfoId: string

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'legal_name' })
  declare legalName: string

  @column({ columnName: 'trading_name' })
  declare tradingName: string | null

  @column()
  declare description: string | null

  @column({ columnName: 'logo_url' })
  declare logoUrl: string | null

  @column()
  declare website: string | null

  @column()
  declare industry: string | null

  @column({ columnName: 'tax_id' })
  declare taxId: string | null

  @column({ columnName: 'support_email' })
  declare supportEmail: string | null

  @column({ columnName: 'support_phone' })
  declare supportPhone: string | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}