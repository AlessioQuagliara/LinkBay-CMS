/**
 * LinkBay CMS - Website Published Event
 * @author Alessio Quagliara
 * @description Evento triggered quando un sito web viene pubblicato
 */

export default class WebsitePublished {
  constructor(public website: any, public user: any, public agency: any) {}

  toJSON() {
    return {
      websiteId: this.website.websiteId,
      name: this.website.name,
      url: this.website.url,
      userId: this.user.userId,
      agencyId: this.agency.agencyId,
      publishedAt: new Date()
    }
  }
}