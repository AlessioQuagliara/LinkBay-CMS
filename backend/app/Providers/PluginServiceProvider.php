<?php

declare(strict_types=1);

namespace App\Providers;

use App\Plugins\CoreBlocks\CoreBlocksServiceProvider;
use App\Plugins\CoreThemes\CoreThemesServiceProvider;
use App\Plugins\PluginRegistry;
use Illuminate\Support\ServiceProvider;

/**
 * Boots the Plugin System.
 *
 * Responsibilities:
 *  1. Bind PluginRegistry as a singleton in the container.
 *  2. Register all plugin service providers in dependency order.
 *
 * Adding a new internal plugin:
 *   Append its ServiceProvider class to $pluginProviders below.
 *   The registry will call registerBlock() or registerTheme() during boot.
 *
 * Adding a future premium plugin pack:
 *   Same pattern — create a ServiceProvider, append here.
 *   Licensing / feature-flag enforcement lives in the plugin provider itself.
 *
 * @var class-string<ServiceProvider>[] $pluginProviders
 */
class PluginServiceProvider extends ServiceProvider
{
    protected array $pluginProviders = [
        CoreBlocksServiceProvider::class,
        CoreThemesServiceProvider::class,
    ];

    public function register(): void
    {
        $this->app->singleton(PluginRegistry::class);

        foreach ($this->pluginProviders as $provider) {
            $this->app->register($provider);
        }
    }
}
