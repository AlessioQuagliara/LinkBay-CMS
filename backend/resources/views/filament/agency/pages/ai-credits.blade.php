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
