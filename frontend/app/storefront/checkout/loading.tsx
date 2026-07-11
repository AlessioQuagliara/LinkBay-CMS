function Pulse({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-gray-100 ${className}`} />
}

export default function CheckoutLoading() {
  return (
    <div
      role="status"
      aria-label="Caricamento checkout"
      className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8"
    >
      <div className="mb-8 h-8 w-40 animate-pulse rounded-lg bg-gray-100" />

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Left — steps + form skeleton */}
        <div className="lg:col-span-3">
          {/* Step indicator */}
          <div className="mb-8 flex items-center gap-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="h-7 w-7 animate-pulse rounded-full bg-gray-100" />
                <div className="h-3 w-16 animate-pulse rounded bg-gray-100" />
                {i < 2 && <div className="mx-1 h-3 w-3 shrink-0" />}
              </div>
            ))}
          </div>

          <div className="mb-4 h-5 w-48 animate-pulse rounded bg-gray-100" />

          {/* Address form fields */}
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Pulse className="h-12" />
              <Pulse className="h-12" />
            </div>
            <Pulse className="h-12" />
            <Pulse className="h-12" />
            <div className="grid gap-4 sm:grid-cols-3">
              <Pulse className="h-12 sm:col-span-2" />
              <Pulse className="h-12" />
            </div>
            <Pulse className="h-12" />
            <Pulse className="mt-2 h-[52px]" />
          </div>
        </div>

        {/* Right — order summary skeleton */}
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
            <div className="mb-4 h-4 w-32 animate-pulse rounded bg-gray-200" />
            <ul className="mb-4 space-y-3">
              {[0, 1, 2].map((i) => (
                <li key={i} className="flex items-center gap-3">
                  <div className="h-10 w-10 shrink-0 animate-pulse rounded-lg bg-gray-200" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-3.5 w-3/4 animate-pulse rounded bg-gray-200" />
                    <div className="h-3 w-1/3 animate-pulse rounded bg-gray-200" />
                  </div>
                </li>
              ))}
            </ul>
            <div className="space-y-2 border-t border-gray-200 pt-4">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="flex justify-between">
                  <div className="h-3.5 w-20 animate-pulse rounded bg-gray-200" />
                  <div className="h-3.5 w-14 animate-pulse rounded bg-gray-200" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
