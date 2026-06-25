<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Central\PluginCatalogItem;
use App\Plugins\PluginRegistry;
use Illuminate\Database\Seeder;

class PluginCatalogItemSeeder extends Seeder
{
    public function run(): void
    {
        $registry = app(PluginRegistry::class);

        $items = collect();

        foreach ($registry->blocks() as $def) {
            if ($def->featureCode !== null) {
                $items->put($def->featureCode, PluginCatalogItem::TYPE_BLOCK_PACK);
            }
        }

        foreach ($registry->themes() as $def) {
            if ($def->featureCode !== null && ! $items->has($def->featureCode)) {
                $items->put($def->featureCode, PluginCatalogItem::TYPE_THEME_PACK);
            }
        }

        $synced = 0;

        foreach ($items as $code => $type) {
            PluginCatalogItem::updateOrCreate(
                ['code' => $code, 'is_system' => true],
                [
                    'type' => $type,
                    'name' => ucwords(str_replace('_', ' ', $code)),
                    'status' => PluginCatalogItem::STATUS_ACTIVE,
                    'is_system' => true,
                ],
            );

            $synced++;
        }

        $this->command->info("PluginCatalogItemSeeder: {$synced} system item(s) sincronizzati dal registro plugin.");
    }
}
