'use client'

import { useState } from 'react'
import { MapPin, Pencil, Trash2, Star, Loader2 } from 'lucide-react'
import type { Address } from '@/types'

interface Props {
  address: Address
  onEdit: (address: Address) => void
  onDelete: (id: number) => Promise<void>
  onSetDefault: (id: number) => Promise<void>
}

export function AddressCard({ address, onEdit, onDelete, onSetDefault }: Props) {
  const [deleting, setDeleting] = useState(false)
  const [settingDefault, setSettingDefault] = useState(false)

  const handleDelete = async () => {
    if (!confirm('Eliminare questo indirizzo?')) return
    setDeleting(true)
    try {
      await onDelete(address.id)
    } finally {
      setDeleting(false)
    }
  }

  const handleSetDefault = async () => {
    setSettingDefault(true)
    try {
      await onSetDefault(address.id)
    } finally {
      setSettingDefault(false)
    }
  }

  return (
    <div
      className={`rounded-xl border-2 p-5 transition-colors ${
        address.is_default ? 'border-gray-900' : 'border-gray-200'
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-gray-500 flex-shrink-0" />
          <span className="text-sm font-medium text-gray-900">
            {address.label ?? 'Indirizzo'}
          </span>
          {address.is_default && (
            <span className="px-2 py-0.5 bg-gray-900 text-white text-xs rounded-full">
              Principale
            </span>
          )}
        </div>
      </div>

      <address className="not-italic text-sm text-gray-600 leading-relaxed mb-4">
        {address.first_name} {address.last_name}<br />
        {address.company && <>{address.company}<br /></>}
        {address.address_line1}<br />
        {address.address_line2 && <>{address.address_line2}<br /></>}
        {address.postal_code} {address.city}
        {address.state && `, ${address.state}`}<br />
        {address.country}
        {address.phone && <><br />{address.phone}</>}
      </address>

      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => onEdit(address)}
          className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-gray-900 transition-colors px-2 py-1 rounded hover:bg-gray-100"
        >
          <Pencil className="w-3.5 h-3.5" />
          Modifica
        </button>

        {!address.is_default && (
          <button
            onClick={handleSetDefault}
            disabled={settingDefault}
            className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-gray-900 transition-colors px-2 py-1 rounded hover:bg-gray-100 disabled:opacity-50"
          >
            {settingDefault
              ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
              : <Star className="w-3.5 h-3.5" />
            }
            Imposta principale
          </button>
        )}

        <button
          onClick={handleDelete}
          disabled={deleting || address.is_default}
          className="flex items-center gap-1.5 text-xs text-red-600 hover:text-red-800 transition-colors px-2 py-1 rounded hover:bg-red-50 disabled:opacity-30"
          title={address.is_default ? 'Non puoi eliminare l\'indirizzo principale' : ''}
        >
          {deleting
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Trash2 className="w-3.5 h-3.5" />
          }
          Elimina
        </button>
      </div>
    </div>
  )
}
