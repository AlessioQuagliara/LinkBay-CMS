<x-filament-panels::page>
    @php
        $hasPlan          = $this->hasActivePlan();
        $isLifetime       = $this->isLifetime();
        $subscription     = $this->subscription();
        $stripeOk         = $this->isStripeConfigured();
        $hasCustomer      = $this->hasStripeCustomer();
        $plans            = $this->availablePlans();
        $billingTypeLabel = $this->billingTypeLabel();
        $recentEvents     = $this->recentBillingEvents();
    @endphp

    {{-- ── PIANO CORRENTE ─────────────────────────────────────────────────── --}}
    <x-filament::section>
        <x-slot name="heading">
            <div class="flex items-center gap-2.5">
                <x-heroicon-o-credit-card class="h-6 w-6 text-primary-500 shrink-0"/>
                <span class="text-xl font-bold text-gray-950 dark:text-white">Piano attuale</span>
            </div>
        </x-slot>

        {{-- Badge Lifetime --}}
        @if($isLifetime)
            <div class="flex items-start gap-4 p-4 rounded-xl bg-amber-50 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-800 mb-6 shadow-sm">
                <div class="p-2.5 rounded-full bg-amber-100 dark:bg-amber-800/40 text-amber-600 dark:text-amber-400 shrink-0">
                    <x-heroicon-o-star class="h-6 w-6"/>
                </div>
                <div>
                    <p class="font-semibold text-amber-900 dark:text-amber-200">Piano Lifetime AppSumo</p>
                    <p class="text-sm text-amber-700 dark:text-amber-400 mt-0.5">Accesso perpetuo — platform share 38% fisso</p>
                </div>
            </div>
        @endif

        {{-- KPI principali --}}
        <div class="grid grid-cols-2 md:grid-cols-5 gap-5 mb-6">
            @php
                $kpiItems = [
                    ['label' => 'Piano',            'value' => $this->planName()],
                    ['label' => 'Prezzo',           'value' => $this->planPrice()],
                    ['label' => 'Fatturazione',     'value' => $billingTypeLabel],
                    ['label' => 'Max Negozi',       'value' => $this->maxStores()],
                    ['label' => 'Fee transazione',  'value' => $this->transactionFee()],
                ];
            @endphp
            @foreach($kpiItems as $kpi)
                <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
                    <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">{{ $kpi['label'] }}</p>
                    <p class="text-xl font-bold text-gray-900 dark:text-white truncate">{{ $kpi['value'] }}</p>
                </div>
            @endforeach
        </div>

        {{-- Stato abbonamento e azioni --}}
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 shadow-inner">
            <div class="flex items-center gap-3.5 flex-wrap">
                @if($subscription)
                    @php
                        $statusColors = [
                            'active'    => 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-900/50',
                            'past_due'  => 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-900/50',
                            'trialing'  => 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-900/50',
                            'cancelled' => 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
                        ];
                        $statusColor = $statusColors[$subscription->status] ?? 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
                        $statusLabels = ['active' => 'Attivo', 'past_due' => 'Pagamento scaduto', 'trialing' => 'In prova', 'cancelled' => 'Cancellato'];
                        $statusLabel = $statusLabels[$subscription->status] ?? ucfirst($subscription->status);
                    @endphp
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border {{ $statusColor }}">
                        {{ $statusLabel }}
                    </span>
                    <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {{ $subscription->renewalLabel() }}
                    </span>
                    @if($subscription->current_period_start)
                        <span class="text-xs text-gray-400 dark:text-gray-500">
                            Attivo dal {{ $subscription->current_period_start->format('d/m/Y') }}
                        </span>
                    @endif
                @elseif($isLifetime)
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-900/50">
                        Lifetime
                    </span>
                    <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Accesso perpetuo</span>
                @else
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600">
                        Nessun abbonamento
                    </span>
                    @if($hasPlan)
                        <span class="text-sm text-gray-500 dark:text-gray-400">Piano assegnato senza abbonamento Stripe attivo</span>
                    @endif
                @endif
            </div>

            @if($stripeOk && $hasCustomer)
                <x-filament::button
                    wire:click="openCustomerPortal"
                    wire:loading.attr="disabled"
                    color="gray"
                    size="sm"
                    outlined
                    class="shadow-sm w-full sm:w-auto shrink-0"
                >
                    <x-heroicon-o-cog-8-tooth class="h-4 w-4 mr-1.5 shrink-0"/>
                    <span wire:loading.remove wire:target="openCustomerPortal">Gestisci abbonamento</span>
                    <span wire:loading wire:target="openCustomerPortal">Caricamento…</span>
                </x-filament::button>
            @endif
        </div>
    </x-filament::section>

    {{-- ── FEATURE INCLUSE ────────────────────────────────────────────────── --}}
    @php
        $limits = $this->features();
        $featureLabels = [
            'white_label'           => 'White-label branding',
            'custom_domain'         => 'Dominio personalizzato',
            'layout_manager'        => 'Layout manager',
            'marketplace_themes'    => 'Temi marketplace',
            'marketplace_plugins'   => 'Plugin marketplace',
            'priority_support'      => 'Supporto prioritario',
            'hide_linkbay_branding' => 'Rimuovi branding LinkBay',
        ];
        $activeFeatures = [];
        if ($limits) {
            $maxS = $limits['max_stores'] ?? null;
            $activeFeatures[] = $maxS === null ? 'Negozi illimitati' : 'Fino a ' . $maxS . ' negozi';
            $aiBonus = (int) ($limits['ai_credits_monthly_bonus'] ?? 0);
            if ($aiBonus > 0) {
                $activeFeatures[] = number_format($aiBonus) . ' crediti AI mensili inclusi';
            }
            foreach ($featureLabels as $key => $label) {
                if (!empty($limits[$key])) {
                    $activeFeatures[] = $label;
                }
            }
        }
    @endphp
    @if(!empty($activeFeatures))
        <x-filament::section class="!mt-10">
            <x-slot name="heading">
                <div class="flex items-center gap-2.5">
                    <x-heroicon-o-check-badge class="h-6 w-6 text-primary-500 shrink-0"/>
                    <span class="text-xl font-bold text-gray-950 dark:text-white">Feature incluse nel piano</span>
                </div>
            </x-slot>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                @foreach($activeFeatures as $feat)
                    <div class="flex items-center gap-3.5 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 shadow-sm transition hover:bg-white dark:hover:bg-gray-800">
                        <x-heroicon-o-check class="h-5 w-5 text-emerald-500 shrink-0"/>
                        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $feat }}</span>
                    </div>
                @endforeach
            </div>
        </x-filament::section>
    @endif

    {{-- ── PIANI DISPONIBILI ──────────────────────────────────────────────── --}}
    @if(!$isLifetime)
        <x-filament::section class="!mt-10">
            <x-slot name="heading">
                <div class="flex items-center gap-2.5">
                    <x-heroicon-o-arrow-trending-up class="h-6 w-6 text-primary-500 shrink-0"/>
                    <span class="text-xl font-bold text-gray-950 dark:text-white">{{ $hasPlan ? 'Cambia piano' : 'Scegli un piano' }}</span>
                </div>
            </x-slot>

            @if(!$stripeOk)
                <div class="flex items-start gap-3 p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 mb-8 shadow-sm">
                    <x-heroicon-o-exclamation-triangle class="h-6 w-6 text-yellow-600 dark:text-yellow-400 shrink-0 mt-0.5"/>
                    <div>
                        <p class="font-semibold text-yellow-900 dark:text-yellow-200">Stripe non configurato</p>
                        <p class="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
                            Contatta il supporto:
                            <a href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}" class="underline font-semibold hover:text-yellow-800 dark:hover:text-yellow-300 transition">
                                {{ config('mail.from.address', 'support@linkbay.it') }}
                            </a>
                        </p>
                    </div>
                </div>
            @endif

            @if($plans->isEmpty())
                <p class="text-sm text-gray-500 text-center py-6">Nessun piano disponibile al momento.</p>
            @else
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
                    @foreach($plans as $plan)
                        @php
                            $isCurrent = $this->agency()?->plan_id === $plan->id;
                            $feeLabel  = ($plan->limits['transaction_fee_pct'] ?? null) ? ($plan->limits['transaction_fee_pct'] . '% fee') : '';
                            $maxS      = $plan->limits['max_stores'] ?? null;
                        @endphp
                        <div class="relative flex flex-col h-full rounded-3xl border shadow-sm transition-all duration-300 hover:shadow-xl hover:-translate-y-1
                            {{ $isCurrent
                                ? 'border-primary-400 bg-primary-50/50 dark:bg-primary-950/20 ring-2 ring-primary-300/50'
                                : 'border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900' }}">
                            @if($isCurrent)
                                <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 z-10">
                                    <span class="px-5 py-1 rounded-full text-xs font-extrabold bg-primary-600 text-white shadow uppercase tracking-wider">
                                        Piano attuale
                                    </span>
                                </div>
                            @endif
                            <div class="p-7 pt-9 flex-grow">
                                <p class="text-2xl font-bold text-gray-950 dark:text-white mb-3 tracking-tight">{{ $plan->name }}</p>
                                <p class="text-5xl font-extrabold text-gray-950 dark:text-white mb-3 tracking-tighter">
                                    €{{ number_format((float) $plan->price, 0, ',', '.') }}
                                    <span class="text-base font-medium text-gray-500 dark:text-gray-400 tracking-normal">
                                        / {{ $plan->billing_interval === 'year' ? 'anno' : 'mese' }}
                                    </span>
                                </p>
                                <hr class="border-gray-100 dark:border-gray-800 my-6">
                                <ul class="space-y-4 mb-8">
                                    <li class="flex items-start gap-3.5 text-sm">
                                        <x-heroicon-o-check class="h-6 w-6 text-emerald-500 shrink-0 mt-0.5"/>
                                        <span class="text-gray-700 dark:text-gray-300 font-medium">
                                            {{ $maxS !== null ? $maxS . ' negozi' : 'Negozi illimitati' }}
                                        </span>
                                    </li>
                                    @if($feeLabel)
                                        <li class="flex items-start gap-3.5 text-sm">
                                            <x-heroicon-o-information-circle class="h-6 w-6 text-blue-500 shrink-0 mt-0.5"/>
                                            <span class="text-gray-700 dark:text-gray-300 font-medium">{{ $feeLabel }} platform share</span>
                                        </li>
                                    @endif
                                    @if($plan->limits['white_label'] ?? false)
                                        <li class="flex items-start gap-3.5 text-sm">
                                            <x-heroicon-o-check class="h-6 w-6 text-emerald-500 shrink-0 mt-0.5"/>
                                            <span class="text-gray-700 dark:text-gray-300 font-medium">White-label branding</span>
                                        </li>
                                    @endif
                                    @if($plan->limits['custom_domain'] ?? false)
                                        <li class="flex items-start gap-3.5 text-sm">
                                            <x-heroicon-o-check class="h-6 w-6 text-emerald-500 shrink-0 mt-0.5"/>
                                            <span class="text-gray-700 dark:text-gray-300 font-medium">Dominio personalizzato</span>
                                        </li>
                                    @endif
                                </ul>
                            </div>
                            <div class="px-7 pb-7 mt-auto rounded-b-3xl bg-gray-50 dark:bg-gray-800/30 border-t border-gray-100 dark:border-gray-800 pt-6">
                                @if($isCurrent && $subscription?->isActive())
                                    <x-filament::button color="gray" class="w-full justify-center shadow-sm" disabled>
                                        Piano attuale
                                    </x-filament::button>
                                @elseif($stripeOk)
                                    @php
                                        $hasActiveSub = $subscription && in_array($subscription->status, ['active', 'trialing', 'past_due']) && $subscription->stripe_subscription_id;
                                        $btnLabel = $isCurrent ? 'Rinnova / Aggiorna' : ($hasActiveSub ? 'Cambia piano' : 'Sottoscrivi');
                                    @endphp
                                    <x-filament::button
                                        wire:click="subscribe({{ $plan->id }})"
                                        wire:loading.attr="disabled"
                                        color="{{ $isCurrent ? 'gray' : 'primary' }}"
                                        class="w-full justify-center shadow-sm"
                                        size="lg"
                                    >
                                        <span wire:loading.remove wire:target="subscribe({{ $plan->id }})">
                                            {{ $btnLabel }}
                                        </span>
                                        <span wire:loading wire:target="subscribe({{ $plan->id }})" class="inline-flex items-center gap-2">
                                            <x-filament::loading-indicator class="h-5 w-5 animate-spin"/>
                                            Caricamento…
                                        </span>
                                    </x-filament::button>
                                @else
                                    <x-filament::button color="gray" class="w-full justify-center shadow-sm" disabled>
                                        Non disponibile
                                    </x-filament::button>
                                @endif
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif

            <p class="mt-10 text-sm text-gray-500 text-center">
                Domande o upgrade per il piano LTD?
                <a href="mailto:{{ config('mail.from.address', 'support@linkbay.it') }}" class="font-semibold underline text-primary-600 hover:text-primary-500 transition">
                    Contatta il supporto
                </a>
            </p>
        </x-filament::section>
    @endif

    {{-- ── CRONOLOGIA PAGAMENTI ───────────────────────────────────────────── --}}
    <x-filament::section class="!mt-10">
        <x-slot name="heading">
            <div class="flex items-center gap-2.5">
                <x-heroicon-o-clock class="h-6 w-6 text-primary-500 shrink-0"/>
                <span class="text-xl font-bold text-gray-950 dark:text-white">Cronologia eventi</span>
            </div>
        </x-slot>

        @if($recentEvents->isEmpty())
            <div class="flex flex-col items-center justify-center py-10 gap-3 text-center">
                <x-heroicon-o-document-magnifying-glass class="h-10 w-10 text-gray-300 dark:text-gray-600"/>
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Nessun evento di fatturazione registrato</p>
                @if($stripeOk && $hasCustomer)
                    <p class="text-xs text-gray-400 dark:text-gray-500">
                        Per visualizzare fatture e pagamenti usa il portale Stripe.
                    </p>
                    <x-filament::button
                        wire:click="openCustomerPortal"
                        color="gray"
                        size="sm"
                        outlined
                        class="mt-2"
                    >
                        <x-heroicon-o-arrow-top-right-on-square class="h-4 w-4 mr-1.5"/>
                        Apri portale Stripe
                    </x-filament::button>
                @endif
            </div>
        @else
            @php
                $eventLabels = [
                    'invoice.paid'                          => 'Pagamento ricevuto',
                    'invoice.payment_failed'                => 'Pagamento fallito',
                    'invoice.payment_succeeded'             => 'Pagamento confermato',
                    'invoice.payment_action_required'       => 'Azione richiesta',
                    'customer.subscription.created'         => 'Abbonamento creato',
                    'customer.subscription.updated'         => 'Abbonamento aggiornato',
                    'customer.subscription.deleted'         => 'Abbonamento cancellato',
                    'customer.subscription.trial_will_end'  => 'Fine trial imminente',
                ];
            @endphp
            <div class="divide-y divide-gray-100 dark:divide-gray-800">
                @foreach($recentEvents as $event)
                    @php
                        $label   = $eventLabels[$event->event_type] ?? $event->event_type;
                        $isError = $event->error !== null;
                        $isPending = $event->processed_at === null && ! $isError;
                    @endphp
                    <div class="flex items-center justify-between py-3.5 gap-4">
                        <div class="flex items-center gap-3.5 min-w-0">
                            @if($isError)
                                <x-heroicon-o-x-circle class="h-5 w-5 text-red-500 shrink-0"/>
                            @elseif($isPending)
                                <x-heroicon-o-clock class="h-5 w-5 text-yellow-500 shrink-0"/>
                            @else
                                <x-heroicon-o-check-circle class="h-5 w-5 text-green-500 shrink-0"/>
                            @endif
                            <div class="min-w-0">
                                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ $label }}</p>
                                @if($isError)
                                    <p class="text-xs text-red-500 truncate">{{ $event->error }}</p>
                                @endif
                            </div>
                        </div>
                        <span class="text-xs text-gray-400 dark:text-gray-500 shrink-0 tabular-nums">
                            {{ $event->created_at->format('d/m/Y H:i') }}
                        </span>
                    </div>
                @endforeach
            </div>

            @if($stripeOk && $hasCustomer)
                <div class="mt-5 pt-5 border-t border-gray-100 dark:border-gray-800 text-center">
                    <x-filament::button
                        wire:click="openCustomerPortal"
                        color="gray"
                        size="sm"
                        outlined
                    >
                        <x-heroicon-o-arrow-top-right-on-square class="h-4 w-4 mr-1.5"/>
                        Scarica fatture complete su Stripe
                    </x-filament::button>
                </div>
            @endif
        @endif
    </x-filament::section>
</x-filament-panels::page>