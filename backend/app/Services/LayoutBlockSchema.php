<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
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
     * Used by LayoutRendererService and admin tools where all blocks are needed.
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
     * Returns only the blocks accessible to the given agency.
     *
     * Free blocks (featureCode = null) are always included.
     * Premium blocks are included only when the agency holds an active entitlement
     * for the required feature code.
     *
     * Pass null to receive free blocks only (e.g. when no agency context is available).
     *
     * @return Block[]
     */
    public static function blocksForAgency(?Agency $agency): array
    {
        $registry = app(PluginRegistry::class);
        $accessService = $agency ? app(FeatureAccessService::class) : null;

        $allowed = array_filter(
            $registry->blocks(),
            static function (BlockDefinition $def) use ($agency, $accessService): bool {
                if ($def->featureCode === null) {
                    return true;
                }

                return $accessService !== null
                    && $accessService->canUseFeature($agency, $def->featureCode);
            }
        );

        return array_map(
            static fn (BlockDefinition $def) => $def->toFilamentBlock(),
            $allowed,
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

    /**
     * Checks whether the given blocks array contains premium blocks the agency
     * is not entitled to use.
     *
     * Returns null when the save is allowed.
     * Returns a human-readable error message when a violation is found.
     *
     * Called by CreateLayoutTemplate and EditLayoutTemplate before persisting.
     *
     * @param  array<int, array{type: string}>  $blocks
     */
    public static function premiumViolation(array $blocks, Agency $agency): ?string
    {
        $registry = app(PluginRegistry::class);
        $accessService = app(FeatureAccessService::class);

        foreach ($blocks as $block) {
            $type = $block['type'] ?? '';
            $def = $registry->getBlock($type);

            if ($def === null || $def->featureCode === null) {
                continue;
            }

            if (! $accessService->canUseFeature($agency, $def->featureCode)) {
                return "Il blocco \"{$def->label}\" richiede il pack \"{$def->featureCode}\", non attivo per questa agency.";
            }
        }

        return null;
    }
}
