@php
    $packs = $this->getUnavailableThemePacks();
    $single = count($packs) === 1;
@endphp

<x-filament::section class="border border-purple-300 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20">
    <div class="flex items-start gap-4">
        <div class="shrink-0 mt-0.5">
            <x-heroicon-o-swatch class="w-5 h-5 text-purple-500"/>
        </div>

        <div class="flex-1 min-w-0">
            @if($single)
                <p class="text-sm font-semibold text-purple-900 dark:text-purple-200">
                    {{ $packs[0]['label'] }} non incluso
                </p>
                <p class="text-sm text-purple-700 dark:text-purple-400 mt-1 leading-relaxed">
                    {{ $packs[0]['description'] }}
                    Temi inclusi: <span class="font-medium">{{ implode(', ', $packs[0]['includes']) }}</span>.
                </p>
            @else
                <p class="text-sm font-semibold text-purple-900 dark:text-purple-200">
                    Theme Pack Premium non inclusi
                </p>
                <div class="mt-1 space-y-1">
                    @foreach($packs as $pack)
                        <p class="text-sm text-purple-700 dark:text-purple-400">
                            <span class="font-medium">{{ $pack['label'] }}</span>:
                            {{ implode(', ', $pack['includes']) }}.
                        </p>
                    @endforeach
                </div>
            @endif

            <div class="mt-3 flex flex-wrap items-center gap-4">
                <a
                    href="{{ route('filament.agency.pages.my-entitlements') }}"
                    class="inline-flex items-center text-sm font-semibold text-purple-700 hover:text-purple-600 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
                >
                    Vedi i miei entitlement
                    <x-heroicon-o-arrow-right class="w-3.5 h-3.5 ml-1"/>
                </a>
                <span class="text-purple-300 dark:text-purple-700 select-none">·</span>
                <a
                    href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}"
                    class="text-sm font-medium text-purple-600 hover:text-purple-500 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
                >
                    Richiedi attivazione
                </a>
            </div>
        </div>
    </div>
</x-filament::section>
