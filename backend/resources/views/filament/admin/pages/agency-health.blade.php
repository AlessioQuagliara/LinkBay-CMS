<x-filament-panels::page>
    @php
        $stats = $this->summaryStats();
        $rows  = $this->healthData();
    @endphp

    {{-- ── Header KPIs ───────────────────────────────────────────────────────── --}}
    <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        @foreach ([
            ['label' => 'Agencies attive ('.$this->days.'d)', 'value' => $stats['active_agencies'],       'icon' => 'heroicon-o-building-office-2', 'color' => 'text-violet-600 dark:text-violet-400'],
            ['label' => 'Store attivi ('.$this->days.'d)',     'value' => $stats['active_tenants'],         'icon' => 'heroicon-o-shopping-bag',       'color' => 'text-blue-600 dark:text-blue-400'],
            ['label' => 'Con premium pack',                    'value' => $stats['premium_pack_agencies'],  'icon' => 'heroicon-o-star',               'color' => 'text-amber-600 dark:text-amber-400'],
        ] as $kpi)
            <div class="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-white/5">
                <x-filament::icon :icon="$kpi['icon']" class="h-8 w-8 shrink-0 {{ $kpi['color'] }}" />
                <div>
                    <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ number_format($kpi['value']) }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ $kpi['label'] }}</div>
                </div>
            </div>
        @endforeach
    </div>

    {{-- ── Filters ─────────────────────────────────────────────────────────────── --}}
    <div class="mb-5 flex flex-wrap items-end gap-3">

        {{-- Window --}}
        <div>
            <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-300">Finestra</label>
            <select wire:model.live="days"
                    class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-gray-200">
                <option value="7">Ultimi 7 giorni</option>
                <option value="30">Ultimi 30 giorni</option>
                <option value="90">Ultimi 90 giorni</option>
            </select>
        </div>

        {{-- Activity level --}}
        <div>
            <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-300">Attività</label>
            <select wire:model.live="filterActivityLevel"
                    class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-gray-200">
                <option value="">Tutte</option>
                @foreach ($this->activityLevelOptions() as $val => $label)
                    <option value="{{ $val }}">{{ $label }}</option>
                @endforeach
            </select>
        </div>

        {{-- Premium adoption --}}
        <div>
            <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-300">Adozione premium</label>
            <select wire:model.live="filterPremiumAdoption"
                    class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-gray-200">
                <option value="">Tutte</option>
                @foreach ($this->premiumAdoptionOptions() as $val => $label)
                    <option value="{{ $val }}">{{ $label }}</option>
                @endforeach
            </select>
        </div>

        @if ($rows->isNotEmpty())
            <div class="ml-auto text-sm text-gray-400 dark:text-gray-500">
                {{ $rows->count() }} {{ $rows->count() === 1 ? 'agency' : 'agencies' }}
            </div>
        @endif
    </div>

    {{-- ── Health table ──────────────────────────────────────────────────────── --}}
    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-white/10 dark:bg-white/5">
        @if ($rows->isEmpty())
            <div class="px-6 py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                Nessuna agency trovata per i filtri selezionati.
            </div>
        @else
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm dark:divide-white/10">
                    <thead class="bg-gray-50 dark:bg-white/5">
                        <tr>
                            @foreach (['Agency', 'Attività', 'Design', 'Marketing', 'Premium', 'Trend', 'Eventi', 'Store'] as $col)
                                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                    {{ $col }}
                                </th>
                            @endforeach
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-white/5">
                        @foreach ($rows as $row)
                            <tr class="hover:bg-gray-50 dark:hover:bg-white/5">

                                {{-- Agency name --}}
                                <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">
                                    {{ $row->agencyName }}
                                </td>

                                {{-- Activity level badge --}}
                                <td class="px-4 py-3">
                                    @include('filament.admin.pages._health-badge', [
                                        'label' => $row->activityLevel->label(),
                                        'color' => $row->activityLevel->badgeColor(),
                                    ])
                                </td>

                                {{-- Design usage badge --}}
                                <td class="px-4 py-3">
                                    @include('filament.admin.pages._health-badge', [
                                        'label' => $row->designUsageLevel->label(),
                                        'color' => $row->designUsageLevel->badgeColor(),
                                    ])
                                </td>

                                {{-- Marketing usage badge --}}
                                <td class="px-4 py-3">
                                    @include('filament.admin.pages._health-badge', [
                                        'label' => $row->marketingUsageLevel->label(),
                                        'color' => $row->marketingUsageLevel->badgeColor(),
                                    ])
                                </td>

                                {{-- Premium adoption badge --}}
                                <td class="px-4 py-3">
                                    @include('filament.admin.pages._health-badge', [
                                        'label' => $row->premiumAdoptionLevel->label(),
                                        'color' => $row->premiumAdoptionLevel->badgeColor(),
                                    ])
                                </td>

                                {{-- Trend badge --}}
                                <td class="px-4 py-3">
                                    @include('filament.admin.pages._health-badge', [
                                        'label' => $row->trend->label(),
                                        'color' => $row->trend->badgeColor(),
                                    ])
                                </td>

                                {{-- Total events --}}
                                <td class="px-4 py-3 text-right tabular-nums text-gray-700 dark:text-gray-300">
                                    {{ number_format($row->totalEvents) }}
                                </td>

                                {{-- Active tenants --}}
                                <td class="px-4 py-3 text-right tabular-nums text-gray-700 dark:text-gray-300">
                                    {{ $row->activeTenants }}
                                </td>

                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @endif
    </div>
</x-filament-panels::page>
