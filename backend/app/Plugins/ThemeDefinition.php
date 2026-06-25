<?php

declare(strict_types=1);

namespace App\Plugins;

/**
 * Immutable descriptor for a theme preset.
 *
 * Pure data — no Filament dependency.
 * Carries the metadata and raw default config that will be normalized
 * by ThemeConfigSchema::normalize() before persisting.
 *
 * To register a new internal theme:
 *   $registry->registerTheme('midnight', new ThemeDefinition(
 *       key: 'midnight',
 *       label: 'Midnight',
 *       isSystem: true,
 *       defaultConfig: ['palette' => ['primary' => '#1e1b4b', ...], ...],
 *   ));
 */
class ThemeDefinition
{
    /**
     * @param  string  $key  Unique slug — must match the DB row slug if seeded
     * @param  string  $label  Human-readable name shown in the panel
     * @param  bool  $isSystem  True = system preset (visible to all agencies, read-only)
     * @param  array  $defaultConfig  Raw config array — normalized by ThemeConfigSchema::normalize()
     * @param  string|null  $featureCode  PluginCatalogItem code required to use this theme (null = free)
     */
    public function __construct(
        public readonly string $key,
        public readonly string $label,
        public readonly bool $isSystem = true,
        public readonly array $defaultConfig = [],
        public readonly ?string $featureCode = null,
    ) {}

    /**
     * Returns the data format expected by ThemePresetSeeder.
     *
     * @return array{name: string, slug: string, config: array}
     */
    public function toPresetSeedData(): array
    {
        return [
            'name' => $this->label,
            'slug' => $this->key,
            'config' => $this->defaultConfig,
        ];
    }
}
