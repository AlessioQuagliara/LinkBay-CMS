<?php

declare(strict_types=1);

namespace App\Plugins;

use App\Plugins\Exceptions\DuplicatePluginKeyException;

/**
 * Central registry for all plugin-contributed blocks and themes.
 *
 * Bound as a singleton by PluginServiceProvider.
 * Populated during application boot by CoreBlocksServiceProvider and
 * CoreThemesServiceProvider (and future premium plugin providers).
 *
 * Rules:
 *  - Keys must be unique: duplicate registration throws DuplicatePluginKeyException.
 *  - No override or silent merge — conflicts must be fixed at the source.
 *  - No dynamic registration from the database or user-uploaded code.
 *  - Registration order is preserved (PHP array insertion order).
 *
 * Reading from the registry:
 *   app(PluginRegistry::class)->blocks()   → BlockDefinition[]
 *   app(PluginRegistry::class)->themes()   → ThemeDefinition[]
 *   app(PluginRegistry::class)->hasBlock('hero')  → bool
 *   app(PluginRegistry::class)->blockKeys() → string[]
 */
class PluginRegistry
{
    /** @var array<string, BlockDefinition> */
    private array $blocks = [];

    /** @var array<string, ThemeDefinition> */
    private array $themes = [];

    // ── Block registration ────────────────────────────────────────────────────

    /**
     * @throws DuplicatePluginKeyException if a block with this key is already registered
     */
    public function registerBlock(string $key, BlockDefinition $definition): void
    {
        if (isset($this->blocks[$key])) {
            throw DuplicatePluginKeyException::forBlock($key);
        }
        $this->blocks[$key] = $definition;
    }

    /** @return array<string, BlockDefinition> */
    public function blocks(): array
    {
        return $this->blocks;
    }

    public function hasBlock(string $key): bool
    {
        return isset($this->blocks[$key]);
    }

    public function getBlock(string $key): ?BlockDefinition
    {
        return $this->blocks[$key] ?? null;
    }

    /** @return string[] */
    public function blockKeys(): array
    {
        return array_keys($this->blocks);
    }

    // ── Theme registration ────────────────────────────────────────────────────

    /**
     * @throws DuplicatePluginKeyException if a theme with this key is already registered
     */
    public function registerTheme(string $key, ThemeDefinition $definition): void
    {
        if (isset($this->themes[$key])) {
            throw DuplicatePluginKeyException::forTheme($key);
        }
        $this->themes[$key] = $definition;
    }

    /** @return array<string, ThemeDefinition> */
    public function themes(): array
    {
        return $this->themes;
    }

    public function hasTheme(string $key): bool
    {
        return isset($this->themes[$key]);
    }

    public function getTheme(string $key): ?ThemeDefinition
    {
        return $this->themes[$key] ?? null;
    }

    /** @return string[] */
    public function themeKeys(): array
    {
        return array_keys($this->themes);
    }
}
