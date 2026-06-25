<x-filament-panels::page>
    @php
        $stats              = $this->summaryStats();
        $plan               = $this->currentPlan();
        $planFeatures       = $this->planFeatures();
        $activeEntitlements = $this->activeEntitlements();
        $inactiveEntitlements = $this->inactiveEntitlements();

        $typeColors = [
            'feature'    => 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900/50',
            'theme_pack' => 'bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-900/30 dark:text-purple-400 dark:border-purple-900/50',
            'block_pack' => 'bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-900/50',
            'plugin'     => 'bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-900/30 dark:text-teal-400 dark:border-teal-900/50',
        ];

        $typeLabels = [
            'feature'    => 'Feature',
            'theme_pack' => 'Theme Pack',
            'block_pack' => 'Block Pack',
            'plugin'     => 'Plugin',
        ];

        $sourceColors = [
            'manual'  => 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900/50',
            'promo'   => 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-900/50',
            'license' => 'bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-900/30 dark:text-indigo-400 dark:border-indigo-900/50',
            'plan'    => 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50',
        ];

        $statusColors = [
            'active'  => 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50',
            'expired' => 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
            'revoked' => 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-900/50',
        ];
    @endphp

    {{-- ── KPI CARDS ──────────────────────────────────────────────────────── --}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="p-4 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-900/50">
            <p class="text-xs font-medium text-primary-600 dark:text-primary-400 uppercase tracking-wide mb-1">Feature attive</p>
            <p class="text-2xl font-bold text-primary-900 dark:text-primary-200">{{ $stats['active_features'] }}</p>
            <p class="text-xs text-primary-500 dark:text-primary-400 mt-1">Piano + entitlements</p>
        </div>
        <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/50">
            <p class="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide mb-1">Add-on premium attivi</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-200">{{ $stats['premium_addons'] }}</p>
            <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Entitlements individuali</p>
        </div>
        <div class="p-4 rounded-xl {{ $stats['inactive_count'] > 0 ? 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/50' : 'bg-gray-50 dark:bg-gray-800 border-gray-100 dark:border-gray-700' }} border">
            <p class="text-xs font-medium {{ $stats['inactive_count'] > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400' }} uppercase tracking-wide mb-1">Scaduti / Revocati</p>
            <p class="text-2xl font-bold {{ $stats['inactive_count'] > 0 ? 'text-red-900 dark:text-red-200' : 'text-gray-700 dark:text-gray-200' }}">{{ $stats['inactive_count'] }}</p>
            <p class="text-xs {{ $stats['inactive_count'] > 0 ? 'text-red-500 dark:text-red-400' : 'text-gray-400 dark:text-gray-500' }} mt-1">Non più attivi</p>
        </div>
    </div>

    {{-- ── PIANO CORRENTE ─────────────────────────────────────────────────── --}}
    <x-filament::section class="!mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2.5">
                <x-heroicon-o-identification class="h-6 w-6 text-primary-500 shrink-0"/>
                <span class="text-xl font-bold text-gray-950 dark:text-white">Piano corrente</span>
            </div>
        </x-slot>

        @if($plan)
            <div class="flex flex-col sm:flex-row sm:items-center gap-4 mb-5">
                <div>
                    <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ $plan->name }}</p>
                    @php
                        $price = $plan->price;
                        $interval = $plan->billing_interval === 'year' ? 'anno' : 'mese';
                    @endphp
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                        € {{ number_format((float) $price, 2, ',', '.') }} / {{ $interval }}
                    </p>
                </div>
            </div>

            @if(count($planFeatures) > 0)
                <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-3">Feature incluse nel piano</p>
                    <div class="flex flex-wrap gap-2">
                        @foreach($planFeatures as $code)
                            <span class="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50">
                                <x-heroicon-o-check-circle class="h-3.5 w-3.5"/>
                                {{ $code }}
                            </span>
                        @endforeach
                    </div>
                </div>
            @else
                <p class="text-sm text-gray-400 dark:text-gray-500 italic">Nessuna feature specifica inclusa nel piano corrente.</p>
            @endif
        @else
            <div class="flex items-center gap-3 p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
                <x-heroicon-o-exclamation-triangle class="h-5 w-5 text-yellow-600 shrink-0"/>
                <p class="text-sm text-yellow-800 dark:text-yellow-300">Nessun piano attivo. Vai su <strong>Abbonamento</strong> per attivarne uno.</p>
            </div>
        @endif
    </x-filament::section>

    {{-- ── ENTITLEMENTS ATTIVI ────────────────────────────────────────────── --}}
    <x-filament::section class="!mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2.5">
                <x-heroicon-o-sparkles class="h-6 w-6 text-blue-500 shrink-0"/>
                <span class="text-xl font-bold text-gray-950 dark:text-white">Add-on premium attivi</span>
            </div>
        </x-slot>

        @if($activeEntitlements->isEmpty())
            <div class="flex flex-col items-center justify-center py-10 text-center">
                <x-heroicon-o-puzzle-piece class="h-12 w-12 text-gray-300 dark:text-gray-600 mb-3"/>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Nessun add-on premium attivo</p>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Gli add-on premium vengono assegnati dall'amministratore della piattaforma.</p>
            </div>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead>
                        <tr class="border-b border-gray-200 dark:border-gray-700">
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Nome</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Codice</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Tipo</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Origine</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Stato</th>
                            <th class="pb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Scadenza</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        @foreach($activeEntitlements as $entitlement)
                            @php $item = $entitlement->catalogItem; @endphp
                            <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                <td class="py-3 pr-4 font-medium text-gray-900 dark:text-white">
                                    {{ $item?->name ?? '—' }}
                                </td>
                                <td class="py-3 pr-4 font-mono text-xs text-gray-500 dark:text-gray-400">
                                    {{ $item?->code ?? '—' }}
                                </td>
                                <td class="py-3 pr-4">
                                    @if($item)
                                        <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium {{ $typeColors[$item->type] ?? 'bg-gray-100 text-gray-600 border-gray-200' }}">
                                            {{ $typeLabels[$item->type] ?? $item->type }}
                                        </span>
                                    @else
                                        <span class="text-gray-400">—</span>
                                    @endif
                                </td>
                                <td class="py-3 pr-4">
                                    <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium {{ $sourceColors[$entitlement->source] ?? 'bg-gray-100 text-gray-600 border-gray-200' }}">
                                        {{ \App\Models\Central\AgencyEntitlement::SOURCES[$entitlement->source] ?? $entitlement->source }}
                                    </span>
                                </td>
                                <td class="py-3 pr-4">
                                    <span class="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium {{ $statusColors['active'] }}">
                                        <x-heroicon-o-check-circle class="h-3 w-3"/>
                                        Attivo
                                    </span>
                                </td>
                                <td class="py-3 text-sm text-gray-500 dark:text-gray-400">
                                    {{ $entitlement->ends_at ? $entitlement->ends_at->format('d/m/Y') : 'Nessuna scadenza' }}
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @endif
    </x-filament::section>

    {{-- ── PACK DISPONIBILI (non ancora attivi) ─────────────────────────── --}}
    @php $unavailablePacks = $this->unavailablePremiumPacks(); @endphp
    @if(count($unavailablePacks) > 0)
        <x-filament::section class="!mt-6">
            <x-slot name="heading">
                <div class="flex items-center gap-2.5">
                    <x-heroicon-o-rocket-launch class="h-6 w-6 text-purple-500 shrink-0"/>
                    <span class="text-xl font-bold text-gray-950 dark:text-white">Pack disponibili</span>
                </div>
            </x-slot>

            <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
                I seguenti pack premium non sono ancora attivi per questa agency.
                Contatta il supporto per richiederne l'attivazione.
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                @foreach($unavailablePacks as $pack)
                    <div class="rounded-xl border border-gray-200 dark:border-gray-700 p-5 bg-gray-50 dark:bg-gray-800/50">
                        <div class="flex items-start gap-3 mb-3">
                            @if($pack['type'] === 'theme_pack')
                                <x-heroicon-o-swatch class="h-5 w-5 text-purple-500 shrink-0 mt-0.5"/>
                            @elseif($pack['type'] === 'block_pack')
                                <x-heroicon-o-squares-2x2 class="h-5 w-5 text-orange-500 shrink-0 mt-0.5"/>
                            @else
                                <x-heroicon-o-puzzle-piece class="h-5 w-5 text-gray-400 shrink-0 mt-0.5"/>
                            @endif
                            <div class="min-w-0">
                                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ $pack['label'] }}</p>
                                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-relaxed">{{ $pack['description'] }}</p>
                            </div>
                        </div>

                        <div class="mt-3">
                            <p class="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-2">Contenuto</p>
                            <div class="flex flex-wrap gap-1.5">
                                @foreach($pack['includes'] as $item)
                                    <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium bg-white text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600">
                                        {{ $item }}
                                    </span>
                                @endforeach
                            </div>
                        </div>

                        <div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                            <a
                                href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}"
                                class="text-sm font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
                            >
                                {{ $pack['ctaLabel'] }} →
                            </a>
                        </div>
                    </div>
                @endforeach
            </div>
        </x-filament::section>
    @endif

    {{-- ── ENTITLEMENTS NON ATTIVI ────────────────────────────────────────── --}}
    @if($inactiveEntitlements->isNotEmpty())
        <x-filament::section class="!mt-6">
            <x-slot name="heading">
                <div class="flex items-center gap-2.5">
                    <x-heroicon-o-archive-box class="h-6 w-6 text-gray-400 shrink-0"/>
                    <span class="text-xl font-bold text-gray-950 dark:text-white">Storico — Scaduti e revocati</span>
                </div>
            </x-slot>

            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead>
                        <tr class="border-b border-gray-200 dark:border-gray-700">
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Nome</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Codice</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Tipo</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Origine</th>
                            <th class="pb-3 pr-4 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Stato</th>
                            <th class="pb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Ultima modifica</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        @foreach($inactiveEntitlements as $entitlement)
                            @php $item = $entitlement->catalogItem; @endphp
                            <tr class="opacity-70 hover:opacity-100 transition-opacity">
                                <td class="py-3 pr-4 font-medium text-gray-700 dark:text-gray-300">
                                    {{ $item?->name ?? '—' }}
                                </td>
                                <td class="py-3 pr-4 font-mono text-xs text-gray-400 dark:text-gray-500">
                                    {{ $item?->code ?? '—' }}
                                </td>
                                <td class="py-3 pr-4">
                                    @if($item)
                                        <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium {{ $typeColors[$item->type] ?? 'bg-gray-100 text-gray-600 border-gray-200' }}">
                                            {{ $typeLabels[$item->type] ?? $item->type }}
                                        </span>
                                    @else
                                        <span class="text-gray-400">—</span>
                                    @endif
                                </td>
                                <td class="py-3 pr-4">
                                    <span class="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium {{ $sourceColors[$entitlement->source] ?? 'bg-gray-100 text-gray-600 border-gray-200' }}">
                                        {{ \App\Models\Central\AgencyEntitlement::SOURCES[$entitlement->source] ?? $entitlement->source }}
                                    </span>
                                </td>
                                <td class="py-3 pr-4">
                                    <span class="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium {{ $statusColors[$entitlement->status] ?? 'bg-gray-100 text-gray-600 border-gray-200' }}">
                                        {{ \App\Models\Central\AgencyEntitlement::STATUSES[$entitlement->status] ?? $entitlement->status }}
                                    </span>
                                </td>
                                <td class="py-3 text-sm text-gray-400 dark:text-gray-500">
                                    {{ $entitlement->updated_at?->format('d/m/Y') ?? '—' }}
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </x-filament::section>
    @endif
</x-filament-panels::page>
