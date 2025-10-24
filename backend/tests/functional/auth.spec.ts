/**
 * LinkBay CMS - Auth Controller Tests
 * @author Alessio Quagliara
 */

import { test } from '@japa/runner'
import testUtils from '@adonisjs/core/services/test_utils'

test.group('Auth Controller', (group) => {
  group.each.setup(() => testUtils.db().withGlobalTransaction())

  test('can register a new user', async ({ client, assert }) => {
    const response = await client.post('/api/v1/auth/register').json({
      email: 'newuser@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'New User'
    })

    response.assertStatus(201)
    response.assertBodyContains({
      user: {
        email: 'newuser@example.com',
        name: 'New User'
      }
    })
    assert.exists(response.body().token)
  })

  test('cannot register with existing email', async ({ client }) => {
    // First registration
    await client.post('/api/v1/auth/register').json({
      email: 'existing@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Existing User'
    })

    // Second registration with same email
    const response = await client.post('/api/v1/auth/register').json({
      email: 'existing@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Another User'
    })

    response.assertStatus(409)
  })

  test('can login with valid credentials', async ({ client, assert }) => {
    // Register user first
    await client.post('/api/v1/auth/register').json({
      email: 'login@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Login User'
    })

    // Login
    const response = await client.post('/api/v1/auth/login').json({
      email: 'login@example.com',
      password: 'password123'
    })

    response.assertStatus(200)
    assert.exists(response.body().token)
    response.assertBodyContains({
      user: {
        email: 'login@example.com'
      }
    })
  })

  test('cannot login with invalid credentials', async ({ client }) => {
    const response = await client.post('/api/v1/auth/login').json({
      email: 'nonexistent@example.com',
      password: 'wrongpassword'
    })

    response.assertStatus(400)
  })

  test('can get user profile when authenticated', async ({ client, assert }) => {
    // Register and get token
    const registerResponse = await client.post('/api/v1/auth/register').json({
      email: 'profile@example.com',
      password: 'password123',
      password_confirmation: 'password123',
      name: 'Profile User'
    })

    const tokenData = registerResponse.body().token
    assert.exists(tokenData)
    
    // Extract the token value
    const token = typeof tokenData === 'string' ? tokenData : tokenData.value

    // Get profile
    const response = await client
      .get('/api/v1/auth/profile')
      .bearerToken(token)

    response.assertStatus(200)
    response.assertBodyContains({
      email: 'profile@example.com',
      name: 'Profile User'
    })
  })

  test('cannot get profile without authentication', async ({ client }) => {
    const response = await client.get('/api/v1/auth/profile')

    response.assertStatus(401)
  })
})