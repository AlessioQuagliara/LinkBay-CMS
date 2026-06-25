<?php

declare(strict_types=1);

namespace App\Plugins\CoreThemes;

use App\Plugins\PluginRegistry;
use App\Plugins\ThemeDefinition;
use Illuminate\Support\ServiceProvider;

/**
 * Registers the 3 built-in system themes into the PluginRegistry.
 *
 * Loaded automatically by PluginServiceProvider.
 * ThemePresetSeeder reads from the registry via ThemeConfigSchema::systemPresets()
 * and creates the corresponding DB records on deploy/seed.
 *
 * Theme keys registered: ocean, slate, sand (free), midnight (premium — requires theme_pack_editorial).
 * Design principle: B2B-sober, neutral, professional — no primary color clashes.
 */
class CoreThemesServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        $registry = $this->app->make(PluginRegistry::class);

        foreach ($this->themeDefinitions() as $definition) {
            $registry->registerTheme($definition->key, $definition);
        }
    }

    /** @return ThemeDefinition[] */
    private function themeDefinitions(): array
    {
        return [
            new ThemeDefinition(
                key: 'ocean',
                label: 'Ocean',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#0ea5e9',
                        'secondary' => '#0284c7',
                        'accent' => '#06b6d4',
                        'surface' => '#f0f9ff',
                        'text' => '#0c4a6e',
                    ],
                    'typography' => ['heading_font' => 'inter', 'body_font' => 'inter', 'scale' => 'md'],
                    'radius' => 'md',
                    'spacing' => 'comfortable',
                    'buttons' => 'soft',
                    'section_style' => 'card',
                    'header_style' => 'split',
                ],
            ),

            new ThemeDefinition(
                key: 'slate',
                label: 'Slate',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#475569',
                        'secondary' => '#334155',
                        'accent' => '#6366f1',
                        'surface' => '#f8fafc',
                        'text' => '#0f172a',
                    ],
                    'typography' => ['heading_font' => 'lato', 'body_font' => 'source_sans', 'scale' => 'md'],
                    'radius' => 'sm',
                    'spacing' => 'compact',
                    'buttons' => 'sharp',
                    'section_style' => 'outlined',
                    'header_style' => 'minimal',
                ],
            ),

            new ThemeDefinition(
                key: 'sand',
                label: 'Sand',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#a16207',
                        'secondary' => '#78350f',
                        'accent' => '#d97706',
                        'surface' => '#fefce8',
                        'text' => '#1c1917',
                    ],
                    'typography' => ['heading_font' => 'dm_serif', 'body_font' => 'lato', 'scale' => 'lg'],
                    'radius' => 'lg',
                    'spacing' => 'spacious',
                    'buttons' => 'rounded',
                    'section_style' => 'default',
                    'header_style' => 'centered',
                ],
            ),

            new ThemeDefinition(
                key: 'midnight',
                label: 'Midnight',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#818cf8',
                        'secondary' => '#6366f1',
                        'accent' => '#c084fc',
                        'surface' => '#0f172a',
                        'text' => '#e2e8f0',
                    ],
                    'typography' => ['heading_font' => 'dm_serif', 'body_font' => 'inter', 'scale' => 'lg'],
                    'radius' => 'full',
                    'spacing' => 'spacious',
                    'buttons' => 'pill',
                    'section_style' => 'card',
                    'header_style' => 'centered',
                ],
                featureCode: 'theme_pack_editorial',
            ),
        ];
    }
}
