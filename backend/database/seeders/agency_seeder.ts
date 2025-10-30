import { BaseSeeder } from '@adonisjs/lucid/seeders'
import AgencyTenant from '#models/agency_tenant'
import Workspace from '#models/workspace'

export default class extends BaseSeeder {
  async run() {
    // Crea agenzia default
    const defaultAgency = await AgencyTenant.create({
      name: 'default', // Nome che corrisponde al subdomain
      status: 'active',
      whiteLabelConfig: {
        primaryColor: '#343a4D',
        logoUrl: 'https://example.com/logo.png',
        companyName: 'LinkBay CMS',
        customDomain: 'linkbay-cms.com',
      },
      subscriptionTier: 'professional',
      maxWebsites: 10,
    })

    await Workspace.create({
      agencyId: defaultAgency.agencyId,
      slug: 'default-workspace',
      name: 'Default Workspace',
      config: {
        timezone: 'Europe/Rome',
        language: 'it',
        currency: 'EUR',
      },
    })

    // Crea agenzia demo
    const agency = await AgencyTenant.create({
      name: 'demo', // Nome che corrisponde al subdomain
      status: 'active',
      whiteLabelConfig: {
        primaryColor: '#3B82F6',
        logoUrl: 'https://example.com/logo.png',
        companyName: 'Agenzia Demo',
        customDomain: 'demo.linkbay.com',
      },
      subscriptionTier: 'professional',
      maxWebsites: 10,
    })

    // Crea workspace per l'agenzia
    await Workspace.create({
      agencyId: agency.agencyId,
      slug: 'demo-workspace',
      name: 'Workspace Demo',
      config: {
        timezone: 'Europe/Rome',
        language: 'it',
        currency: 'EUR',
      },
    })

    // Crea altre agenzie demo
    const agency2 = await AgencyTenant.create({
      name: 'websolutions', // Nome che corrisponde al subdomain
      status: 'active',
      whiteLabelConfig: {
        primaryColor: '#10B981',
        logoUrl: 'https://example.com/logo2.png',
        companyName: 'Web Solutions Italia',
      },
      subscriptionTier: 'starter',
      maxWebsites: 3,
    })

    await Workspace.create({
      agencyId: agency2.agencyId,
      slug: 'web-solutions',
      name: 'Web Solutions Workspace',
      config: {
        timezone: 'Europe/Rome',
        language: 'it',
        currency: 'EUR',
      },
    })
  }
}