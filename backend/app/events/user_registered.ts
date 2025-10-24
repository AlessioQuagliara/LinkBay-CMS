/**
 * LinkBay CMS - User Registered Event
 * @author Alessio Quagliara
 * @description Evento triggered quando un utente si registra
 */

export default class UserRegistered {
  constructor(public user: any) {}

  toJSON() {
    return {
      userId: this.user.userId,
      email: this.user.email,
      name: this.user.name,
      role: this.user.role,
      registeredAt: this.user.createdAt
    }
  }
}