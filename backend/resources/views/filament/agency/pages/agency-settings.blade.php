<x-filament-panels::page>
    <x-filament::tabs label="Impostazioni Agenzia">

        {{-- TAB BRAND --}}
        <x-filament::tabs.item label="Brand" icon="heroicon-o-paint-brush">
            @if($this->canAccessWhiteLabel())
                <form wire:submit="saveBrand" class="space-y-4 mt-4">
                    <x-filament::section>
                        <div class="grid grid-cols-2 gap-4">
                            <x-filament::input.wrapper label="Brand Name">
                                <x-filament::input type="text" wire:model="brandData.brand_name" />
                            </x-filament::input.wrapper>
                            <x-filament::input.wrapper label="Logo URL">
                                <x-filament::input type="url" wire:model="brandData.logo_url" />
                            </x-filament::input.wrapper>
                            <x-filament::input.wrapper label="Favicon URL">
                                <x-filament::input type="url" wire:model="brandData.favicon_url" />
                            </x-filament::input.wrapper>
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
                    </x-filament::section>
                    <x-filament::button type="submit">Salva brand</x-filament::button>
                </form>
            @else
                <x-filament::section class="mt-4 border-amber-400 bg-amber-50 dark:bg-amber-900/20">
                    <div class="flex items-center gap-3">
                        <x-heroicon-o-sparkles class="w-6 h-6 text-amber-500" />
                        <div>
                            <p class="font-medium">Upgrade to Pro to enable White-Label branding</p>
                            <p class="text-sm text-gray-500">Personalizza brand name, logo, colori e rimuovi il branding LinkBay.</p>
                            <a href="{{ route('filament.agency.pages.agency-billing') }}" class="text-sm font-medium underline text-amber-600">Vai ai piani →</a>
                        </div>
                    </div>
                </x-filament::section>
            @endif
        </x-filament::tabs.item>

        {{-- TAB DOMINIO --}}
        <x-filament::tabs.item label="Dominio Custom" icon="heroicon-o-globe-alt">
            @if($this->canAccessCustomDomain())
                <form wire:submit="saveDomain" class="space-y-4 mt-4">
                    <x-filament::section>
                        <x-filament::input.wrapper label="Dominio personalizzato">
                            <x-filament::input type="text" wire:model="domainData.custom_domain" placeholder="cms.miagenzia.it" />
                        </x-filament::input.wrapper>
                        <x-filament::section class="mt-4 bg-gray-50 dark:bg-gray-800">
                            <p class="text-sm font-mono">Aggiungi un CNAME dal tuo DNS:</p>
                            <p class="text-sm font-mono text-blue-600">cms.tuodominio.it → linkbay-cms.com</p>
                            <p class="text-xs text-gray-500 mt-1">La propagazione richiede fino a 48 ore.</p>
                        </x-filament::section>
                    </x-filament::section>
                    <x-filament::button type="submit">Salva dominio</x-filament::button>
                </form>
            @else
                <x-filament::section class="mt-4 border-amber-400 bg-amber-50 dark:bg-amber-900/20">
                    <p class="font-medium">Upgrade a Business per Custom Domain</p>
                    <p class="text-sm text-gray-500">Disponibile sul piano Business.</p>
                    <a href="{{ route('filament.agency.pages.agency-billing') }}" class="text-sm underline text-amber-600">Vai ai piani →</a>
                </x-filament::section>
            @endif
        </x-filament::tabs.item>

        {{-- TAB STRIPE CONNECT --}}
        <x-filament::tabs.item label="Stripe Connect" icon="heroicon-o-credit-card">
            <div class="mt-4">
                @if($this->stripeIsOnboarded())
                    <x-filament::section>
                        <div class="flex items-center gap-2">
                            <x-heroicon-o-check-circle class="w-6 h-6 text-green-500"/>
                            <span class="font-medium text-green-600">Account Stripe collegato</span>
                        </div>
                        <p class="text-sm text-gray-500 mt-2">Fee attuale: <strong>{{ $this->currentTransactionFee() }}</strong> per transazione</p>
                        <a href="https://dashboard.stripe.com" target="_blank" class="text-sm underline">Apri Stripe Dashboard →</a>
                    </x-filament::section>
                @else
                    <x-filament::section class="border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20">
                        <p class="font-medium">Collega il tuo account Stripe per ricevere pagamenti</p>
                        <p class="text-sm text-gray-500">LinkBay trattiene il {{ $this->currentTransactionFee() }} per transazione.</p>
                        @php $url = $this->getStripeConnectUrl(); @endphp
                        @if($url)
                            <a href="{{ $url }}" class="mt-3 inline-block">
                                <x-filament::button color="warning">Collega Stripe →</x-filament::button>
                            </a>
                        @else
                            <p class="text-xs text-red-500 mt-2">Configura STRIPE_SECRET nel file .env</p>
                        @endif
                    </x-filament::section>
                @endif
            </div>
        </x-filament::tabs.item>

    </x-filament::tabs>
</x-filament-panels::page>
