/**
 * LinkBay CMS - Agencies Controller
 * @author Alessio Quagliara
 * @description Gestione agenzie tenant
 */

import type { HttpContext } from '@adonisjs/core/http'
import AgencyTenant from '#models/agency_tenant'

export default class AgenciesController {
  /**
   * Lista tutte le agenzie
   */
  async index({ request, response }: HttpContext) {
    const page = request.input('page', 1)
    const limit = request.input('limit', 20)

    const agencies = await AgencyTenant.query()
      .preload('workspace')
      .paginate(page, limit)

    return response.ok(agencies)
  }

  /**
   * Mostra singola agenzia
   */
  async show({ params, response }: HttpContext) {
    const agency = await AgencyTenant.findOrFail(params.id)
    await agency.load('workspace')

    return response.ok(agency)
  }

  /**
   * Crea nuova agenzia
   */
  async store({ request, response }: HttpContext) {
    const payload = request.only([
      'name',
      'status',
      'whiteLabelConfig',
      'subscriptionTier',
      'maxWebsites',
    ])

    const agency = await AgencyTenant.create(payload)
    await agency.load('workspace')

    return response.created(agency)
  }

  /**
   * Aggiorna agenzia
   */
  async update({ params, request, response }: HttpContext) {
    const agency = await AgencyTenant.findOrFail(params.id)
    const payload = request.only([
      'name',
      'status',
      'whiteLabelConfig',
      'subscriptionTier',
      'maxWebsites',
    ])

    agency.merge(payload)
    await agency.save()
    await agency.load('workspace')

    return response.ok(agency)
  }

  /**
   * Elimina agenzia
   */
  async destroy({ params, response }: HttpContext) {
    const agency = await AgencyTenant.findOrFail(params.id)
    await agency.delete()

    return response.noContent()
  }
}