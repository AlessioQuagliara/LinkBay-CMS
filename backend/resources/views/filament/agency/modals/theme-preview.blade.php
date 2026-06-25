@php
    use App\Services\ThemeConfigSchema;

    $config   = $preset->normalizedConfig();
    $palette  = $config['palette'] ?? [];
    $typo     = $config['typography'] ?? [];

    $paletteLabels = [
        'primary'   => 'Primario',
        'secondary' => 'Secondario',
        'accent'    => 'Accento',
        'surface'   => 'Sfondo',
        'text'      => 'Testo',
    ];

    $headingFont = ThemeConfigSchema::HEADING_FONTS[$typo['heading_font'] ?? 'inter'] ?? 'Inter';
    $bodyFont    = ThemeConfigSchema::BODY_FONTS[$typo['body_font'] ?? 'inter'] ?? 'Inter';
    $radius      = ThemeConfigSchema::RADIUS_OPTIONS[$config['radius'] ?? 'md'] ?? '—';
    $spacing     = ThemeConfigSchema::SPACING_OPTIONS[$config['spacing'] ?? 'comfortable'] ?? '—';
    $buttons     = ThemeConfigSchema::BUTTON_OPTIONS[$config['buttons'] ?? 'soft'] ?? '—';
@endphp

<div class="space-y-6 pb-2">

    {{-- ── PREVIEW BADGE ───────────────────────────────────────────────────── --}}
    <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 rounded-full border border-purple-300 bg-purple-50 px-3 py-1.5 text-sm font-semibold text-purple-700 dark:border-purple-800 dark:bg-purple-900/20 dark:text-purple-300">
            <x-heroicon-o-eye class="h-4 w-4"/>
            Premium · Anteprima
        </span>
        @if($definition)
            <span class="text-xs text-gray-400 dark:text-gray-500">
                Entitlement richiesto: <span class="font-mono">{{ $definition->featureCode }}</span>
            </span>
        @endif
    </div>

    {{-- ── PALETTE ─────────────────────────────────────────────────────────── --}}
    <div>
        <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
            Palette colori
        </p>
        <div class="grid grid-cols-5 gap-2">
            @foreach($paletteLabels as $key => $label)
                @php $hex = $palette[$key] ?? '#888888'; @endphp
                <div class="text-center">
                    <div class="mb-1.5 h-14 w-full rounded-lg border border-black/10 dark:border-white/10 shadow-sm"
                         style="background-color: {{ $hex }}"></div>
                    <p class="text-xs font-medium text-gray-600 dark:text-gray-300">{{ $label }}</p>
                    <p class="font-mono text-[10px] text-gray-400 dark:text-gray-500">{{ $hex }}</p>
                </div>
            @endforeach
        </div>
    </div>

    {{-- ── PALETTE PREVIEW STRIP ───────────────────────────────────────────── --}}
    @if(isset($palette['surface'], $palette['primary'], $palette['text'], $palette['accent']))
        <div class="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700"
             style="background-color: {{ $palette['surface'] }}">
            {{-- Simulated header bar --}}
            <div class="flex items-center justify-between px-4 py-2.5"
                 style="background-color: {{ $palette['primary'] }}">
                <span class="text-sm font-bold" style="color: {{ $palette['surface'] }}">Storefront Preview</span>
                <span class="h-2 w-16 rounded-full opacity-60" style="background-color: {{ $palette['accent'] }}"></span>
            </div>
            {{-- Simulated content --}}
            <div class="px-4 py-4 space-y-2">
                <div class="h-3 w-2/3 rounded-full opacity-80" style="background-color: {{ $palette['text'] }}"></div>
                <div class="h-2 w-1/2 rounded-full opacity-40" style="background-color: {{ $palette['text'] }}"></div>
                <div class="mt-3 inline-flex items-center rounded-lg px-4 py-1.5 text-xs font-bold"
                     style="background-color: {{ $palette['primary'] }}; color: {{ $palette['surface'] }}">
                    Pulsante CTA
                </div>
            </div>
        </div>
    @endif

    {{-- ── TYPOGRAPHY & STYLE ──────────────────────────────────────────────── --}}
    <div class="grid grid-cols-2 gap-5">
        <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                Tipografia
            </p>
            <dl class="space-y-1 text-sm">
                <div class="flex gap-2">
                    <dt class="text-gray-500 dark:text-gray-400">Titoli</dt>
                    <dd class="font-medium text-gray-800 dark:text-gray-200">{{ $headingFont }}</dd>
                </div>
                <div class="flex gap-2">
                    <dt class="text-gray-500 dark:text-gray-400">Corpo</dt>
                    <dd class="font-medium text-gray-800 dark:text-gray-200">{{ $bodyFont }}</dd>
                </div>
            </dl>
        </div>
        <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                Stile interfaccia
            </p>
            <dl class="space-y-1 text-sm">
                <div class="flex gap-2">
                    <dt class="text-gray-500 dark:text-gray-400">Bordi</dt>
                    <dd class="font-medium text-gray-800 dark:text-gray-200">{{ $radius }}</dd>
                </div>
                <div class="flex gap-2">
                    <dt class="text-gray-500 dark:text-gray-400">Spaziatura</dt>
                    <dd class="font-medium text-gray-800 dark:text-gray-200">{{ $spacing }}</dd>
                </div>
                <div class="flex gap-2">
                    <dt class="text-gray-500 dark:text-gray-400">Pulsanti</dt>
                    <dd class="font-medium text-gray-800 dark:text-gray-200">{{ $buttons }}</dd>
                </div>
            </dl>
        </div>
    </div>

    {{-- ── CALLOUT ─────────────────────────────────────────────────────────── --}}
    <div class="flex items-start gap-3 rounded-xl border border-purple-200 bg-purple-50 p-4 dark:border-purple-800 dark:bg-purple-900/20">
        <x-heroicon-o-lock-closed class="mt-0.5 h-5 w-5 shrink-0 text-purple-500"/>
        <div>
            <p class="text-sm font-semibold text-purple-900 dark:text-purple-200">
                Anteprima disponibile — attivazione richiede accesso al pack
            </p>
            <p class="mt-1 text-sm leading-relaxed text-purple-700 dark:text-purple-400">
                Il tuo storefront continua a usare il tema predefinito finché non è attivo l'entitlement
                @if($definition)
                    <span class="font-mono font-semibold">{{ $definition->featureCode }}</span>.
                @endif
                Questa anteprima mostra il look del tema senza alterare lo store.
            </p>
            <div class="mt-3 flex flex-wrap items-center gap-4">
                <a
                    href="{{ route('filament.agency.pages.my-entitlements') }}"
                    class="text-sm font-semibold text-purple-700 transition-colors hover:text-purple-600 dark:text-purple-400 dark:hover:text-purple-300"
                >
                    Vedi i miei entitlement →
                </a>
                <span class="select-none text-purple-300 dark:text-purple-700">·</span>
                <a
                    href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}"
                    class="text-sm font-medium text-purple-600 transition-colors hover:text-purple-500 dark:text-purple-400"
                >
                    Richiedi attivazione
                </a>
            </div>
        </div>
    </div>

</div>
