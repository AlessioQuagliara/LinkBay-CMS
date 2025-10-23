/**
 * LinkBay CMS - DomainMap Model
 * @author Alessio Quagliara
 * @description Mappatura domini e sottodomini con SSL
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import AgencyTenant from '#models/agency_tenant'
import Website from '#models/website'

export default class DomainMap extends BaseModel {
  static table = 'domain_map'

  @column({ isPrimary: true, columnName: 'domain_map_id' })
  declare domainMapId: string

  @column({ columnName: 'domain_name' })
  declare domainName: string

  @column()
  declare subdomain: string | null

  @column({ columnName: 'domain_type' })
  declare domainType: 'custom' | 'subdomain' | 'alias'

  @column()
  declare status: 'active' | 'pending' | 'inactive'

  @column({ columnName: 'ssl_status' })
  declare sslStatus: 'active' | 'pending' | 'error'

  @column({ serializeAs: null, columnName: 'ssl_certificate' })
  declare sslCertificate: string | null

  @column({ serializeAs: null, columnName: 'ssl_private_key' })
  declare sslPrivateKey: string | null

  @column({ columnName: 'agency_id' })
  declare agencyId: string

  @column({ columnName: 'website_id' })
  declare websiteId: string | null

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => AgencyTenant, { foreignKey: 'agencyId' })
  declare agency: BelongsTo<typeof AgencyTenant>

  @belongsTo(() => Website, { foreignKey: 'websiteId' })
  declare website: BelongsTo<typeof Website>
}