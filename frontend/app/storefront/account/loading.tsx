export default function AccountLoading() {
  return (
    <div
      role="status"
      aria-label="Caricamento account"
      className="mx-auto max-w-2xl px-4 py-12 sm:px-6"
    >
      {/* Heading / greeting */}
      <div className="mb-8 space-y-2">
        <div className="h-8 w-56 animate-pulse rounded-lg bg-gray-100" />
        <div className="h-4 w-40 animate-pulse rounded bg-gray-100" />
      </div>

      {/* Card list — approximates nav tiles, order list, or profile sections */}
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="flex items-center gap-4 rounded-2xl border border-gray-200 bg-white p-4"
          >
            <div className="h-10 w-10 shrink-0 animate-pulse rounded-xl bg-gray-100" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-1/2 animate-pulse rounded bg-gray-100" />
              <div className="h-3 w-1/3 animate-pulse rounded bg-gray-100" />
            </div>
            <div className="h-4 w-4 shrink-0 animate-pulse rounded bg-gray-100" />
          </div>
        ))}
      </div>

      <div className="mt-8 h-11 w-full animate-pulse rounded-xl bg-gray-100" />
    </div>
  )
}
