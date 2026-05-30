<x-filament-panels::page>
    {{-- Fee attuale -------------------------------------------------------}}
    @php
        $rule   = $this->currentFeeRule();
        $totals = $this->aggregateTotals();
        $stores = $this->stores();
    @endphp

    <x-filament::section heading="Fee piattaforma attuale">
        @if($rule)
            <div class="flex flex-wrap items-center gap-6">
                <div class="text-center">
                    <p class="text-xs text-gray-500">Platform Share</p>
                    <p class="text-2xl font-bold text-primary-600">{{ $rule->feePctAsPercent() }}</p>
                </div>
                <div class="text-sm text-gray-500 space-y-1">
                    <p>Piano: <strong>{{ $rule->plan?->name ?? '—' }}</strong></p>
                    <p>Tipo: <strong>{{ ucfirst($rule->fee_type) }}</strong></p>
                    <p class="text-xs">Valida dal {{ $rule->valid_from->format('d/m/Y') }}</p>
                    @if($rule->description)
                        <p class="text-xs italic">{{ $rule->description }}</p>
                    @endif
                </div>
                <div class="ml-auto text-xs text-gray-400 max-w-sm">
                    Questa percentuale viene trattenuta da LinkBayCMS su ogni pagamento processato dai tuoi clienti finali tramite il tuo account Stripe Connect.
                </div>
            </div>
        @else
            <div class="flex items-start gap-2 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 text-sm">
                <x-heroicon-o-exclamation-triangle class="w-4 h-4 text-yellow-600 shrink-0 mt-0.5" />
                <span class="text-yellow-800 dark:text-yellow-300">
                    Nessuna regola fee trovata per il piano <strong>{{ $this->missingRulePlanName() }}</strong>.
                    Contatta il supporto: <a href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}" class="underline">{{ config('mail.from.address', 'support@linkbay.it') }}</a>
                </span>
            </div>
        @endif
    </x-filament::section>

    {{-- Totali periodo ----------------------------------------------------}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
            <p class="text-xs text-gray-500">Transazioni</p>
            <p class="text-2xl font-bold">{{ number_format($totals['count']) }}</p>
        </div>
        <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
            <p class="text-xs text-gray-500">GMV lordo</p>
            <p class="text-2xl font-bold">€{{ number_format($totals['gross'] / 100, 2, ',', '.') }}</p>
        </div>
        <div class="text-center p-4 rounded-lg bg-red-50 dark:bg-red-900/20">
            <p class="text-xs text-gray-500">Fee LinkBay</p>
            <p class="text-2xl font-bold text-red-600">€{{ number_format($totals['fee'] / 100, 2, ',', '.') }}</p>
        </div>
        <div class="text-center p-4 rounded-lg bg-green-50 dark:bg-green-900/20">
            <p class="text-xs text-gray-500">Netto a te</p>
            <p class="text-2xl font-bold text-green-600">€{{ number_format($totals['net'] / 100, 2, ',', '.') }}</p>
        </div>
    </div>

    {{-- Filtri ------------------------------------------------------------}}
    <x-filament::section class="mt-6">
        <div class="flex flex-wrap items-end gap-4">
            <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Periodo</label>
                <select wire:model.live="filterPeriod"
                        class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2">
                    <option value="month">Questo mese</option>
                    <option value="quarter">Questo trimestre</option>
                    <option value="year">Quest'anno</option>
                    <option value="all">Tutti</option>
                </select>
            </div>

            @if($stores->isNotEmpty())
            <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Store</label>
                <select wire:model.live="filterStore"
                        class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2">
                    <option value="">Tutti gli store</option>
                    @foreach($stores as $store)
                        <option value="{{ $store->id }}">{{ $store->name }}</option>
                    @endforeach
                </select>
            </div>
            @endif

            <div class="ml-auto">
                <x-filament::button
                    wire:click="exportCsv"
                    color="gray"
                    icon="heroicon-o-arrow-down-tray"
                >
                    Esporta CSV
                </x-filament::button>
            </div>
        </div>
    </x-filament::section>

    {{-- Tabella commissioni -----------------------------------------------}}
    <x-filament::section class="mt-4">
        @php $commissions = $this->commissions(); @endphp

        @if($commissions->isEmpty())
            <p class="text-sm text-gray-400 text-center py-8">
                Nessuna commissione trovata per il periodo selezionato.
            </p>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left border-b border-gray-200 dark:border-gray-700">
                            <th class="pb-3 pr-4 text-gray-500 font-medium">Data</th>
                            <th class="pb-3 pr-4 text-gray-500 font-medium">Store</th>
                            <th class="pb-3 pr-4 text-gray-500 font-medium text-right">GMV</th>
                            <th class="pb-3 pr-4 text-gray-500 font-medium text-right">Fee %</th>
                            <th class="pb-3 pr-4 text-gray-500 font-medium text-right">Fee LinkBay</th>
                            <th class="pb-3 pr-4 text-gray-500 font-medium text-right">Netto</th>
                            <th class="pb-3 text-gray-500 font-medium">Stato</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($commissions as $c)
                        <tr class="border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td class="py-3 pr-4 text-gray-500 text-xs whitespace-nowrap">
                                {{ $c->created_at->format('d/m/Y H:i') }}
                            </td>
                            <td class="py-3 pr-4 text-xs font-mono">
                                {{ $c->tenant_id ?? '—' }}
                            </td>
                            <td class="py-3 pr-4 text-right font-mono">
                                {{ $c->grossFormatted() }}
                            </td>
                            <td class="py-3 pr-4 text-right text-gray-500">
                                {{ $c->feePctFormatted() }}
                            </td>
                            <td class="py-3 pr-4 text-right font-mono text-red-600 dark:text-red-400">
                                {{ $c->feeFormatted() }}
                            </td>
                            <td class="py-3 pr-4 text-right font-mono text-green-600 dark:text-green-400">
                                {{ $c->netFormatted() }}
                            </td>
                            <td class="py-3">
                                @php
                                    $badge = match($c->status) {
                                        'settled'  => ['bg-green-100 text-green-700', 'Pagato'],
                                        'pending'  => ['bg-yellow-100 text-yellow-700', 'In attesa'],
                                        'refunded' => ['bg-blue-100 text-blue-700', 'Rimborsato'],
                                        'disputed' => ['bg-red-100 text-red-700', 'Contestato'],
                                        default    => ['bg-gray-100 text-gray-600', ucfirst($c->status)],
                                    };
                                @endphp
                                <span class="px-2 py-0.5 rounded text-xs font-medium {{ $badge[0] }}">
                                    {{ $badge[1] }}
                                </span>
                            </td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
            <p class="mt-3 text-xs text-gray-400">Mostrate le ultime 200 righe. Usa l'export CSV per il dettaglio completo.</p>
        @endif
    </x-filament::section>
</x-filament-panels::page>
