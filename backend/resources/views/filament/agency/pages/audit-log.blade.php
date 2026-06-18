<x-filament-panels::page>
    @php
        $events       = $this->events();
        $eventOptions = $this->eventTypeOptions();
        $actorOptions = $this->actorOptions();
        $hasFilters   = $this->hasActiveFilters();

        $severityClasses = [
            'danger'  => 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-900/50',
            'warning' => 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-900/50',
            'success' => 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50',
        ];
    @endphp

    {{-- ── Filters ──────────────────────────────────────────────────────────── --}}
    <x-filament::section>
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-funnel class="h-5 w-5 text-primary-500 shrink-0"/>
                <span>Filtri</span>
            </div>
        </x-slot>

        <x-slot name="headerEnd">
            @if($hasFilters)
                <button
                    wire:click="clearFilters"
                    class="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                >
                    Azzera filtri
                </button>
            @endif
        </x-slot>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {{-- Event type --}}
            <div>
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Tipo di evento</label>
                <select
                    wire:model.live="filterEvent"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                    <option value="">Tutti gli eventi</option>
                    @foreach($eventOptions as $value => $label)
                        <option value="{{ $value }}">{{ $label }}</option>
                    @endforeach
                </select>
            </div>

            {{-- Actor --}}
            <div>
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Utente</label>
                <select
                    wire:model.live="filterUser"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                    <option value="">Tutti gli utenti</option>
                    @foreach($actorOptions as $id => $name)
                        <option value="{{ $id }}">{{ $name }}</option>
                    @endforeach
                </select>
            </div>

            {{-- Date from --}}
            <div>
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Dal</label>
                <input
                    type="date"
                    wire:model.live="filterDateFrom"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
            </div>

            {{-- Date to --}}
            <div>
                <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Al</label>
                <input
                    type="date"
                    wire:model.live="filterDateTo"
                    class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
            </div>
        </div>
    </x-filament::section>

    {{-- ── Event log table ─────────────────────────────────────────────────── --}}
    <x-filament::section class="mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-clipboard-document-list class="h-5 w-5 text-primary-500 shrink-0"/>
                <span>Cronologia operazioni</span>
            </div>
        </x-slot>

        <x-slot name="headerEnd">
            <span class="text-xs text-gray-400">
                {{ $events->count() }} {{ $events->count() === 1 ? 'evento' : 'eventi' }}
                @if($events->count() >= 500)(max 500)@endif
            </span>
        </x-slot>

        @if($events->isEmpty())
            <div class="flex flex-col items-center justify-center py-12 gap-2 text-center">
                <x-heroicon-o-shield-check class="h-10 w-10 text-gray-300 dark:text-gray-600"/>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Nessun evento trovato</p>
                <p class="text-xs text-gray-400 dark:text-gray-500">
                    @if($hasFilters)
                        Nessun risultato per i filtri applicati.
                    @else
                        Le operazioni sensibili verranno registrate qui.
                    @endif
                </p>
            </div>
        @else
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-100 dark:border-gray-800">
                            <th class="text-left py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide whitespace-nowrap">Data / Ora</th>
                            <th class="text-left py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Utente</th>
                            <th class="text-left py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Evento</th>
                            <th class="text-left py-2.5 pr-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Oggetto</th>
                            <th class="text-left py-2.5 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Dettagli</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50 dark:divide-gray-800/60">
                        @foreach($events as $event)
                            @php $color = $severityClasses[$event->severityColor()]; @endphp
                            <tr class="group hover:bg-gray-50/60 dark:hover:bg-gray-800/40 transition-colors align-top">

                                {{-- Timestamp --}}
                                <td class="py-3 pr-4 whitespace-nowrap">
                                    <span class="text-xs text-gray-500 dark:text-gray-500 tabular-nums">
                                        {{ $event->created_at->format('d/m/Y') }}
                                    </span>
                                    <br>
                                    <span class="text-xs text-gray-400 tabular-nums">
                                        {{ $event->created_at->format('H:i:ss') }}
                                    </span>
                                </td>

                                {{-- Actor --}}
                                <td class="py-3 pr-4">
                                    <span class="font-medium text-gray-800 dark:text-gray-200 text-xs">
                                        {{ $event->actorLabel() }}
                                    </span>
                                    @if($event->ip_address)
                                        <br>
                                        <span class="text-xs text-gray-400 font-mono">{{ $event->ip_address }}</span>
                                    @endif
                                </td>

                                {{-- Event badge --}}
                                <td class="py-3 pr-4">
                                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border {{ $color }}">
                                        {{ $event->eventLabel() }}
                                    </span>
                                </td>

                                {{-- Subject --}}
                                <td class="py-3 pr-4">
                                    <span class="text-xs text-gray-600 dark:text-gray-400">
                                        {{ $event->subjectLabel() }}
                                    </span>
                                </td>

                                {{-- Details (old/new values summary) --}}
                                <td class="py-3">
                                    @if($event->new_values || $event->old_values || $event->metadata)
                                        <div class="text-xs space-y-0.5 max-w-xs">
                                            @if($event->new_values)
                                                @foreach($event->new_values as $key => $val)
                                                    <div class="flex gap-1.5 items-baseline">
                                                        <span class="text-gray-400 shrink-0">{{ $key }}:</span>
                                                        <span class="text-gray-700 dark:text-gray-300 font-medium truncate">
                                                            {{ is_array($val) ? json_encode($val) : $val }}
                                                        </span>
                                                    </div>
                                                @endforeach
                                            @endif

                                            @if($event->old_values && $event->new_values)
                                                <div class="text-gray-400 text-[10px] pt-0.5">
                                                    da: {{ implode(', ', array_map(fn($v) => is_array($v) ? json_encode($v) : $v, $event->old_values)) }}
                                                </div>
                                            @endif

                                            @if($event->metadata && ! $event->new_values)
                                                @foreach($event->metadata as $key => $val)
                                                    <div class="flex gap-1.5 items-baseline">
                                                        <span class="text-gray-400 shrink-0">{{ $key }}:</span>
                                                        <span class="text-gray-700 dark:text-gray-300 truncate">
                                                            {{ is_array($val) ? json_encode($val) : $val }}
                                                        </span>
                                                    </div>
                                                @endforeach
                                            @endif
                                        </div>
                                    @else
                                        <span class="text-gray-300 dark:text-gray-600">—</span>
                                    @endif
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @endif
    </x-filament::section>

</x-filament-panels::page>
