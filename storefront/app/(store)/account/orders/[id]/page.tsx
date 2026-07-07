import type { Metadata } from 'next'
import { AccountLayout } from '@/components/account/AccountLayout'
import { OrderDetail } from '@/components/account/OrderDetail'
import { accountApi } from '@/lib/api/client'

export const metadata: Metadata = {
  title: 'Dettaglio ordine',
  robots: { index: false },
}

interface Props {
  params: Promise<{ id: string }>
}

export default async function OrderDetailPage({ params }: Props) {
  const { id } = await params

  try {
    const res = await accountApi.getOrder(Number(id))
    return (
      <AccountLayout title="Dettaglio ordine">
        <OrderDetail order={res.data} />
      </AccountLayout>
    )
  } catch {
    return (
      <AccountLayout title="Ordine non trovato">
        <p className="text-sm text-gray-500">
          Ordine non trovato o non hai i permessi per visualizzarlo.
        </p>
      </AccountLayout>
    )
  }
}
