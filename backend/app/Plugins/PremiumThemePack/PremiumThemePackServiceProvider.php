<?php

declare(strict_types=1);

namespace App\Plugins\PremiumThemePack;

use App\Plugins\PluginRegistry;
use App\Plugins\ThemeDefinition;
use Illuminate\Support\ServiceProvider;

/**
 * Registers the Premium Theme Pack into the PluginRegistry.
 *
 * SKU breakdown (Fase 4C):
 *   FEATURE_CODE_EDITORIAL → Noir + Midnight — dark, editorial, luxury aesthetics.
 *   FEATURE_CODE_BUSINESS  → Atelier + Meridian — professional and creative business contexts.
 *
 * FEATURE_CODE_LEGACY ('theme_premium') is kept for backward compatibility:
 * FeatureAccessService expands legacy entitlements to grant both editorial and business access.
 *
 * Themes registered: noir, atelier, meridian.
 *
 * Loaded automatically by PluginServiceProvider.
 * To enable for an agency: Admin → Marketplace → Entitlements → grant the relevant code.
 */
class PremiumThemePackServiceProvider extends ServiceProvider
{
    public const FEATURE_CODE_EDITORIAL = 'theme_pack_editorial';

    public const FEATURE_CODE_BUSINESS = 'theme_pack_business';

    /** @deprecated use FEATURE_CODE_EDITORIAL or FEATURE_CODE_BUSINESS — kept for backward compat */
    public const FEATURE_CODE_LEGACY = 'theme_premium';

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
            // Dark editorial luxury — fashion, premium brands, cultural institutions
            new ThemeDefinition(
                key: 'noir',
                label: 'Noir',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#d4af37',
                        'secondary' => '#a89028',
                        'accent' => '#f5e6a3',
                        'surface' => '#0a0a0a',
                        'text' => '#f5f5f5',
                    ],
                    'typography' => ['heading_font' => 'playfair', 'body_font' => 'lato', 'scale' => 'lg'],
                    'radius' => 'none',
                    'spacing' => 'spacious',
                    'buttons' => 'sharp',
                    'section_style' => 'card',
                    'header_style' => 'centered',
                ],
                featureCode: self::FEATURE_CODE_EDITORIAL,
            ),

            // Warm artisanal refinement — creative studios, consultancies, craft brands
            new ThemeDefinition(
                key: 'atelier',
                label: 'Atelier',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#c4704f',
                        'secondary' => '#9a5240',
                        'accent' => '#e8a87c',
                        'surface' => '#fdf6f0',
                        'text' => '#2d1b0e',
                    ],
                    'typography' => ['heading_font' => 'merriweather', 'body_font' => 'source_sans', 'scale' => 'md'],
                    'radius' => 'lg',
                    'spacing' => 'comfortable',
                    'buttons' => 'rounded',
                    'section_style' => 'default',
                    'header_style' => 'split',
                ],
                featureCode: self::FEATURE_CODE_BUSINESS,
            ),

            // Precise corporate geometry — B2B SaaS, fintech, enterprise
            new ThemeDefinition(
                key: 'meridian',
                label: 'Meridian',
                isSystem: true,
                defaultConfig: [
                    'palette' => [
                        'primary' => '#1e3a5f',
                        'secondary' => '#152c4a',
                        'accent' => '#3b82f6',
                        'surface' => '#ffffff',
                        'text' => '#1e293b',
                    ],
                    'typography' => ['heading_font' => 'inter', 'body_font' => 'inter', 'scale' => 'md'],
                    'radius' => 'sm',
                    'spacing' => 'compact',
                    'buttons' => 'soft',
                    'section_style' => 'outlined',
                    'header_style' => 'minimal',
                ],
                featureCode: self::FEATURE_CODE_BUSINESS,
            ),
        ];
    }
}
