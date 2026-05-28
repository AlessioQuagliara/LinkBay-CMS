<?php

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\Setting;
use Filament\Forms;
use Filament\Forms\Concerns\InteractsWithForms;

use Filament\Notifications\Notification;
use Filament\Pages\Page;

class StoreSettings extends Page
{
    use InteractsWithForms;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-cog-6-tooth';
    protected static string|\UnitEnum|null $navigationGroup = 'Impostazioni';
    protected static ?string $navigationLabel = 'Impostazioni negozio';
    protected string $view = 'filament.tenant.pages.store-settings';

    public array $storeData = [];
    public array $seoData = [];
    public array $paymentData = [];

    public function mount(): void
    {
        $this->storeData = [
            'store_name' => Setting::get('store_name', ''),
            'currency' => Setting::get('currency', 'EUR'),
            'timezone' => Setting::get('timezone', 'Europe/Rome'),
            'admin_email' => Setting::get('admin_email', ''),
        ];
        $this->seoData = [
            'meta_title' => Setting::get('meta_title', ''),
            'meta_description' => Setting::get('meta_description', ''),
        ];
        $this->paymentData = [
            'stripe_key' => Setting::get('stripe_key', ''),
            'paypal_client_id' => Setting::get('paypal_client_id', ''),
        ];
    }

    public function saveStore(): void
    {
        foreach ($this->storeData as $key => $value) {
            Setting::set($key, $value);
        }
        Notification::make()->title('Impostazioni negozio salvate')->success()->send();
    }

    public function saveSeo(): void
    {
        foreach ($this->seoData as $key => $value) {
            Setting::set($key, $value, 'seo');
        }
        Notification::make()->title('Impostazioni SEO salvate')->success()->send();
    }

    public function savePayment(): void
    {
        foreach ($this->paymentData as $key => $value) {
            Setting::set($key, $value, 'payment');
        }
        Notification::make()->title('Impostazioni pagamenti salvate')->success()->send();
    }
}
