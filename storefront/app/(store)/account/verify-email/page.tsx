import type { Metadata } from 'next'
import Link from 'next/link'
import { MailCheck } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Verifica email',
  robots: { index: false },
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm text-center">
        <MailCheck className="w-16 h-16 text-gray-900 mx-auto mb-4" />
        <h1 className="text-xl font-bold text-gray-900 mb-2">Verifica la tua email</h1>
        <p className="text-sm text-gray-600 mb-6">
          Ti abbiamo inviato un'email di verifica. Clicca il link nell'email per attivare il tuo
          account.
        </p>
        <p className="text-sm text-gray-500">
          Non hai ricevuto l'email?{' '}
          <Link href="/account/login" className="font-medium text-gray-900 hover:underline">
            Prova ad accedere
          </Link>{' '}
          e segui le istruzioni.
        </p>
      </div>
    </div>
  )
}
