import type { Metadata } from 'next'
import { accountApi } from '@/lib/api/client'
import { OrderConfirmation } from '@/components/checkout/OrderConfirmation'

export const metadata: Metadata = {
  title: 'Ordine confermato',
  robots: { index: false },
}

interface Props {
  params: Promise<{ orderId: string }>
}

export default async function OrderConfirmationPage({ params }: Props) {
  const { orderId } = await params

  try {
    const res = await accountApi.getOrder(Number(orderId))
    return <OrderConfirmation order={res.data} />
  } catch {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Ordine confermato</h1>
          <p className="text-gray-600">
            Il tuo ordine è stato ricevuto. Riceverai una email di conferma a breve.
          </p>
        </div>
      </div>
    )
  }
}
