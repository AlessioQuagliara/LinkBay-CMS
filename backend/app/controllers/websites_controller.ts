/**
 * LinkBay CMS - Websites Controller
 * @author Alessio Quagliara
 * @description Gestione siti web
 */

import type { HttpContext } from '@adonisjs/core/http'
import Website from '#models/website'

export default class WebsitesController {
  /**
   * Lista tutti i siti web
   */
  async index({ request, response }: HttpContext) {
    const page = request.input('page', 1)
    const limit = request.input('limit', 20)

    const websites = await Website.query()
      .preload('agency')
      .preload('workspace')
      .preload('config')
      .paginate(page, limit)

    return response.ok(websites)
  }

  /**
   * Mostra singolo sito web
   */
  async show({ params, response }: HttpContext) {
    const website = await Website.findOrFail(params.id)
    await website.load('agency')
    await website.load('workspace')
    await website.load('config')

    return response.ok(website)
  }

  /**
   * Crea nuovo sito web
   */
  async store({ request, response }: HttpContext) {
    const payload = request.only([
      'tenantId',
      'workspaceId',
      'websiteConfigId',
      'name',
      'description',
      'industry',
      'currency',
      'language',
      'timezone',
      'subscriptionUserId',
    ])

    const website = await Website.create(payload)
    await website.load('agency')
    await website.load('workspace')
    await website.load('config')

    return response.created(website)
  }

  /**
   * Aggiorna sito web
   */
  async update({ params, request, response }: HttpContext) {
    const website = await Website.findOrFail(params.id)
    const payload = request.only([
      'tenantId',
      'workspaceId',
      'websiteConfigId',
      'name',
      'description',
      'industry',
      'currency',
      'language',
      'timezone',
      'subscriptionUserId',
    ])

    website.merge(payload)
    await website.save()
    await website.load('agency')
    await website.load('workspace')
    await website.load('config')

    return response.ok(website)
  }

  /**
   * Elimina sito web
   */
  async destroy({ params, response }: HttpContext) {
    const website = await Website.findOrFail(params.id)
    await website.delete()

    return response.noContent()
  }
}