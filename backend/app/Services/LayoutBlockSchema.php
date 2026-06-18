<?php

declare(strict_types=1);

namespace App\Services;

use App\Plugins\BlockDefinition;
use App\Plugins\PluginRegistry;
use Filament\Forms\Components\Builder\Block;

/**
 * Registry adapter: bridges PluginRegistry and the Filament Builder component.
 *
 * Callers (LayoutTemplateResource, LayoutRendererService) import this class
 * and call the same static API they always have. The block definitions now live
 * in CoreBlocksServiceProvider (and future premium block pack providers) rather
 * than being hardcoded here.
 *
 * Adding a new block:
 *  1. Create a BlockDefinition in a ServiceProvider's boot() method.
 *  2. Call $registry->registerBlock($key, $definition).
 *  3. No changes needed here.
 */
class LayoutBlockSchema
{
    /**
     * Returns all registered blocks as Filament Builder Block objects.
     * Used by LayoutTemplateResource to populate the Builder component.
     *
     * @return Block[]
     */
    public static function blocks(): array
    {
        return array_map(
            static fn (BlockDefinition $def) => $def->toFilamentBlock(),
            app(PluginRegistry::class)->blocks(),
        );
    }

    /**
     * Returns the keys of all registered block types.
     * Used by LayoutRendererService as the whitelist for storefront rendering.
     *
     * @return string[]
     */
    public static function knownTypes(): array
    {
        return app(PluginRegistry::class)->blockKeys();
    }
}
