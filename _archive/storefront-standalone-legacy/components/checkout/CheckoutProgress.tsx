'use client'

import { Check } from 'lucide-react'
import Link from 'next/link'

const STEPS = [
  { label: 'Indirizzo', href: '/checkout' },
  { label: 'Spedizione', href: '/checkout/shipping' },
  { label: 'Pagamento', href: '/checkout/payment' },
]

interface Props {
  currentStep: 0 | 1 | 2
}

export function CheckoutProgress({ currentStep }: Props) {
  return (
    <nav aria-label="Avanzamento checkout" className="mb-8">
      <ol className="flex items-center gap-0">
        {STEPS.map((step, index) => {
          const done = index < currentStep
          const active = index === currentStep

          return (
            <li key={step.href} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                {done ? (
                  <Link
                    href={step.href}
                    className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center"
                  >
                    <Check className="w-4 h-4 text-white" />
                  </Link>
                ) : (
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-sm font-medium ${
                      active
                        ? 'border-gray-900 bg-gray-900 text-white'
                        : 'border-gray-300 text-gray-400'
                    }`}
                  >
                    {index + 1}
                  </div>
                )}
                <span
                  className={`mt-1 text-xs font-medium ${
                    active ? 'text-gray-900' : done ? 'text-gray-600' : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 mb-4 ${
                    done ? 'bg-gray-900' : 'bg-gray-200'
                  }`}
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
