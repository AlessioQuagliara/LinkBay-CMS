<?php

declare(strict_types=1);

namespace App\Services;

use App\Plugins\PluginRegistry;

/**
 * Single source of truth for the Theme Engine v1 config structure.
 *
 * Responsibilities:
 *  - Declare allowed values for every config key (whitelists).
 *  - Normalize/sanitize raw config arrays (unknown keys dropped, invalid enum values replaced with defaults).
 *  - Define the three built-in system presets (Ocean, Slate, Sand).
 *  - Provide flat-field helpers for the Filament form (pack/unpack between flat form data and nested config).
 *
 * Adding a new config key in v2:
 *  - Add it to defaults()
 *  - Add normalization logic in normalize()
 *  - Add pack/unpack in packFromForm() / flattenForForm()
 *  - Update formFieldNames()
 */
class ThemeConfigSchema
{
    // ── Option whitelists ─────────────────────────────────────────────────────

    public const HEADING_FONTS = [
        'inter' => 'Inter',
        'lato' => 'Lato',
        'playfair' => 'Playfair Display',
        'merriweather' => 'Merriweather',
        'dm_serif' => 'DM Serif Display',
    ];

    public const BODY_FONTS = [
        'inter' => 'Inter',
        'lato' => 'Lato',
        'source_sans' => 'Source Sans 3',
        'nunito' => 'Nunito',
    ];

    public const SCALE_OPTIONS = ['sm' => 'Piccolo', 'md' => 'Medio', 'lg' => 'Grande'];

    public const RADIUS_OPTIONS = [
        'none' => 'Nessuno',
        'sm' => 'Piccolo',
        'md' => 'Medio',
        'lg' => 'Grande',
        'full' => 'Pieno',
    ];

    public const SPACING_OPTIONS = [
        'compact' => 'Compatto',
        'comfortable' => 'Confortevole',
        'spacious' => 'Spazioso',
    ];

    public const BUTTON_OPTIONS = [
        'sharp' => 'Affilato',
        'soft' => 'Morbido',
        'rounded' => 'Arrotondato',
        'pill' => 'Pillola',
    ];

    public const SECTION_STYLES = [
        'default' => 'Default',
        'card' => 'Card',
        'outlined' => 'Outlined',
    ];

    public const HEADER_STYLES = [
        'minimal' => 'Minimale',
        'centered' => 'Centrato',
        'split' => 'Split',
    ];

    public const PALETTE_KEYS = ['primary', 'secondary', 'accent', 'surface', 'text'];

    // ── Defaults ──────────────────────────────────────────────────────────────

    public static function defaults(): array
    {
        return [
            'palette' => [
                'primary' => '#ff5758',
                'secondary' => '#1e293b',
                'accent' => '#f59e0b',
                'surface' => '#f8fafc',
                'text' => '#0f172a',
            ],
            'typography' => [
                'heading_font' => 'inter',
                'body_font' => 'inter',
                'scale' => 'md',
            ],
            'radius' => 'md',
            'spacing' => 'comfortable',
            'buttons' => 'soft',
            'section_style' => 'default',
            'header_style' => 'minimal',
        ];
    }

    // ── Normalization ─────────────────────────────────────────────────────────

    /**
     * Normalize and whitelist a raw config array.
     * Unknown keys are dropped. Invalid enum values fall back to defaults.
     * Hex colors must be #rrggbb format; others are replaced with the default.
     */
    public static function normalize(array $raw): array
    {
        $defaults = self::defaults();

        // Palette
        $palette = $defaults['palette'];
        foreach (self::PALETTE_KEYS as $key) {
            $value = $raw['palette'][$key] ?? null;
            if ($value !== null && preg_match('/^#[0-9a-fA-F]{6}$/', (string) $value)) {
                $palette[$key] = strtolower((string) $value);
            }
        }

        // Typography
        $typography = $defaults['typography'];
        $headingFont = $raw['typography']['heading_font'] ?? null;
        if ($headingFont !== null && array_key_exists($headingFont, self::HEADING_FONTS)) {
            $typography['heading_font'] = $headingFont;
        }
        $bodyFont = $raw['typography']['body_font'] ?? null;
        if ($bodyFont !== null && array_key_exists($bodyFont, self::BODY_FONTS)) {
            $typography['body_font'] = $bodyFont;
        }
        $scale = $raw['typography']['scale'] ?? null;
        if ($scale !== null && array_key_exists($scale, self::SCALE_OPTIONS)) {
            $typography['scale'] = $scale;
        }

        return [
            'palette' => $palette,
            'typography' => $typography,
            'radius' => array_key_exists($raw['radius'] ?? '', self::RADIUS_OPTIONS) ? $raw['radius'] : $defaults['radius'],
            'spacing' => array_key_exists($raw['spacing'] ?? '', self::SPACING_OPTIONS) ? $raw['spacing'] : $defaults['spacing'],
            'buttons' => array_key_exists($raw['buttons'] ?? '', self::BUTTON_OPTIONS) ? $raw['buttons'] : $defaults['buttons'],
            'section_style' => array_key_exists($raw['section_style'] ?? '', self::SECTION_STYLES) ? $raw['section_style'] : $defaults['section_style'],
            'header_style' => array_key_exists($raw['header_style'] ?? '', self::HEADER_STYLES) ? $raw['header_style'] : $defaults['header_style'],
        ];
    }

