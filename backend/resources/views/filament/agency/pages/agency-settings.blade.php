<x-filament-panels::page>
    <div>
        {{-- Riga superiore: Brand + Dominio Custom --}}
        <div class="grid grid-cols-1 md:grid-cols-2">
            {{-- CARD BRAND --}}
            <div style="padding: 1.5rem;">
                <x-filament::section class="h-full">
                    <x-slot name="heading">
                        <div class="flex items-center gap-2">
                            <x-heroicon-o-paint-brush class="w-5 h-5 shrink-0 text-primary-500"/>
                            <span>Brand</span>
                        </div>
                    </x-slot>

                    @if($this->canAccessWhiteLabel())
                        @php $brand = $this->brandData ?? []; @endphp
                        <div x-data="{ editing: false }">
                            {{-- RIEPILOGO --}}
                            <div x-show="!editing" class="space-y-4">
                                <div class="flex items-center gap-4">
                                    @if(!empty($brand['logo_url']))
                                        <img src="{{ $brand['logo_url'] }}" alt="Logo" class="h-10 w-auto object-contain rounded border bg-white p-1"/>
                                    @else
                                        <div class="w-10 h-10 rounded bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                                            <x-heroicon-o-photo class="w-5 h-5 shrink-0 text-gray-400"/>
                                        </div>
                                    @endif
                                    <div>
                                        <p class="font-semibold text-lg">{{ $brand['brand_name'] ?? '—' }}</p>
                                        <p class="text-sm text-gray-500">
                                            @if(!empty($brand['support_email']))
                                                Supporto: {{ $brand['support_email'] }}
                                            @else
                                                Nessuna email di supporto
                                            @endif
                                        </p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-2 text-sm">
                                    <span class="inline-block w-4 h-4 rounded-full border" style="background-color: {{ $brand['primary_color'] ?? '#999' }}"></span>
                                    <span class="text-gray-600 dark:text-gray-300">{{ $brand['primary_color'] ?? 'Nessun colore primario' }}</span>
                                </div>
                                <x-filament::button size="sm" x-on:click="editing = true">Modifica</x-filament::button>
                            </div>

                            {{-- FORM MODIFICA --}}
                            <div x-show="editing" x-cloak>
                                <form wire:submit="saveBrand" class="space-y-4">
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        <x-filament::input.wrapper label="Brand Name">
                                            <x-filament::input type="text" wire:model="brandData.brand_name" />
                                        </x-filament::input.wrapper>

                                        {{-- Logo upload --}}
                                        <div class="space-y-1">
                                            <p class="text-sm font-medium text-gray-700 dark:text-gray-200">Logo</p>
                                            @if(!empty($brand['logo_url']))
                                                <div class="flex items-center gap-2">
                                                    <img src="{{ $brand['logo_url'] }}" alt="Logo" class="h-8 w-auto object-contain rounded border bg-white p-0.5"/>
                                                    <button wire:click="clearLogo" type="button" class="text-xs text-red-500 hover:underline">Rimuovi</button>
                                                </div>
                                            @endif
                                            <input type="file" wire:model="logoFile" accept="image/*"
                                                   class="block w-full text-sm text-gray-600 dark:text-gray-400 file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"/>
                                            @error('logoFile') <p class="text-xs text-red-500">{{ $message }}</p> @enderror
                                            <p class="text-xs text-gray-400">Oppure incolla URL:</p>
                                            <x-filament::input type="url" wire:model="brandData.logo_url" placeholder="https://..." />
                                        </div>

                                        {{-- Favicon upload --}}
                                        <div class="space-y-1">
                                            <p class="text-sm font-medium text-gray-700 dark:text-gray-200">Favicon</p>
                                            @if(!empty($brand['favicon_url']))
                                                <div class="flex items-center gap-2">
                                                    <img src="{{ $brand['favicon_url'] }}" alt="Favicon" class="h-6 w-6 object-contain rounded border bg-white p-0.5"/>
                                                    <button wire:click="clearFavicon" type="button" class="text-xs text-red-500 hover:underline">Rimuovi</button>
                                                </div>
                                            @endif
                                            <input type="file" wire:model="faviconFile" accept="image/*"
                                                   class="block w-full text-sm text-gray-600 dark:text-gray-400 file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"/>
                                            @error('faviconFile') <p class="text-xs text-red-500">{{ $message }}</p> @enderror
                                            <p class="text-xs text-gray-400">Oppure incolla URL:</p>
                                            <x-filament::input type="url" wire:model="brandData.favicon_url" placeholder="https://..." />
                                        </div>

                                        <x-filament::input.wrapper label="Colore primario">
                                            <input type="color" wire:model="brandData.primary_color" class="w-12 h-10 rounded border" />
                                        </x-filament::input.wrapper>
                                        <x-filament::input.wrapper label="Email supporto">
                                            <x-filament::input type="email" wire:model="brandData.support_email" />
                                        </x-filament::input.wrapper>
                                        <x-filament::input.wrapper label="URL supporto">
                                            <x-filament::input type="url" wire:model="brandData.support_url" />
                                        </x-filament::input.wrapper>
                                    </div>
                                    <div class="flex gap-2">
                                        <x-filament::button type="submit" size="sm">Salva</x-filament::button>
                                        <x-filament::button color="gray" size="sm" x-on:click="editing = false">Annulla</x-filament::button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    @else
                        <div class="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 text-sm">
                            <span class="text-amber-800 dark:text-amber-300">
                                White-label disponibile sul piano Pro.
                                <a href="{{ route('filament.agency.pages.agency-billing') }}" class="font-medium underline ml-1">Aggiorna piano →</a>
                            </span>
                        </div>
                    @endif
                </x-filament::section>
            </div>

            {{-- CARD DOMINIO CUSTOM --}}
            <div style="padding: 1.5rem;">
                <x-filament::section class="h-full">
                    <x-slot name="heading">
                        <div class="flex items-center gap-2">
                            <x-heroicon-o-globe-alt class="w-5 h-5 shrink-0 text-primary-500"/>
                            <span>Dominio Custom</span>
                        </div>
                    </x-slot>

                    @if($this->canAccessCustomDomain())
                        @php $domainData = $this->domainData ?? []; @endphp
                        <div x-data="{ editing: false }">
                            <div x-show="!editing" class="space-y-4">
                                <div class="flex items-center gap-2">
                                    @if(!empty($domainData['custom_domain']))
                                        <x-heroicon-o-check-circle class="w-5 h-5 shrink-0 text-green-500"/>
                                        <span class="font-medium">{{ $domainData['custom_domain'] }}</span>
                                    @else
                                        <x-heroicon-o-x-circle class="w-5 h-5 shrink-0 text-gray-400"/>
                                        <span class="text-gray-500">Nessun dominio personalizzato</span>
                                    @endif
                                </div>
                                <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-mono space-y-1">
                                    <p class="font-sans text-xs text-gray-500 font-medium mb-1">Configurazione DNS:</p>
                                    <p>CNAME &nbsp;<span class="text-blue-600">cms.tuodominio.it</span> → <span class="text-blue-600">linkbay-cms.com</span></p>
                                    <p class="font-sans text-gray-400">Propagazione: fino a 48 ore.</p>
                                </div>
                                <x-filament::button size="sm" x-on:click="editing = true">Modifica</x-filament::button>
                            </div>

                            <div x-show="editing" x-cloak>
                                <form wire:submit="saveDomain" class="space-y-4">
                                    <x-filament::input.wrapper label="Dominio personalizzato">
                                        <x-filament::input type="text" wire:model="domainData.custom_domain" placeholder="cms.miagenzia.it" />
                                    </x-filament::input.wrapper>
                                    <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-mono space-y-1">
                                        <p class="font-sans text-xs text-gray-500 font-medium mb-1">Configurazione DNS:</p>
                                        <p>CNAME &nbsp;<span class="text-blue-600">cms.tuodominio.it</span> → <span class="text-blue-600">linkbay-cms.com</span></p>
                                        <p class="font-sans text-gray-400">Propagazione: fino a 48 ore.</p>
                                    </div>
                                    <div class="flex gap-2">
                                        <x-filament::button type="submit" size="sm">Salva</x-filament::button>
                                        <x-filament::button color="gray" size="sm" x-on:click="editing = false">Annulla</x-filament::button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    @else
                        <div class="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 text-sm">
                            <span class="text-amber-800 dark:text-amber-300">
                                Dominio personalizzato disponibile sul piano Business.
                                <a href="{{ route('filament.agency.pages.agency-billing') }}" class="font-medium underline ml-1">Aggiorna piano →</a>
                            </span>
                        </div>
                    @endif
                </x-filament::section>
            </div>
        </div>

        {{-- CARD STRIPE CONNECT (larghezza piena) --}}
        <div style="padding: 1.5rem;">
            <x-filament::section>
                <x-slot name="heading">
                    <div class="flex items-center gap-2">
                        <x-heroicon-o-credit-card class="w-5 h-5 shrink-0 text-primary-500"/>
                        <span>Stripe Connect</span>
                    </div>
                </x-slot>

                <div class="space-y-4">
                    @if($this->stripeIsOnboarded())
                        <div class="flex flex-wrap items-center gap-4">
                            <div class="flex items-center gap-2">
                                <x-heroicon-o-check-circle class="w-5 h-5 shrink-0 text-green-500"/>
                                <span class="font-medium text-green-600">Account Stripe collegato</span>
                            </div>
                            <x-filament::badge color="gray">
                                Fee: <strong>{{ $this->currentTransactionFee() }}</strong> per transazione
                            </x-filament::badge>
                        </div>
                        <a href="https://dashboard.stripe.com" target="_blank" class="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:underline">
                            Apri Stripe Dashboard →
                        </a>
                    @else
                        <div class="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
                            <p class="font-medium">Collega il tuo account Stripe per ricevere pagamenti</p>
                            <p class="text-sm text-gray-500 mt-1">LinkBayCMS trattiene il {{ $this->currentTransactionFee() }} per transazione.</p>
                            @php $url = $this->getStripeConnectUrl(); @endphp
                            @if($url)
                                <a href="{{ $url }}" class="mt-3 inline-block">
                                    <x-filament::button color="warning">Collega Stripe →</x-filament::button>
                                </a>
                            @else
                                <div class="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-sm mt-3">
                                    <span class="text-red-700 dark:text-red-300">
                                        Integrazione Stripe temporaneamente non disponibile.
                                        Contatta il supporto su
                                        <a href="mailto:support@linkbay-cms.com" class="underline font-medium">support@linkbay-cms.com</a>.
                                    </span>
                                </div>
                            @endif
                        </div>
                    @endif
                </div>
            </x-filament::section>
        </div>
    </div>
</x-filament-panels::page>