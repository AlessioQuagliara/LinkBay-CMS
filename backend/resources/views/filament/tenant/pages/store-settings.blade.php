<x-filament-panels::page>
    <x-filament::tabs label="Impostazioni">
        <x-filament::tabs.item label="Negozio" icon="heroicon-o-building-storefront">
            <form wire:submit="saveStore" class="space-y-4 mt-4">
                <x-filament::section>
                    <x-filament::input.wrapper label="Nome negozio">
                        <x-filament::input type="text" wire:model="storeData.store_name" />
                    </x-filament::input.wrapper>
                    <x-filament::input.wrapper label="Valuta">
                        <x-filament::input type="text" wire:model="storeData.currency" />
                    </x-filament::input.wrapper>
                    <x-filament::input.wrapper label="Fuso orario">
                        <x-filament::input type="text" wire:model="storeData.timezone" />
                    </x-filament::input.wrapper>
                    <x-filament::input.wrapper label="Email admin">
                        <x-filament::input type="email" wire:model="storeData.admin_email" />
                    </x-filament::input.wrapper>
                </x-filament::section>
                <x-filament::button type="submit">Salva</x-filament::button>
            </form>
        </x-filament::tabs.item>
        <x-filament::tabs.item label="SEO" icon="heroicon-o-magnifying-glass">
            <form wire:submit="saveSeo" class="space-y-4 mt-4">
                <x-filament::section>
                    <x-filament::input.wrapper label="Meta Title">
                        <x-filament::input type="text" wire:model="seoData.meta_title" />
                    </x-filament::input.wrapper>
                    <x-filament::input.wrapper label="Meta Description">
                        <x-filament::input type="text" wire:model="seoData.meta_description" />
                    </x-filament::input.wrapper>
                </x-filament::section>
                <x-filament::button type="submit">Salva</x-filament::button>
            </form>
        </x-filament::tabs.item>
        <x-filament::tabs.item label="Pagamenti" icon="heroicon-o-credit-card">
            <form wire:submit="savePayment" class="space-y-4 mt-4">
                <x-filament::section>
                    <x-filament::input.wrapper label="Stripe Public Key">
                        <x-filament::input type="password" wire:model="paymentData.stripe_key" />
                    </x-filament::input.wrapper>
                    <x-filament::input.wrapper label="PayPal Client ID">
                        <x-filament::input type="password" wire:model="paymentData.paypal_client_id" />
                    </x-filament::input.wrapper>
                </x-filament::section>
                <x-filament::button type="submit">Salva</x-filament::button>
            </form>
        </x-filament::tabs.item>
    </x-filament::tabs>
</x-filament-panels::page>
