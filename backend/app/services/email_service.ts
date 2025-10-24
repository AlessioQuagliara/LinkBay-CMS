/**
 * LinkBay CMS - Email Service
 * @author Alessio Quagliara
 * @description Servizio per l'invio di email
 */

export interface EmailData {
  to: string
  subject: string
  html?: string
  text?: string
  from?: string
}

export interface EmailResult {
  success: boolean
  messageId?: string
  error?: string
}

export default class EmailService {
  private smtpConfig = {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT || '587'),
    secure: false,
    auth: {
      user: process.env.SMTP_USER || '',
      pass: process.env.SMTP_PASS || ''
    }
  }

  /**
   * Send email
   */
  async sendEmail(emailData: EmailData): Promise<EmailResult> {
    try {
      // In produzione, usare un servizio email come SendGrid, Mailgun, ecc.
      // Per ora simuliamo l'invio

      console.log(`📧 Sending email to ${emailData.to}: ${emailData.subject}`)

      // Simula invio email
      const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

      // Log per debug
      console.log('Email data:', {
        to: emailData.to,
        subject: emailData.subject,
        hasHtml: !!emailData.html,
        hasText: !!emailData.text
      })

      return {
        success: true,
        messageId
      }
    } catch (error) {
      console.error('Email sending error:', error)
      return {
        success: false,
        error: (error as Error).message
      }
    }
  }

  /**
   * Send welcome email to new user
   */
  async sendWelcomeEmail(email: string, name: string): Promise<EmailResult> {
    const subject = 'Benvenuto su LinkBay CMS!'
    const html = `
      <h1>Benvenuto ${name}!</h1>
      <p>Grazie per esserti registrato su LinkBay CMS.</p>
      <p>Il tuo account è stato creato con successo.</p>
      <p>Puoi ora accedere alla piattaforma e iniziare a creare i tuoi siti web.</p>
      <br>
      <p>Cordiali saluti,<br>Il team LinkBay</p>
    `

    return this.sendEmail({
      to: email,
      subject,
      html,
      text: `Benvenuto ${name}! Grazie per esserti registrato su LinkBay CMS.`
    })
  }

  /**
   * Send password reset email
   */
  async sendPasswordResetEmail(email: string, resetToken: string): Promise<EmailResult> {
    const resetUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/reset-password?token=${resetToken}`

    const subject = 'Reset Password - LinkBay CMS'
    const html = `
      <h1>Reset Password</h1>
      <p>Hai richiesto il reset della password per il tuo account LinkBay CMS.</p>
      <p>Clicca sul link seguente per reimpostare la password:</p>
      <a href="${resetUrl}" style="background: #3B82F6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
      <p>Se non hai richiesto questo reset, ignora questa email.</p>
      <p>Il link scadrà tra 1 ora.</p>
      <br>
      <p>Cordiali saluti,<br>Il team LinkBay</p>
    `

    return this.sendEmail({
      to: email,
      subject,
      html,
      text: `Reset password: ${resetUrl}`
    })
  }

  /**
   * Send agency subscription confirmation
   */
  async sendSubscriptionConfirmation(email: string, agencyName: string, plan: string): Promise<EmailResult> {
    const subject = 'Abbonamento Attivato - LinkBay CMS'
    const html = `
      <h1>Abbonamento Attivato!</h1>
      <p>Congratulazioni! L'abbonamento per l'agenzia <strong>${agencyName}</strong> è stato attivato.</p>
      <p><strong>Piano:</strong> ${plan}</p>
      <p>Puoi ora iniziare a creare e gestire i tuoi siti web.</p>
      <br>
      <p>Cordiali saluti,<br>Il team LinkBay</p>
    `

    return this.sendEmail({
      to: email,
      subject,
      html,
      text: `Abbonamento attivato per ${agencyName} - Piano: ${plan}`
    })
  }

  /**
   * Send payment failed notification
   */
  async sendPaymentFailedNotification(email: string, agencyName: string, amount: number): Promise<EmailResult> {
    const subject = 'Pagamento Fallito - LinkBay CMS'
    const html = `
      <h1>Attenzione: Pagamento Fallito</h1>
      <p>Il pagamento di €${amount} per l'agenzia <strong>${agencyName}</strong> non è andato a buon fine.</p>
      <p>Ti preghiamo di verificare i dati della tua carta di credito e riprovare.</p>
      <p>Se il problema persiste, contatta il nostro supporto.</p>
      <br>
      <p>Cordiali saluti,<br>Il team LinkBay</p>
    `

    return this.sendEmail({
      to: email,
      subject,
      html,
      text: `Pagamento fallito per ${agencyName} - Importo: €${amount}`
    })
  }
}