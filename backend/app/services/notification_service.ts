/**
 * LinkBay CMS - Notification Service
 * @author Alessio Quagliara
 * @description Servizio per le notifiche in-app e push
 */

export interface NotificationData {
  userId: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  actionUrl?: string
  metadata?: Record<string, any>
}

export interface PushNotificationData {
  userId: string
  title: string
  body: string
  icon?: string
  badge?: string
  data?: Record<string, any>
}

export default class NotificationService {
  /**
   * Create in-app notification
   */
  async createNotification(notificationData: NotificationData): Promise<boolean> {
    try {
      // In produzione, salvare in tabella notifications
      // Per ora logghiamo solo

      console.log(`🔔 Creating notification for user ${notificationData.userId}: ${notificationData.title}`)

      // Simula salvataggio notifica
      const notification = {
        id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        userId: notificationData.userId,
        title: notificationData.title,
        message: notificationData.message,
        type: notificationData.type,
        actionUrl: notificationData.actionUrl,
        metadata: notificationData.metadata,
        read: false,
        createdAt: new Date()
      }

      console.log('Notification created:', notification)

      return true
    } catch (error) {
      console.error('Notification creation error:', error)
      return false
    }
  }

  /**
   * Send push notification
   */
  async sendPushNotification(pushData: PushNotificationData): Promise<boolean> {
    try {
      // In produzione, integrare con Firebase Cloud Messaging, OneSignal, ecc.
      console.log(`📱 Sending push notification to user ${pushData.userId}: ${pushData.title}`)

      // Simula invio push notification
      console.log('Push data:', {
        title: pushData.title,
        body: pushData.body,
        userId: pushData.userId
      })

      return true
    } catch (error) {
      console.error('Push notification error:', error)
      return false
    }
  }

  /**
   * Notify user registration
   */
  async notifyUserRegistered(userId: string, userEmail: string): Promise<void> {
    await this.createNotification({
      userId,
      title: 'Benvenuto su LinkBay CMS!',
      message: 'Il tuo account è stato creato con successo. Inizia a esplorare la piattaforma.',
      type: 'success',
      actionUrl: '/dashboard'
    })

    await this.sendPushNotification({
      userId,
      title: 'Benvenuto!',
      body: 'Il tuo account LinkBay CMS è pronto.',
      data: { type: 'welcome' }
    })
  }

  /**
   * Notify website published
   */
  async notifyWebsitePublished(userId: string, websiteName: string, websiteUrl: string): Promise<void> {
    await this.createNotification({
      userId,
      title: 'Sito Web Pubblicato!',
      message: `Il sito "${websiteName}" è stato pubblicato con successo.`,
      type: 'success',
      actionUrl: `/websites/${websiteUrl}`
    })

    await this.sendPushNotification({
      userId,
      title: 'Sito Pubblicato',
      body: `"${websiteName}" è ora online!`,
      data: { type: 'website_published', websiteUrl }
    })
  }

  /**
   * Notify payment success
   */
  async notifyPaymentSuccess(userId: string, amount: number, plan: string): Promise<void> {
    await this.createNotification({
      userId,
      title: 'Pagamento Completato',
      message: `Pagamento di €${amount} per il piano ${plan} elaborato con successo.`,
      type: 'success',
      actionUrl: '/billing'
    })

    await this.sendPushNotification({
      userId,
      title: 'Pagamento Riuscito',
      body: `€${amount} accreditati per ${plan}`,
      data: { type: 'payment_success', amount, plan }
    })
  }

  /**
   * Notify payment failed
   */
  async notifyPaymentFailed(userId: string, amount: number, reason: string): Promise<void> {
    await this.createNotification({
      userId,
      title: 'Pagamento Fallito',
      message: `Il pagamento di €${amount} non è andato a buon fine: ${reason}`,
      type: 'error',
      actionUrl: '/billing'
    })

    await this.sendPushNotification({
      userId,
      title: 'Pagamento Fallito',
      body: `Problema con il pagamento di €${amount}`,
      data: { type: 'payment_failed', amount, reason }
    })
  }

  /**
   * Notify subscription expiring
   */
  async notifySubscriptionExpiring(userId: string, daysLeft: number, plan: string): Promise<void> {
    const type = daysLeft <= 3 ? 'error' : daysLeft <= 7 ? 'warning' : 'info'
    const urgency = daysLeft <= 3 ? 'Urgente: ' : ''

    await this.createNotification({
      userId,
      title: `${urgency}Abbonamento in Scadenza`,
      message: `Il tuo abbonamento ${plan} scade tra ${daysLeft} giorni.`,
      type,
      actionUrl: '/billing'
    })

    await this.sendPushNotification({
      userId,
      title: 'Abbonamento in Scadenza',
      body: `${plan} scade tra ${daysLeft} giorni`,
      data: { type: 'subscription_expiring', daysLeft, plan }
    })
  }

  /**
   * Notify system maintenance
   */
  async notifySystemMaintenance(userId: string, startTime: Date, duration: string): Promise<void> {
    await this.createNotification({
      userId,
      title: 'Manutenzione Programmata',
      message: `Sarà effettuata manutenzione del sistema il ${startTime.toLocaleDateString()} per ${duration}.`,
      type: 'warning',
      metadata: { maintenance: true, startTime, duration }
    })
  }

  /**
   * Get user notifications
   */
  async getUserNotifications(userId: string, limit: number = 20): Promise<any[]> {
    try {
      // In produzione, query dal database
      // Per ora restituiamo array vuoto
      console.log(`📋 Getting notifications for user ${userId} (limit: ${limit})`)
      return []
    } catch (error) {
      console.error('Error fetching notifications:', error)
      return []
    }
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string, userId: string): Promise<boolean> {
    try {
      // In produzione, aggiornare nel database
      console.log(`✅ Marking notification ${notificationId} as read for user ${userId}`)
      return true
    } catch (error) {
      console.error('Error marking notification as read:', error)
      return false
    }
  }

  /**
   * Broadcast notification to all users
   */
  async broadcastToAllUsers(title: string, message: string, type: 'info' | 'warning' | 'error' = 'info'): Promise<void> {
    try {
      // In produzione, ottenere tutti gli utenti e creare notifiche
      console.log(`📢 Broadcasting to all users: ${title}`)

      // Simula broadcast
      console.log('Broadcast data:', { title, message, type })
    } catch (error) {
      console.error('Broadcast error:', error)
    }
  }
}