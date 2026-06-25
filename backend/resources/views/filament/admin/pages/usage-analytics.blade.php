<x-filament-panels::page>
    @php
        $stats = $this->stats();
        $topTenants = $this->topTenants();
        $recentEvents = $this->recentEvents();
    @endphp

    {{-- ── Stats overview (last 30 days) ──────────────────────────────────── --}}
    <div class="mb-6">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Last 30 days
        </h2>
        <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            @foreach ([
                ['label' => 'Active agencies', 'value' => $stats['active_agencies_30d'], 'icon' => 'heroicon-o-building-office-2', 'color' => 'text-violet-600 dark:text-violet-400'],
                ['label' => 'Active stores', 'value' => $stats['active_tenants_30d'], 'icon' => 'heroicon-o-shopping-bag', 'color' => 'text-blue-600 dark:text-blue-400'],
                ['label' => 'Storefronts rendered', 'value' => $stats['storefronts_rendered_30d'], 'icon' => 'heroicon-o-globe-alt', 'color' => 'text-gray-600 dark:text-gray-300'],
                ['label' => 'Premium themes', 'value' => $stats['premium_themes_30d'], 'icon' => 'heroicon-o-swatch', 'color' => 'text-amber-600 dark:text-amber-400'],
                ['label' => 'Premium blocks', 'value' => $stats['premium_blocks_30d'], 'icon' => 'heroicon-o-squares-plus', 'color' => 'text-green-600 dark:text-green-400'],
                ['label' => 'Forks created', 'value' => $stats['forks_created_30d'], 'icon' => 'heroicon-o-scissors', 'color' => 'text-indigo-600 dark:text-indigo-400'],
            ] as $stat)
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-white/5">
                    <div class="flex items-center gap-2 mb-2">
                        <x-filament::icon
                            :icon="$stat['icon']"
                            class="h-4 w-4 {{ $stat['color'] }}"
                        />
                        <span class="text-xs text-gray-500 dark:text-gray-400">{{ $stat['label'] }}</span>
                    </div>
                    <span class="text-2xl font-bold text-gray-900 dark:text-white">
                        {{ number_format($stat['value']) }}
                    </span>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ── Two-column layout ────────────────────────────────────────────────── --}}
    <div class="grid gap-6 lg:grid-cols-2">

        {{-- Top active tenants --}}
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-white/10 dark:bg-white/5">
            <div class="border-b border-gray-100 px-5 py-4 dark:border-white/10">
                <h3 class="font-semibold text-gray-900 dark:text-white">Top active stores (30d)</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ranked by total event count</p>
            </div>
            <div class="divide-y divide-gray-100 dark:divide-white/5">
                @forelse ($topTenants as $i => $row)
                    <div class="flex items-center justify-between px-5 py-3">
                        <div class="flex items-center gap-3">
                            <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-500 dark:bg-white/10 dark:text-gray-300">
                                {{ $i + 1 }}
                            </span>
                            <span class="font-mono text-sm text-gray-700 dark:text-gray-200">
                                {{ $row->tenant_id }}
                            </span>
                        </div>
                        <span class="rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-semibold text-violet-700 dark:bg-violet-900/30 dark:text-violet-300">
                            {{ number_format($row->event_count) }}
                        </span>
                    </div>
                @empty
                    <div class="px-5 py-8 text-center text-sm text-gray-400 dark:text-gray-500">
                        No data yet
                    </div>
                @endforelse
            </div>
        </div>

        {{-- Recent events --}}
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-white/10 dark:bg-white/5">
            <div class="border-b border-gray-100 px-5 py-4 dark:border-white/10">
                <h3 class="font-semibold text-gray-900 dark:text-white">Recent events</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Last 30 entries</p>
            </div>
            <div class="divide-y divide-gray-100 dark:divide-white/5 overflow-y-auto max-h-[480px]">
                @forelse ($recentEvents as $event)
                    <div class="flex items-start justify-between gap-3 px-5 py-3">
                        <div class="min-w-0">
                            <span class="inline-block rounded-md bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-700 dark:bg-white/10 dark:text-gray-200">
                                {{ $event->event_type }}
                            </span>
                            @if ($event->agency)
                                <span class="mt-0.5 block truncate text-xs text-gray-500 dark:text-gray-400">
                                    {{ $event->agency->name }}
                                    @if ($event->tenant_id)
                                        · {{ $event->tenant_id }}
                                    @endif
                                </span>
                            @elseif ($event->tenant_id)
                                <span class="mt-0.5 block truncate font-mono text-xs text-gray-500 dark:text-gray-400">
                                    {{ $event->tenant_id }}
                                </span>
                            @endif
                        </div>
                        <span class="shrink-0 text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
                            {{ $event->occurred_at->diffForHumans() }}
                        </span>
                    </div>
                @empty
                    <div class="px-5 py-8 text-center text-sm text-gray-400 dark:text-gray-500">
                        No events recorded yet
                    </div>
                @endforelse
            </div>
        </div>
    </div>
</x-filament-panels::page>
