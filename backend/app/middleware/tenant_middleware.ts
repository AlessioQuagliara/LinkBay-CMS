/**
 * LinkBay CMS - Tenant Middleware
 * @author Alessio Quagliara
 * @description Middleware per isolamento multi-tenant
 */

import type { HttpContext } from '@adonisjs/core/http'
import type { NextFn } from '@adonisjs/core/types/http'
import AgencyTenant from '#models/agency_tenant'

export default class TenantMiddleware {
  /**
   * Handle tenant isolation
   */
  async handle(ctx: HttpContext, next: NextFn) {
    const { request, response, auth } = ctx

    try {
      // Ottieni l'utente autenticato
      const user = auth.user
      if (!user) {
        return response.unauthorized({ message: 'Authentication required' })
      }

      // Per admin, permetti accesso a tutto
      if (user.role === 'admin') {
        return next()
      }

      // Per utenti agency, determina il tenant dall'URL o dal contesto
      const tenantId = this.extractTenantId(ctx)

      if (!tenantId) {
        return response.badRequest({ message: 'Tenant ID required' })
      }

      // Verifica che l'utente appartenga al tenant
      const agency = await AgencyTenant.query()
        .where('agency_id', tenantId)
        .preload('workspace')
        .first()

      if (!agency) {
        return response.notFound({ message: 'Agency not found' })
      }

      // Verifica che l'utente sia associato all'agenzia
      // TODO: Implementare controllo associazione utente-agenzia
      const isUserAssociated = await this.checkUserAgencyAssociation(user.id, tenantId)

      if (!isUserAssociated) {
        return response.forbidden({ message: 'Access denied to this agency' })
      }

      // Aggiungi informazioni del tenant al contesto della richiesta
      (ctx as any).tenant = {
        id: agency.agencyId,
        name: agency.name,
        workspaceId: agency.workspaceId,
        subscriptionTier: agency.subscriptionTier,
        maxWebsites: agency.maxWebsites,
        whiteLabelConfig: agency.whiteLabelConfig
      }

      // Continua con la richiesta
      return next()

    } catch (error) {
      console.error('Tenant middleware error:', error)
      return response.internalServerError({ message: 'Internal server error' })
    }
  }

  /**
   * Extract tenant ID from request
   */
  private extractTenantId(ctx: HttpContext): string | null {
    const { request, params } = ctx

    // Prima controlla i parametri della route
    if (params.tenantId || params.agencyId) {
      return params.tenantId || params.agencyId
    }

    // Poi controlla gli header
    const tenantHeader = request.header('X-Tenant-ID') || request.header('X-Agency-ID')
    if (tenantHeader) {
      return tenantHeader
    }

    // Infine controlla il subdomain (per white-label)
    const host = request.header('host')
    if (host && host.includes('.')) {
      const subdomain = host.split('.')[0]
      if (subdomain !== 'www' && subdomain !== 'app') {
        // Cerca l'agenzia per dominio white-label
        // TODO: Implementare cache per performance
        return null // Per ora restituisci null
      }
    }

    return null
  }

  /**
   * Check if user is associated with agency
   */
  private async checkUserAgencyAssociation(userId: number, agencyId: string): Promise<boolean> {
    try {
      // TODO: Implementare controllo associazione
      // Per ora, permetti tutto (da implementare con tabella user_tenants)
      return true
    } catch (error) {
      console.error('Error checking user-agency association:', error)
      return false
    }
  }
}