    // ── Filament form pack / unpack ───────────────────────────────────────────

    /**
     * Flat form field name prefix used to avoid collision with model attributes.
     */
    private const FIELD_PREFIX = 'cfg_';

    /**
     * All flat form field names produced by flattenForForm() / consumed by packFromForm().
     *
     * @return string[]
     */
    public static function formFieldNames(): array
    {
        $fields = [];
        foreach (self::PALETTE_KEYS as $key) {
            $fields[] = self::FIELD_PREFIX.'palette_'.$key;
        }
        $fields[] = self::FIELD_PREFIX.'typography_heading_font';
        $fields[] = self::FIELD_PREFIX.'typography_body_font';
        $fields[] = self::FIELD_PREFIX.'typography_scale';
        $fields[] = self::FIELD_PREFIX.'radius';
        $fields[] = self::FIELD_PREFIX.'spacing';
        $fields[] = self::FIELD_PREFIX.'buttons';
        $fields[] = self::FIELD_PREFIX.'section_style';
        $fields[] = self::FIELD_PREFIX.'header_style';

        return $fields;
    }

    /**
     * Unpack a nested config array into flat form fields.
     *
     * @param  array<string, mixed>  $config
     * @return array<string, mixed>
     */
    public static function flattenForForm(array $config): array
    {
        $defaults = self::defaults();
        $palette = array_merge($defaults['palette'], $config['palette'] ?? []);
        $typography = array_merge($defaults['typography'], $config['typography'] ?? []);

        $flat = [];
        foreach (self::PALETTE_KEYS as $key) {
            $flat[self::FIELD_PREFIX.'palette_'.$key] = $palette[$key] ?? $defaults['palette'][$key];
        }
        $flat[self::FIELD_PREFIX.'typography_heading_font'] = $typography['heading_font'] ?? $defaults['typography']['heading_font'];
        $flat[self::FIELD_PREFIX.'typography_body_font'] = $typography['body_font'] ?? $defaults['typography']['body_font'];
        $flat[self::FIELD_PREFIX.'typography_scale'] = $typography['scale'] ?? $defaults['typography']['scale'];
        $flat[self::FIELD_PREFIX.'radius'] = $config['radius'] ?? $defaults['radius'];
        $flat[self::FIELD_PREFIX.'spacing'] = $config['spacing'] ?? $defaults['spacing'];
        $flat[self::FIELD_PREFIX.'buttons'] = $config['buttons'] ?? $defaults['buttons'];
        $flat[self::FIELD_PREFIX.'section_style'] = $config['section_style'] ?? $defaults['section_style'];
        $flat[self::FIELD_PREFIX.'header_style'] = $config['header_style'] ?? $defaults['header_style'];

        return $flat;
    }

    /**
     * Pack flat form fields back into a nested config array.
     * Call normalize() on the result before persisting.
     *
     * @param  array<string, mixed>  $data
     * @return array<string, mixed>
     */
    public static function packFromForm(array $data): array
    {
        $p = self::FIELD_PREFIX;
        $palette = [];
        foreach (self::PALETTE_KEYS as $key) {
            $palette[$key] = $data["{$p}palette_{$key}"] ?? '';
        }

        return [
            'palette' => $palette,
            'typography' => [
                'heading_font' => $data["{$p}typography_heading_font"] ?? '',
                'body_font' => $data["{$p}typography_body_font"] ?? '',
                'scale' => $data["{$p}typography_scale"] ?? '',
            ],
            'radius' => $data["{$p}radius"] ?? '',
            'spacing' => $data["{$p}spacing"] ?? '',
            'buttons' => $data["{$p}buttons"] ?? '',
            'section_style' => $data["{$p}section_style"] ?? '',
            'header_style' => $data["{$p}header_style"] ?? '',
        ];
    }

    // ── System presets ────────────────────────────────────────────────────────

    /**
     * System presets sourced from the PluginRegistry.
     * Previously a static array; now delegated to CoreThemesServiceProvider
     * (and future premium theme pack providers).
     *
     * Returns only themes marked as is_system = true.
     * Keyed by slug — format is preserved for ThemePresetSeeder backwards compatibility.
     *
     * @return array<string, array{name: string, slug: string, config: array}>
     */
    public static function systemPresets(): array
    {
        $registry = app(PluginRegistry::class);
        $presets = [];

        foreach ($registry->themes() as $key => $definition) {
            if ($definition->isSystem) {
                $presets[$key] = $definition->toPresetSeedData();
            }
        }

        return $presets;
    }
}
