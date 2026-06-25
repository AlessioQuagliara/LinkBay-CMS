<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Plugins\PluginRegistry;

/**
 * Encapsulates the fork-with-lock logic for theme preset variants.
 *
 * A "fork" is an agency-owned ThemePreset that inherits all values from a parent system
 * theme and stores only the fields the agency has customized in override_config.
 *
 * Locked fields (section_style, header_style) define the structural personality of the
 * theme. Forks inherit them unconditionally and cannot override them, even if override_config
 * contains values for those keys.
 */
class ThemeForkResolver
{
    /**
     * Config keys that are locked to the parent theme's values in all forks.
     * Even if override_config contains these keys, they are silently ignored.
     */
    public const LOCKED_FIELDS = ['section_style', 'header_style'];

    /**
     * Top-level config keys that forks may customize.
     */
    public const OVERRIDABLE_KEYS = ['palette', 'typography', 'radius', 'spacing', 'buttons'];

    /**
     * Return true if the agency may create a fork of the given system theme.
     *
     * Free themes (featureCode = null) are always forkable.
     * Premium themes require the agency to hold the appropriate entitlement or plan.
     */
    public static function canFork(Agency $agency, string $systemThemeSlug): bool
    {
        $def = app(PluginRegistry::class)->getTheme($systemThemeSlug);

        if ($def === null) {
            return false;
        }

        if ($def->featureCode === null) {
            return true;
        }

        return app(FeatureAccessService::class)->canUseFeature($agency, $def->featureCode);
    }

    /**
     * Merge base config with the fork's override config.
     *
     * Only overridable fields are merged — locked fields always come from base.
     * Invalid values in overrides (bad hex, unknown enum) are silently ignored.
     *
     * @param  array<string, mixed>  $baseConfig  Normalized parent base config
     * @param  array<string, mixed>  $overrides  Only the fields the agency customized
     * @return array<string, mixed>
     */
    public static function applyOverrides(array $baseConfig, array $overrides): array
    {
        $result = $baseConfig;

        // Palette: per-key merge (valid hex values only)
        if (isset($overrides['palette'])) {
            foreach (ThemeConfigSchema::PALETTE_KEYS as $key) {
                $value = $overrides['palette'][$key] ?? null;
                if ($value !== null && preg_match('/^#[0-9a-fA-F]{6}$/', (string) $value)) {
                    $result['palette'][$key] = strtolower((string) $value);
                }
            }
        }

        // Typography: per-key merge with enum validation
        if (isset($overrides['typography'])) {
            $hFont = $overrides['typography']['heading_font'] ?? null;
            if ($hFont !== null && array_key_exists($hFont, ThemeConfigSchema::HEADING_FONTS)) {
                $result['typography']['heading_font'] = $hFont;
            }

            $bFont = $overrides['typography']['body_font'] ?? null;
            if ($bFont !== null && array_key_exists($bFont, ThemeConfigSchema::BODY_FONTS)) {
                $result['typography']['body_font'] = $bFont;
            }

            $scale = $overrides['typography']['scale'] ?? null;
            if ($scale !== null && array_key_exists($scale, ThemeConfigSchema::SCALE_OPTIONS)) {
                $result['typography']['scale'] = $scale;
            }
        }

        // Flat overridable enum keys
        if (isset($overrides['radius']) && array_key_exists($overrides['radius'], ThemeConfigSchema::RADIUS_OPTIONS)) {
            $result['radius'] = $overrides['radius'];
        }

        if (isset($overrides['spacing']) && array_key_exists($overrides['spacing'], ThemeConfigSchema::SPACING_OPTIONS)) {
            $result['spacing'] = $overrides['spacing'];
        }

        if (isset($overrides['buttons']) && array_key_exists($overrides['buttons'], ThemeConfigSchema::BUTTON_OPTIONS)) {
            $result['buttons'] = $overrides['buttons'];
        }

        // Locked fields always inherit from base — enforced even if overrides contain them
        $result['section_style'] = $baseConfig['section_style'];
        $result['header_style'] = $baseConfig['header_style'];

        return $result;
    }

    /**
     * Compute the minimal override_config by diffing the edited config against the parent base.
     * Only fields that actually differ from the parent are stored.
     * Locked fields are never written to override_config.
     *
     * @param  array<string, mixed>  $baseConfig  Normalized parent base config
     * @param  array<string, mixed>  $newConfig  Normalized config as submitted by the agency
     * @return array<string, mixed>
     */
    public static function computeOverrides(array $baseConfig, array $newConfig): array
    {
        $overrides = [];

        // Palette diff
        $paletteDiff = [];
        foreach (ThemeConfigSchema::PALETTE_KEYS as $key) {
            $newVal = strtolower($newConfig['palette'][$key] ?? '');
            $baseVal = strtolower($baseConfig['palette'][$key] ?? '');
            if ($newVal !== $baseVal && $newVal !== '') {
                $paletteDiff[$key] = $newVal;
            }
        }
        if (! empty($paletteDiff)) {
            $overrides['palette'] = $paletteDiff;
        }

        // Typography diff
        $typoDiff = [];
        foreach (['heading_font', 'body_font', 'scale'] as $key) {
            $newVal = $newConfig['typography'][$key] ?? '';
            $baseVal = $baseConfig['typography'][$key] ?? '';
            if ($newVal !== $baseVal && $newVal !== '') {
                $typoDiff[$key] = $newVal;
            }
        }
        if (! empty($typoDiff)) {
            $overrides['typography'] = $typoDiff;
        }

        // Flat overridable keys diff (locked fields excluded)
        foreach (['radius', 'spacing', 'buttons'] as $key) {
            $newVal = $newConfig[$key] ?? '';
            $baseVal = $baseConfig[$key] ?? '';
            if ($newVal !== $baseVal && $newVal !== '') {
                $overrides[$key] = $newVal;
            }
        }

        return $overrides;
    }
}
