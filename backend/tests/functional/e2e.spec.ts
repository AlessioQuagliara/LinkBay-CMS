/**
 * LinkBay CMS - API E2E Tests
 * @author Alessio Quagliara
 */

import { test } from '@japa/runner'
import testUtils from '@adonisjs/core/services/test_utils'

test.group('API E2E', (group) => {
  group.each.setup(() => testUtils.db().withGlobalTransaction())

  test('full user workflow: register, login, get profile, update, logout', async ({ client, assert }) => {
    // 1. Register
    const registerResponse = await client.post('/api/v1/auth/register').json({
      email: 'workflow@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Workflow User'
    })

    registerResponse.assertStatus(201)
    const tokenData = registerResponse.body().token
    assert.exists(tokenData)
    const token = typeof tokenData === 'string' ? tokenData : tokenData.value

    // 2. Login
    const loginResponse = await client.post('/api/v1/auth/login').json({
      email: 'workflow@example.com',
      password: 'password123'
    })

    loginResponse.assertStatus(200)
    assert.exists(loginResponse.body().token)

    // 3. Get profile
    const profileResponse = await client
      .get('/api/v1/auth/profile')
      .bearerToken(token)

    profileResponse.assertStatus(200)
    profileResponse.assertBodyContains({
      email: 'workflow@example.com',
      name: 'Workflow User'
    })

    // 4. Logout
    const logoutResponse = await client
      .post('/api/v1/auth/logout')
      .bearerToken(token)

    logoutResponse.assertStatus(200)
  })

  test('agency management workflow', async ({ client, assert }) => {
    // Register admin user
    const registerResponse = await client.post('/api/v1/auth/register').json({
      email: 'admin@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Admin User'
    })

    const tokenData = registerResponse.body().token
    const token = typeof tokenData === 'string' ? tokenData : tokenData.value

    // Create agency
    const createAgencyResponse = await client
      .post('/api/v1/agencies')
      .bearerToken(token)
      .json({
        name: 'Test Agency',
        subscriptionTier: 'professional',
        maxWebsites: 10
      })

    createAgencyResponse.assertStatus(201)
    const agencyId = createAgencyResponse.body().agencyId
    assert.exists(agencyId)

    // Get agencies list
    const listResponse = await client
      .get('/api/v1/agencies')
      .bearerToken(token)

    listResponse.assertStatus(200)
    assert.isArray(listResponse.body().data)

    // Get specific agency
    const getResponse = await client
      .get(`/api/v1/agencies/${agencyId}`)
      .bearerToken(token)

    getResponse.assertStatus(200)
    getResponse.assertBodyContains({
      name: 'Test Agency',
      subscriptionTier: 'professional'
    })

    // Update agency
    const updateResponse = await client
      .put(`/api/v1/agencies/${agencyId}`)
      .bearerToken(token)
      .json({
        name: 'Updated Agency Name'
      })

    updateResponse.assertStatus(200)
    updateResponse.assertBodyContains({
      name: 'Updated Agency Name'
    })
  })

  test('website management workflow', async ({ client, assert }) => {
    // Register and create agency first
    const registerResponse = await client.post('/api/v1/auth/register').json({
      email: 'website@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Website User'
    })

    const tokenData = registerResponse.body().token
    const token = typeof tokenData === 'string' ? tokenData : tokenData.value

    const agencyResponse = await client
      .post('/api/v1/agencies')
      .bearerToken(token)
      .json({
        name: 'Website Agency',
        subscriptionTier: 'starter',
        maxWebsites: 3
      })

    const agencyId = agencyResponse.body().agencyId

    // Create website
    const createWebsiteResponse = await client
      .post('/api/v1/websites')
      .bearerToken(token)
      .json({
        name: 'Test Website',
        domain: 'test.example.com',
        tenantId: agencyId,
        status: 'draft'
      })

    createWebsiteResponse.assertStatus(201)
    const websiteId = createWebsiteResponse.body().websiteId
    assert.exists(websiteId)

    // Get websites list
    const listResponse = await client
      .get('/api/v1/websites')
      .bearerToken(token)

    listResponse.assertStatus(200)
    assert.isArray(listResponse.body().data)

    // Update website
    const updateResponse = await client
      .put(`/api/v1/websites/${websiteId}`)
      .bearerToken(token)
      .json({
        status: 'published'
      })

    updateResponse.assertStatus(200)
    updateResponse.assertBodyContains({
      status: 'published'
    })
  })
})