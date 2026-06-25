<x-filament-panels::page>
    @php
        $insights = $this->insightsData();
        $aliveStores = $insights->aliveStores();
        $calmStores  = $insights->calmStores();
    @endphp

    {{-- ── FILTRO FINESTRA TEMPORALE ─────────────────────────────────────── --}}
    <div class="flex items-center gap-2 mb-6">
        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Periodo:</span>
        @foreach ($this->dayOptions as $option)
            <button
                wire:click="$set('days', {{ $option }})"
                class="px-3 py-1 rounded-full text-sm font-medium transition-colors
                    {{ $this->days === $option
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/20' }}"
            >
                {{ $option }} giorni
            </button>
        @endforeach
    </div>

    {{-- ── KPI CARDS ──────────────────────────────────────────────────────── --}}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

        {{-- Store attivi --}}
        <div class="p-4 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-900/50">
            <p class="text-xs font-medium text-primary-600 dark:text-primary-400 uppercase tracking-wide mb-1">Store attivi</p>
            <p class="text-2xl font-bold text-primary-900 dark:text-primary-200">
                {{ $insights->activeStoresCount }}
                <span class="text-base font-normal text-primary-500 dark:text-primary-400">/ {{ $insights->totalStoresCount }}</span>
            </p>
            <p class="text-xs text-primary-500 dark:text-primary-400 mt-1">Con visite negli ultimi {{ $insights->windowDays }} giorni</p>
        </div>

        {{-- Aggiornamenti layout --}}
        <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/50">
            <p class="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide mb-1">Aggiornamenti layout</p>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-200">{{ $insights->layoutUpdates }}</p>
            <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Layout salvati nel periodo</p>
        </div>

        {{-- Blocchi di campagna (solo con Marketing Pack) --}}
        @if ($insights->hasMarketingPack)
        <div class="p-4 rounded-xl bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-900/50">
            <p class="text-xs font-medium text-orange-600 dark:text-orange-400 uppercase tracking-wide mb-1">Blocchi campagna</p>
            <p class="text-2xl font-bold text-orange-900 dark:text-orange-200">{{ $insights->marketingBlocksUsed }}</p>
            <p class="text-xs text-orange-500 dark:text-orange-400 mt-1">Render blocchi premium</p>
        </div>
        @endif

        {{-- Tendenza --}}
        <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Tendenza</p>
            <p class="text-2xl font-bold text-gray-800 dark:text-gray-100">{{ $insights->trend->label() }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Rispetto al periodo precedente</p>
        </div>

    </div>

    {{-- ── ATTIVITÀ STORE ─────────────────────────────────────────────────── --}}
    <x-filament::section>
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-building-storefront class="h-5 w-5 text-primary-500 shrink-0"/>
                <span>Attività degli store</span>
            </div>
        </x-slot>

        @if (empty($insights->storeActivity))
            <p class="text-sm text-gray-500 dark:text-gray-400 py-2">Nessuno store trovato per questa agenzia.</p>
        @else
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                @foreach ($insights->storeActivity as $store)
                    <div class="flex items-center justify-between px-4 py-3 rounded-lg
                        {{ $store['alive']
                            ? 'bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30'
                            : 'bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700' }}">
                        <span class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate mr-2">
                            {{ $store['name'] ?: $store['id'] }}
                        </span>
                        @if ($store['alive'])
                            <span class="shrink-0 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                                Vivo
                            </span>
                        @else
                            <span class="shrink-0 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-300">
                                Calmo
                            </span>
                        @endif
                    </div>
                @endforeach
            </div>

            @if (count($aliveStores) === 0 && $insights->totalStoresCount > 0)
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-3">
                    Nessuno store ha ricevuto visite negli ultimi {{ $insights->windowDays }} giorni.
                    Controlla che i tuoi store siano online e indicizzabili.
                </p>
            @endif
        @endif
    </x-filament::section>

    {{-- ── BLOCCHI & BUILDER ──────────────────────────────────────────────── --}}
    <x-filament::section class="!mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-squares-2x2 class="h-5 w-5 text-orange-500 shrink-0"/>
                <span>Blocchi & Builder</span>
            </div>
        </x-slot>

        @if ($insights->hasMarketingPack)
            <div class="flex items-start gap-4">
                <div class="flex-1">
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        Il tuo <span class="font-medium">Marketing Block Pack</span> è attivo.
                        Negli ultimi {{ $insights->windowDays }} giorni i blocchi di campagna sono stati resi
                        <span class="font-semibold text-orange-600 dark:text-orange-400">{{ $insights->marketingBlocksUsed }}</span>
                        @if ($insights->marketingBlocksUsed === 1) volta. @else volte. @endif
                    </p>
                    @if ($insights->marketingBlocksUsed === 0)
                        <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            Prova ad inserire un blocco campagna in uno dei tuoi layout per iniziare a raccogliere dati.
                        </p>
                    @endif
                </div>
            </div>
        @else
            <div class="flex items-start gap-3 p-4 rounded-lg bg-orange-50 dark:bg-orange-900/10 border border-orange-100 dark:border-orange-900/30">
                <x-heroicon-o-sparkles class="h-5 w-5 text-orange-500 shrink-0 mt-0.5"/>
                <div>
                    <p class="text-sm font-medium text-orange-800 dark:text-orange-300">Sblocca i blocchi di campagna</p>
                    <p class="text-xs text-orange-600 dark:text-orange-400 mt-0.5">
                        Con il <span class="font-medium">Marketing Block Pack</span> puoi usare blocchi avanzati
                        come price table, testimonial, logo cloud e call-to-action nei tuoi layout.
                    </p>
                </div>
            </div>
        @endif

        <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Aggiornamenti layout</p>
            <p class="text-sm text-gray-700 dark:text-gray-300">
                @if ($insights->layoutUpdates > 0)
                    Hai salvato il layout
                    <span class="font-semibold">{{ $insights->layoutUpdates }}</span>
                    @if ($insights->layoutUpdates === 1) volta @else volte @endif
                    negli ultimi {{ $insights->windowDays }} giorni.
                @else
                    Nessun aggiornamento al layout in questo periodo.
                @endif
            </p>
        </div>
    </x-filament::section>

    {{-- ── TEMI & BRANDING ────────────────────────────────────────────────── --}}
    <x-filament::section class="!mt-6">
        <x-slot name="heading">
            <div class="flex items-center gap-2">
                <x-heroicon-o-swatch class="h-5 w-5 text-purple-500 shrink-0"/>
                <span>Temi & Branding</span>
            </div>
        </x-slot>

        @if ($insights->hasPremiumThemePack)
            <div class="space-y-3">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="px-4 py-3 rounded-lg bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-900/30">
                        <p class="text-xs font-medium text-purple-600 dark:text-purple-400 uppercase tracking-wide mb-1">Render temi premium</p>
                        <p class="text-xl font-bold text-purple-900 dark:text-purple-200">{{ $insights->premiumThemeRenders }}</p>
                        <p class="text-xs text-purple-500 dark:text-purple-400 mt-1">Negli ultimi {{ $insights->windowDays }} giorni</p>
                    </div>
                    <div class="px-4 py-3 rounded-lg bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-900/30">
                        <p class="text-xs font-medium text-indigo-600 dark:text-indigo-400 uppercase tracking-wide mb-1">Varianti di tema create</p>
                        <p class="text-xl font-bold text-indigo-900 dark:text-indigo-200">{{ $insights->themeForksCreated }}</p>
                        <p class="text-xs text-indigo-500 dark:text-indigo-400 mt-1">Fork da temi premium</p>
                    </div>
                </div>
                @if ($insights->premiumThemeRenders === 0 && $insights->themeForksCreated === 0)
                    <p class="text-xs text-gray-400 dark:text-gray-500">
                        Hai accesso ai temi premium ma non sono ancora stati usati in questo periodo.
                        Prova ad assegnare un tema premium a uno dei tuoi store.
                    </p>
                @endif
            </div>
        @else
            <p class="text-sm text-gray-600 dark:text-gray-400">
                I tuoi store utilizzano i temi inclusi nel piano.
                I <span class="font-medium">Theme Pack premium</span> offrono design esclusivi e varianti personalizzabili.
            </p>
        @endif

    </x-filament::section>

</x-filament-panels::page>
