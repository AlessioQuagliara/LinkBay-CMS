import { createRequire } from 'module'
const require = createRequire(import.meta.url)

async function createAssociation() {
  const { default: User } = await import('#models/user')
  const { default: AgencyTenant } = await import('#models/agency_tenant')
  const { default: UserManager } = await import('#models/user_manager')

  try {
    const user = await User.findBy('email', 'agenzia@demo.com')
    const agency = await AgencyTenant.findBy('name', 'demo')

    if (user && agency) {
      const existing = await UserManager.query()
        .where('userId', user.id)
        .where('agencyId', agency.agencyId)
        .first()

      if (!existing) {
        await UserManager.create({
          userId: user.id,
          agencyId: agency.agencyId,
          role: 'owner',
        })
        console.log('Association created successfully')
      } else {
        console.log('Association already exists')
      }
    } else {
      console.log('User or agency not found')
    }
  } catch (error) {
    console.error('Error:', error)
  }

  process.exit(0)
}

createAssociation()