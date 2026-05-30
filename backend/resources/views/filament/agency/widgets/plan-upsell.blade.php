<x-filament::section class="border-amber-400 bg-amber-50 dark:bg-amber-900/20">
    <div class="flex items-start gap-4">
        <x-heroicon-o-exclamation-triangle class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div class="flex-1">
            <p class="text-lg font-semibold text-amber-800 dark:text-amber-300">Nessun piano attivo</p>
            <p class="text-sm text-amber-700 dark:text-amber-400 mt-1">
                Attiva un piano per sbloccare tutte le funzionalità: white-label, domini personalizzati, crediti AI mensili e altro.
            </p>

            @php $plans = $this->getPlans(); @endphp

            @if($plans->isNotEmpty())
                <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    @foreach($plans as $plan)
                        <div class="border border-amber-300 dark:border-amber-700 rounded-xl p-4 bg-white dark:bg-amber-900/30 text-center">
                            <p class="font-bold text-base">{{ $plan->name }}</p>
                            <p class="text-2xl font-black text-amber-600 dark:text-amber-400 my-1">
                                €{{ number_format((float) $plan->price, 0, ',', '.') }}
                            </p>
                            <p class="text-xs text-gray-500">/ {{ $plan->billing_interval === 'year' ? 'anno' : 'mese' }}</p>
                        </div>
                    @endforeach
                </div>
            @endif

            <div class="mt-4 flex flex-wrap gap-3">
                <a href="{{ route('filament.agency.pages.agency-billing') }}">
                    <x-filament::button color="warning">Vedi piani e abbonati</x-filament::button>
                </a>
                <a href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}">
                    <x-filament::button color="gray">Contatta supporto</x-filament::button>
                </a>
            </div>
        </div>
    </div>
</x-filament::section>
