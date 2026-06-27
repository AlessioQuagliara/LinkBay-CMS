<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\StoreLanguage;
use App\Models\Tenant\Translation;
use Illuminate\Database\Eloquent\Model;

class TranslationService
{
    public function set(Model $model, string $field, string $locale, string $value): void
    {
        Translation::updateOrCreate(
            [
                'translatable_type' => $model->getMorphClass(),
                'translatable_id' => $model->getKey(),
                'locale' => $locale,
                'field' => $field,
            ],
            ['value' => $value]
        );
    }

    public function get(Model $model, string $field, string $locale, ?string $fallbackLocale = null): ?string
    {
        $value = Translation::where([
            'translatable_type' => $model->getMorphClass(),
            'translatable_id' => $model->getKey(),
            'locale' => $locale,
            'field' => $field,
        ])->value('value');

        if ($value !== null) {
            return $value;
        }

        if ($fallbackLocale && $fallbackLocale !== $locale) {
            return $this->get($model, $field, $fallbackLocale);
        }

        return null;
    }

    public function getAll(Model $model, string $field): array
    {
        return Translation::where([
            'translatable_type' => $model->getMorphClass(),
            'translatable_id' => $model->getKey(),
            'field' => $field,
        ])
            ->pluck('value', 'locale')
            ->all();
    }

    /** @param array<string, array<string, string>> $translations  format: ['field' => ['it' => '...', 'en' => '...']] */
    public function bulkSet(Model $model, array $translations): void
    {
        foreach ($translations as $field => $locales) {
            foreach ($locales as $locale => $value) {
                $this->set($model, $field, $locale, $value);
            }
        }
    }

    public function defaultLocale(): string
    {
        try {
            return StoreLanguage::where('is_default', true)->value('locale')
                ?? config('app.locale', 'it');
        } catch (\Throwable) {
            return config('app.locale', 'it');
        }
    }
}
