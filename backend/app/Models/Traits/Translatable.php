<?php

declare(strict_types=1);

namespace App\Models\Traits;

use App\Models\Tenant\StoreLanguage;
use App\Models\Tenant\Translation;

trait Translatable
{
    public function translations()
    {
        return $this->morphMany(Translation::class, 'translatable');
    }

    public function translate(string $field, string $locale): ?string
    {
        return $this->translations
            ->where('field', $field)
            ->where('locale', $locale)
            ->value('value');
    }

    public function setTranslation(string $field, string $locale, string $value): void
    {
        $this->translations()->updateOrCreate(
            ['field' => $field, 'locale' => $locale],
            ['value' => $value]
        );

        // Refresh the loaded relation so subsequent translate() calls see the change
        $this->unsetRelation('translations');
    }

    public function getTranslation(string $field, ?string $locale = null): string
    {
        $locale ??= $this->resolveDefaultLocale();

        $value = $this->translate($field, $locale);
        if ($value !== null) {
            return $value;
        }

        // Fallback to default locale
        $defaultLocale = $this->resolveDefaultLocale();
        if ($defaultLocale !== $locale) {
            $value = $this->translate($field, $defaultLocale);
            if ($value !== null) {
                return $value;
            }
        }

        // Final fallback: the model's own field value
        return (string) ($this->{$field} ?? '');
    }

    private function resolveDefaultLocale(): string
    {
        try {
            $default = StoreLanguage::where('is_default', true)->first();

            return $default?->locale ?? config('app.locale', 'it');
        } catch (\Throwable) {
            return config('app.locale', 'it');
        }
    }
}
