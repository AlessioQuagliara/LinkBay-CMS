/**
 * LinkBay CMS - User Model Tests
 * @author Alessio Quagliara
 */

import { test } from '@japa/runner'
import User from '#models/user'
import testUtils from '@adonisjs/core/services/test_utils'

test.group('User Model', (group) => {
  group.each.setup(() => testUtils.db().withGlobalTransaction())

  test('can create a user', async ({ assert }) => {
    const user = await User.create({
      email: 'test@example.com',
      password: 'password123',
      name: 'Test User',
      role: 'agency',
      isActive: true
    })

    assert.exists(user.id)
    assert.equal(user.email, 'test@example.com')
    assert.equal(user.name, 'Test User')
    assert.equal(user.role, 'agency')
    assert.isTrue(user.isActive)
  })

  test('can find user by email', async ({ assert }) => {
    await User.create({
      email: 'find@example.com',
      password: 'password123',
      name: 'Find User',
      role: 'agency',
      isActive: true
    })

    const user = await User.findBy('email', 'find@example.com')

    assert.exists(user)
    assert.equal(user?.email, 'find@example.com')
  })

  test('password is hashed on save', async ({ assert }) => {
    const plainPassword = 'password123'

    const user = await User.create({
      email: 'hash@example.com',
      password: plainPassword,
      name: 'Hash User',
      role: 'agency',
      isActive: true
    })

    assert.notEqual(user.password, plainPassword)
    assert.isTrue(user.password.length > 20)
  })

  test('can update user', async ({ assert }) => {
    const user = await User.create({
      email: 'update@example.com',
      password: 'password123',
      name: 'Update User',
      role: 'agency',
      isActive: true
    })

    user.name = 'Updated Name'
    await user.save()

    const updatedUser = await User.find(user.id)
    assert.equal(updatedUser?.name, 'Updated Name')
  })

  test('can delete user', async ({ assert }) => {
    const user = await User.create({
      email: 'delete@example.com',
      password: 'password123',
      name: 'Delete User',
      role: 'agency',
      isActive: true
    })

    await user.delete()

    const deletedUser = await User.find(user.id)
    assert.isNull(deletedUser)
  })

  test('validates unique email', async ({ assert }) => {
    await User.create({
      email: 'unique@example.com',
      password: 'password123',
      name: 'Unique User',
      role: 'agency',
      isActive: true
    })

    // Trying to create another user with same email should fail
    assert.rejects(async () => {
      await User.create({
        email: 'unique@example.com',
        password: 'password123',
        name: 'Duplicate User',
        role: 'agency',
        isActive: true
      })
    })
  })
})