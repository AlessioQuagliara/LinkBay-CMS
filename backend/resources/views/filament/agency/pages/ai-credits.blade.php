<x-filament-panels::page>

    {{-- ── Saldo ────────────────────────────────────────────────────────────── --}}
    <div class="flex items-center gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
        <x-heroicon-o-sparkles class="w-5 h-5 text-amber-500 shrink-0"/>
        <div>
            <p class="text-xs text-gray-500">Saldo crediti AI</p>
            <p class="text-2xl font-bold">{{ number_format($this->balance()) }}</p>
        </div>
    </div>

    {{-- ── Acquista crediti ─────────────────────────────────────────────────── --}}
    @php $stripeReady = $this->isStripeConfigured(); @endphp

    <x-filament::section heading="Acquista crediti" class="mt-6">

        @if(!$stripeReady)
            <div class="flex items-center gap-3 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 mb-4">
                <x-heroicon-o-exclamation-triangle class="w-5 h-5 text-yellow-600 dark:text-yellow-400 shrink-0"/>
                <p class="text-sm text-yellow-800 dark:text-yellow-300">
                    Stripe non è configurato. Per acquistare crediti contatta:
                    <a href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}" class="underline font-medium">
                        {{ config('mail.from.address', 'support@linkbay.it') }}
                    </a>
                </p>
            </div>
        @endif

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            @foreach($this->packages() as $package)
                @php
                    $hasProduct   = $package->stripe_price_id !== null;
                    $canBuy       = $stripeReady && $hasProduct;
                @endphp
                <div class="border rounded-xl p-5 flex flex-col gap-3
                    {{ $canBuy ? 'border-gray-200 dark:border-gray-700 hover:border-primary-400 hover:shadow-md transition' : 'border-gray-200 dark:border-gray-700 opacity-60' }}">

                    <div class="text-center">
                        <p class="font-bold text-base">{{ $package->name }}</p>
                        <p class="text-3xl font-black text-amber-500 my-1">{{ number_format($package->credits) }}</p>
                        <p class="text-xs text-gray-500 mb-2">crediti</p>
                        <p class="text-xl font-bold">{{ $package->priceFormatted() }}</p>
                    </div>

                    <div class="mt-auto">
                        @if($canBuy)
                            <x-filament::button
                                wire:click="startCheckout({{ $package->id }})"
                                wire:loading.attr="disabled"
                                wire:target="startCheckout({{ $package->id }})"
                                class="w-full">
                                <span wire:loading.remove wire:target="startCheckout({{ $package->id }})">Acquista</span>
                                <span wire:loading wire:target="startCheckout({{ $package->id }})">Caricamento…</span>
                            </x-filament::button>
                        @elseif(!$hasProduct)
                            <p class="text-center text-xs text-gray-400">Prodotto non configurato</p>
                        @else
                            <p class="text-center text-xs text-gray-400">Non disponibile</p>
                        @endif
                    </div>
                </div>
            @endforeach
        </div>
    </x-filament::section>

    {{-- ── Utilizzo per negozio ────────────────────────────────────────────── --}}
    @php $breakdown = $this->storeBreakdown(); @endphp

    <x-filament::section class="mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-building-storefront class="h-5 w-5 text-primary-500 shrink-0"/>
                <span>Utilizzo per negozio</span>
            </div>
        </x-slot>

        <x-slot name="headerEnd">
            {{-- Period filter pills --}}
            <div class="flex items-center gap-1 text-xs">
                @foreach(['30d' => '30 gg', '90d' => '90 gg', 'all' => 'Tutto'] as $val => $label)
                    <button
                        wire:click="$set('filterPeriod', '{{ $val }}')"
                        class="px-2.5 py-1 rounded-full font-medium transition-colors
                            {{ $filterPeriod === $val
                                ? 'bg-primary-500 text-white'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600' }}"
                    >{{ $label }}</button>
                @endforeach
            </div>
        </x-slot>

        @if($breakdown->isEmpty())
            <div class="flex flex-col items-center justify-center py-10 gap-2 text-center">
                <x-heroicon-o-sparkles class="h-10 w-10 text-gray-300 dark:text-gray-600"/>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Nessun consumo registrato
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 max-w-xs">
                    I crediti AI vengono consumati quando i negozi utilizzano funzionalità AI.
                    Nessun utilizzo nei {{ $this->filterPeriodLabel() }}.
                </p>
            </div>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-100 dark:border-gray-800">
                            <th class="text-left py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Negozio</th>
                            <th class="text-right py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Crediti</th>
                            <th class="text-right py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Utilizzi</th>
                            <th class="text-left py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Ultimo utilizzo</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50 dark:divide-gray-800/60">
                        @foreach($breakdown as $row)
                            <tr class="group hover:bg-gray-50/60 dark:hover:bg-gray-800/40 transition-colors">
                                <td class="py-3 pr-4">
                                    <div class="flex items-center gap-2">
                                        @if($row->tenant_id)
                                            <x-heroicon-o-building-storefront class="h-4 w-4 text-gray-400 shrink-0"/>
                                        @else
                                            <x-heroicon-o-cog-6-tooth class="h-4 w-4 text-gray-300 shrink-0"/>
                                        @endif
                                        <span class="font-medium text-gray-900 dark:text-white">{{ $row->store_name }}</span>
                                        @if($row->tenant_id)
                                            <span class="text-xs text-gray-400 font-mono">{{ $row->tenant_id }}</span>
                                        @endif
                                    </div>
                                </td>
                                <td class="py-3 pr-4 text-right">
                                    <span class="font-semibold tabular-nums text-amber-600 dark:text-amber-400">
                                        {{ number_format($row->credits_consumed) }}
                                    </span>
                                </td>
                                <td class="py-3 pr-4 text-right tabular-nums text-gray-600 dark:text-gray-400">
                                    {{ number_format($row->event_count) }}
                                </td>
                                <td class="py-3 text-xs text-gray-500 dark:text-gray-500 tabular-nums whitespace-nowrap">
                                    {{ $row->last_used_at?->format('d/m/Y H:i') ?? '—' }}
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                    <tfoot>
                        <tr class="border-t border-gray-200 dark:border-gray-700">
                            <td class="pt-2.5 pr-4 text-xs font-medium text-gray-500 uppercase tracking-wide">Totale</td>
                            <td class="pt-2.5 pr-4 text-right font-bold tabular-nums text-amber-600 dark:text-amber-400">
                                {{ number_format($breakdown->sum('credits_consumed')) }}
                            </td>
                            <td class="pt-2.5 pr-4 text-right tabular-nums text-gray-600 dark:text-gray-400">
                                {{ number_format($breakdown->sum('event_count')) }}
                            </td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        @endif
    </x-filament::section>

    {{-- ── Storico ──────────────────────────────────────────────────────────── --}}
    <x-filament::section heading="Storico (ultimi 20)" class="mt-6">
        @php $ledger = $this->ledger(); @endphp

        @if($ledger->isEmpty())
            <p class="text-sm text-gray-400 py-4 text-center">Nessuna transazione ancora.</p>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left border-b border-gray-200 dark:border-gray-700">
                            <th class="pb-2 text-gray-500 font-medium">Data</th>
                            <th class="pb-2 text-gray-500 font-medium">Tipo</th>
                            <th class="pb-2 text-gray-500 font-medium">Descrizione</th>
                            <th class="pb-2 text-gray-500 font-medium text-right">Crediti</th>
                            <th class="pb-2 text-gray-500 font-medium text-right">Saldo dopo</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($ledger as $entry)
                            <tr class="border-b border-gray-100 dark:border-gray-800 last:border-0">
                                <td class="py-2 text-xs text-gray-500 whitespace-nowrap">
                                    {{ $entry->created_at->format('d/m/Y H:i') }}
                                </td>
                                <td class="py-2">
                                    <span class="px-2 py-0.5 rounded text-xs font-medium
                                        {{ $entry->type === 'purchase' ? 'bg-green-100 text-green-700' :
                                           ($entry->type === 'bonus' ? 'bg-blue-100 text-blue-700' :
                                           ($entry->type === 'refund' ? 'bg-yellow-100 text-yellow-700' :
                                           'bg-red-100 text-red-700')) }}">
                                        {{ ucfirst($entry->type) }}
                                    </span>
                                </td>
                                <td class="py-2">{{ $entry->description }}</td>
                                <td class="py-2 text-right font-mono {{ $entry->amount > 0 ? 'text-green-600' : 'text-red-600' }}">
                                    {{ $entry->amount > 0 ? '+' : '' }}{{ number_format($entry->amount) }}
                                </td>
                                <td class="py-2 text-right font-mono text-gray-600 dark:text-gray-400">
                                    {{ number_format($entry->balance_after) }}
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @endif
    </x-filament::section>

</x-filament-panels::page>
