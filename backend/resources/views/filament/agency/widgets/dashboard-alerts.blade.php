@php
    $alerts  = $this->getAlerts();
    $isOwner = $this->currentMemberIsOwner();

    $cfg = [
        'danger' => [
            'wrap'   => 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
            'title'  => 'text-red-900 dark:text-red-200',
            'body'   => 'text-red-700 dark:text-red-400',
            'note'   => 'text-red-600 dark:text-red-400',
            'icon'   => 'heroicon-o-x-circle',
            'iconCl' => 'text-red-500',
            'cta'    => 'border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40',
        ],
        'warning' => [
            'wrap'   => 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800',
            'title'  => 'text-amber-900 dark:text-amber-200',
            'body'   => 'text-amber-700 dark:text-amber-400',
            'note'   => 'text-amber-600 dark:text-amber-400',
            'icon'   => 'heroicon-o-exclamation-triangle',
            'iconCl' => 'text-amber-500',
            'cta'    => 'border-amber-300 dark:border-amber-700 text-amber-700 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900/40',
        ],
        'info' => [
            'wrap'   => 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
            'title'  => 'text-blue-900 dark:text-blue-200',
            'body'   => 'text-blue-700 dark:text-blue-400',
            'note'   => 'text-blue-600 dark:text-blue-400',
            'icon'   => 'heroicon-o-information-circle',
            'iconCl' => 'text-blue-500',
            'cta'    => 'border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/40',
        ],
    ];
@endphp

@if($alerts->isNotEmpty())
    <div class="space-y-2">
        @foreach($alerts as $alert)
            @php
                $c       = $cfg[$alert->severity] ?? $cfg['info'];
                $canAct  = ! $alert->ctaOwnerOnly || $isOwner;
            @endphp

            <div class="flex items-start gap-3 px-4 py-3 rounded-xl border {{ $c['wrap'] }}">
                {{-- Severity icon --}}
                <x-dynamic-component
                    :component="$c['icon']"
                    class="h-5 w-5 shrink-0 mt-0.5 {{ $c['iconCl'] }}"
                />

                {{-- Text --}}
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold {{ $c['title'] }}">{{ $alert->title }}</p>
                    <p class="text-xs mt-0.5 {{ $c['body'] }}">{{ $alert->body }}</p>
                </div>

                {{-- CTA --}}
                @if($canAct)
                    <a
                        href="{{ route($alert->ctaRoute) }}"
                        class="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-colors {{ $c['cta'] }}"
                    >
                        {{ $alert->ctaLabel }}
                        <x-heroicon-o-arrow-right class="h-3.5 w-3.5" />
                    </a>
                @else
                    <span class="shrink-0 text-xs italic {{ $c['note'] }}">Contatta l'account owner</span>
                @endif
            </div>
        @endforeach
    </div>
@endif
