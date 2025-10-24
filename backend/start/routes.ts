/*
|--------------------------------------------------------------------------
| Routes file
|--------------------------------------------------------------------------
|
| The routes file is used for defining the HTTP routes.
|
*/

import router from '@adonisjs/core/services/router'
import { middleware } from '#start/kernel'

// Import controllers
import AuthController from '#controllers/auth_controller'
import UsersController from '#controllers/users_controller'
import AgenciesController from '#controllers/agencies_controller'
import WebsitesController from '#controllers/websites_controller'

// Health check
router.get('/', async () => {
  return {
    name: 'LinkBay CMS API',
    version: '1.0.0',
    status: 'running',
  }
})

// API Routes (v1)
router.group(() => {
  // ===== AUTHENTICATION =====
  router.post('/auth/register', [AuthController, 'register'])
  router.post('/auth/login', [AuthController, 'login'])

  // Protected routes (require authentication)
  router.group(() => {
    // Auth
    router.post('/auth/logout', [AuthController, 'logout'])
    router.get('/auth/profile', [AuthController, 'profile'])
    router.post('/auth/refresh', [AuthController, 'refresh'])

    // Users management
    router.group(() => {
      router.resource('/users', UsersController)
      router.patch('/users/:id/toggle-active', [UsersController, 'toggleActive'])
    }).use(middleware.tenant())

    // Agencies management
    router.group(() => {
      router.resource('/agencies', AgenciesController)
    }).use(middleware.tenant())

    // Websites management
    router.group(() => {
      router.resource('/websites', WebsitesController)
    }).use(middleware.tenant())

  }).use(middleware.auth())

}).prefix('/api/v1')
