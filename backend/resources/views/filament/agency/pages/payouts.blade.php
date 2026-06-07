<x-filament-panels::page>
    @php
        $stats           = $this->summaryStats();
        $payouts         = $this->payouts();
        $hasConnect      = $this->hasConnectAccount();
        $isOnboarded     = $this->isConnectOnboarded();
        $stripeOk        = $this->isStripeConfigured();

        $statusOptions = [
            ''           => 'Tutti gli stati',
            'pending'    => 'In attesa',
            'in_transit' => 'In transito',
            'paid'       => 'Pagato',
            'failed'     => 'Fallito',
            'cancelled'  => 'Annullato',
        ];

        $statusColors = [
            'pending'    => 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-900/50',
            'in_transit' => 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900/50',
            'paid'       => 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50',
            'failed'     => 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-900/50',
            'cancelled'  => 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
        ];
    @endphp

    {{-- ── CONNECT STATUS BANNER ─────────────────────────────────────────── --}}
    @if(! $hasConnect)
        <div class="flex items-start gap-3 p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 mb-2">
            <x-heroicon-o-exclamation-triangle class="h-5 w-5 text-yellow-600 shrink-0 mt-0.5"/>
            <div class="text-sm text-yellow-800 dark:text-yellow-300">
                Stripe Connect non è stato configurato per questa agency.
                Vai su <strong>Impostazioni</strong> per completare l'onboarding e abilitare i payout.
            </div>
        </div>
    @elseif(! $isOnboarded)
        <div class="flex items-start gap-3 p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 mb-2">
            <x-heroicon-o-information-circle class="h-5 w-5 text-blue-600 shrink-0 mt-0.5"/>
            <div class="text-sm text-blue-800 dark:text-blue-300">
                L'onboarding Stripe Connect è in corso. I payout diventeranno disponibili al completamento della verifica.
            </div>
        </div>
    @endif

    {{-- ── KPI CARDS ──────────────────────────────────────────────────────── --}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
        <div class="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-900/50">
            <p class="text-xs font-medium text-green-600 dark:text-green-400 uppercase tracking-wide mb-1">Totale pagato</p>
            <p class="text-2xl font-bold text-green-900 dark:text-green-200">
                {{ number_format($stats['paid_cents'] / 100, 2, ',', '.') }} €
            </p>
        </div>
        <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/50">
            <p class="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide mb-1">In transito</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-200">
                {{ number_format($stats['in_transit_cents'] / 100, 2, ',', '.') }} €
            </p>
        </div>
        <div class="p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-900/50">
            <p class="text-xs font-medium text-yellow-600 dark:text-yellow-400 uppercase tracking-wide mb-1">In attesa</p>
            <p class="text-2xl font-bold text-yellow-900 dark:text-yellow-200">
                {{ number_format($stats['pending_cents'] / 100, 2, ',', '.') }} €
            </p>
        </div>
        <div class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/50">
            <p class="text-xs font-medium text-red-600 dark:text-red-400 uppercase tracking-wide mb-1">Payout falliti</p>
            <p class="text-2xl font-bold text-red-900 dark:text-red-200">{{ $stats['failed_count'] }}</p>
        </div>
    </div>

    {{-- ── PAYOUT TABLE ────────────────────────────────────────────────────── --}}
    <x-filament::section class="!mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2.5">
                <x-heroicon-o-wallet class="h-6 w-6 text-primary-500 shrink-0"/>
                <span class="text-xl font-bold text-gray-950 dark:text-white">Storico payout</span>
            </div>
        </x-slot>

        {{-- Filters --}}
        <div class="flex flex-wrap items-end gap-3 mb-5">
            <div class="flex flex-col gap-1">
                <label class="text-xs font-medium text-gray-500 uppercase tracking-wide">Stato</label>
                <select
                    wire:model.live="filterStatus"
                    class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                    @foreach($statusOptions as $val => $label)
                        <option value="{{ $val }}">{{ $label }}</option>
                    @endforeach
                </select>
            </div>

            <div class="flex flex-col gap-1">
                <label class="text-xs font-medium text-gray-500 uppercase tracking-wide">Dal</label>
                <input
                    type="date"
                    wire:model.live="filterDateFrom"
                    class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
            </div>

            <div class="flex flex-col gap-1">
                <label class="text-xs font-medium text-gray-500 uppercase tracking-wide">Al</label>
                <input
                    type="date"
                    wire:model.live="filterDateTo"
                    class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
            </div>

            @if($filterStatus !== '' || $filterDateFrom !== '' || $filterDateTo !== '')
                <button
                    wire:click="$set('filterStatus', ''); $set('filterDateFrom', ''); $set('filterDateTo', '')"
                    class="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 underline self-end pb-2"
                >
                    Azzera filtri
                </button>
            @endif
        </div>

        @if($payouts->isEmpty())
            <div class="flex flex-col items-center justify-center py-14 gap-3 text-center">
                <x-heroicon-o-wallet class="h-12 w-12 text-gray-300 dark:text-gray-600"/>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
                    @if($filterStatus !== '' || $filterDateFrom !== '' || $filterDateTo !== '')
                        Nessun payout trovato con i filtri selezionati
                    @else
                        Nessun payout registrato ancora
                    @endif
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 max-w-sm">
                    I payout vengono registrati automaticamente tramite i webhook Stripe.
                    Assicurati che Stripe Connect sia attivo e i webhook siano configurati.
                </p>
            </div>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-100 dark:border-gray-800">
                            <th class="text-left py-2.5 pr-4 font-medium text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Data</th>
                            <th class="text-right py-2.5 pr-4 font-medium text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Importo</th>
                            <th class="text-center py-2.5 pr-4 font-medium text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Stato</th>
                            <th class="text-left py-2.5 pr-4 font-medium text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Arrivo previsto</th>
                            <th class="text-left py-2.5 font-medium text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Note</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50 dark:divide-gray-800/60">
                        @foreach($payouts as $payout)
                            @php $color = $statusColors[$payout->status] ?? $statusColors['cancelled']; @endphp
                            <tr class="group hover:bg-gray-50/60 dark:hover:bg-gray-800/40 transition-colors">
                                <td class="py-3 pr-4 text-gray-700 dark:text-gray-300 tabular-nums">
                                    {{ $payout->created_at->format('d/m/Y') }}
                                </td>
                                <td class="py-3 pr-4 text-right font-semibold text-gray-900 dark:text-white tabular-nums">
                                    {{ $payout->amountFormatted() }}
                                </td>
                                <td class="py-3 pr-4 text-center">
                                    <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide border {{ $color }}">
                                        {{ $payout->statusLabel() }}
                                    </span>
                                </td>
                                <td class="py-3 pr-4 text-gray-600 dark:text-gray-400 tabular-nums">
                                    {{ $payout->arrival_date?->format('d/m/Y') ?? '—' }}
                                </td>
                                <td class="py-3 text-xs text-gray-500 dark:text-gray-500">
                                    @if($payout->failure_reason)
                                        <span class="text-red-500">{{ $payout->failure_reason }}</span>
                                    @else
                                        —
                                    @endif
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            @if($payouts->count() >= 200)
                <p class="mt-3 text-xs text-gray-400 text-center">
                    Mostrando i 200 payout più recenti. Usa i filtri per affinare la ricerca.
                </p>
            @endif
        @endif
    </x-filament::section>

    {{-- ── STRIPE EXPRESS LINK ─────────────────────────────────────────────── --}}
    @if($hasConnect)
        <div class="mt-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Stripe Express Dashboard</p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                    Per gestire metodi di pagamento, scaricare estratti conto e accedere alle impostazioni avanzate del tuo account Stripe.
                </p>
            </div>
            @if($stripeOk)
                <x-filament::button
                    wire:click="openExpressDashboard"
                    wire:loading.attr="disabled"
                    color="gray"
                    size="sm"
                    outlined
                    class="shrink-0"
                >
                    <x-heroicon-o-arrow-top-right-on-square class="h-4 w-4 mr-1.5"/>
                    <span wire:loading.remove wire:target="openExpressDashboard">Apri Stripe Dashboard</span>
                    <span wire:loading wire:target="openExpressDashboard">Caricamento…</span>
                </x-filament::button>
            @endif
        </div>
    @endif
</x-filament-panels::page>
