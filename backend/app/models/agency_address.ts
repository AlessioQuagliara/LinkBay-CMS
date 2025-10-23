/**
 * LinkBay CMS - AgencyAddress Model
 * @author Alessio Quagliara
 * @description Indirizzi delle agenzie
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'

export default class AgencyAddress extends BaseModel {
  static table = 'agency_addresses'

  @column({ isPrimary: true, columnName: 'address_id' })
  declare addressId: string

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'address_type' })
  declare addressType: 'billing' | 'shipping' | 'registered' | 'other'

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

  @column({ columnName: 'is_primary' })
  declare isPrimary: boolean

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>
}