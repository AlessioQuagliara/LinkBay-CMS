/**
 * LinkBay CMS - Agency Created Event
 * @author Alessio Quagliara
 * @description Evento triggered quando viene creata una nuova agenzia
 */

export default class AgencyCreated {
  constructor(public agency: any, public owner: any) {}

  toJSON() {
    return {
      agencyId: this.agency.agencyId,
      name: this.agency.name,
      ownerId: this.owner.userId,
      ownerEmail: this.owner.email,
      subscriptionTier: this.agency.subscriptionTier,
      createdAt: this.agency.createdAt
    }
  }
}