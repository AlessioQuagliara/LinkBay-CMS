/**
 * LinkBay CMS - TenantsConfig Model
 * @author Alessio Quagliara
 * @description Configurazione per tenant end-user
 */

import { DateTime } from 'luxon'
import { BaseModel, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import UserTenant from '#models/user_tenant'
import BillingInfo from '#models/billing_info'

export default class TenantsConfig extends BaseModel {
  static table = 'tenants_config'

  @column({ isPrimary: true, columnName: 'tenant_config_id' })
  declare tenantConfigId: string

  @column({ columnName: 'tenant_user_id' })
  declare tenantUserId: string

  @column({ columnName: 'billing_info_id' })
  declare billingInfoId: string | null

  @column({ columnName: 'max_products' })
  declare maxProducts: number

  @column({ columnName: 'max_users' })
  declare maxUsers: number

  @column({
    prepare: (value: any) => JSON.stringify(value),
    consume: (value: string) => JSON.parse(value),
    columnName: 'features_allowed'
  })
  declare featuresAllowed: Record<string, any> | null

  @column({ columnName: 'api_rate_limit' })
  declare apiRateLimit: number

  @column({ columnName: 'storage_limit_mb' })
  declare storageLimitMb: number

  @column.dateTime({ autoCreate: true, columnName: 'created_at' })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true, columnName: 'updated_at' })
  declare updatedAt: DateTime

  @belongsTo(() => UserTenant, { foreignKey: 'tenantUserId' })
  declare tenantUser: BelongsTo<typeof UserTenant>

  @belongsTo(() => BillingInfo, { foreignKey: 'billingInfoId' })
  declare billingInfo: BelongsTo<typeof BillingInfo>
}