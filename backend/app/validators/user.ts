/**
 * LinkBay CMS - User Validators
 * @author Alessio Quagliara
 * @description Validatori per gestione utenti
 */

import vine from '@vinejs/vine'

export const createUserValidator = vine.compile(
  vine.object({
    name: vine.string().minLength(2).maxLength(100),
    email: vine.string().email().normalizeEmail(),
    password: vine.string().minLength(8),
    role: vine.enum(['agency', 'admin', 'superadmin']).optional(),
    isActive: vine.boolean().optional(),
  })
)

export const updateUserValidator = vine.compile(
  vine.object({
    name: vine.string().minLength(2).maxLength(100).optional(),
    email: vine.string().email().normalizeEmail().optional(),
    role: vine.enum(['agency', 'admin', 'superadmin']).optional(),
    isActive: vine.boolean().optional(),
  })
)