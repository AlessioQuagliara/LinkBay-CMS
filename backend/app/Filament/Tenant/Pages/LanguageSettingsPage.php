<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\StoreLanguage;
use Filament\Notifications\Notification;
use Filament\Pages\Page;

class LanguageSettingsPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-language';

    protected static string|\UnitEnum|null $navigationGroup = 'Impostazioni';

    protected static ?string $navigationLabel = 'Lingue';

    protected static ?int $navigationSort = 21;

    protected string $view = 'filament.tenant.pages.language-settings';

    public array $languages = [];

    public string $newLocale = '';

    public bool $newIsActive = true;

    public static function availableLocales(): array
    {
        return [
            'it' => 'Italiano',
            'en' => 'English',
            'fr' => 'Français',
            'de' => 'Deutsch',
            'es' => 'Español',
            'pt' => 'Português',
            'nl' => 'Nederlands',
            'pl' => 'Polski',
            'ru' => 'Русский',
            'zh' => '中文',
            'ja' => '日本語',
            'ar' => 'العربية',
        ];
    }

    public function mount(): void
    {
        $this->refreshLanguages();
    }

    public function addLanguage(): void
    {
        $this->validate([
            'newLocale' => 'required|string|max:10',
        ]);

        $tenantId = $this->resolveTenantId();

        if (StoreLanguage::where('tenant_id', $tenantId)->where('locale', $this->newLocale)->exists()) {
            Notification::make()->title('Lingua già presente')->warning()->send();

            return;
        }

        $isFirst = ! StoreLanguage::where('tenant_id', $tenantId)->exists();

        StoreLanguage::create([
            'tenant_id' => $tenantId,
            'locale' => $this->newLocale,
            'is_default' => $isFirst,
            'is_active' => $this->newIsActive,
        ]);

        $this->newLocale = '';
        $this->newIsActive = true;
        $this->refreshLanguages();

        Notification::make()->title('Lingua aggiunta')->success()->send();
    }

    public function setDefault(int $id): void
    {
        $tenantId = $this->resolveTenantId();

        StoreLanguage::where('tenant_id', $tenantId)->update(['is_default' => false]);
        StoreLanguage::where('id', $id)->update(['is_default' => true]);

        $this->refreshLanguages();
        Notification::make()->title('Lingua predefinita aggiornata')->success()->send();
    }

    public function toggleActive(int $id): void
    {
        $lang = StoreLanguage::findOrFail($id);

        if ($lang->is_default && $lang->is_active) {
            Notification::make()
                ->title('Non puoi disattivare la lingua predefinita')
                ->warning()
                ->send();

            return;
        }

        $lang->update(['is_active' => ! $lang->is_active]);
        $this->refreshLanguages();
    }

    public function removeLanguage(int $id): void
    {
        $lang = StoreLanguage::findOrFail($id);

        if ($lang->is_default) {
            Notification::make()->title('Non puoi eliminare la lingua predefinita')->danger()->send();

            return;
        }

        $lang->delete();
        $this->refreshLanguages();
        Notification::make()->title('Lingua rimossa')->success()->send();
    }

    private function refreshLanguages(): void
    {
        $this->languages = StoreLanguage::where('tenant_id', $this->resolveTenantId())
            ->orderByDesc('is_default')
            ->orderBy('locale')
            ->get()
            ->toArray();
    }

    private function resolveTenantId(): string
    {
        try {
            if (function_exists('tenancy') && tenancy()->initialized) {
                return (string) tenant()->id;
            }
        } catch (\Throwable) {
        }

        return 'default';
    }
}
