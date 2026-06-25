<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\Central\Tenant;
use App\Plugins\PluginRegistry;
use App\Services\FeatureAccessService;
use Illuminate\Http\JsonResponse;

class StorefrontFeaturesController extends Controller
{
    public function __invoke(
        string $tenantId,
        FeatureAccessService $access,
        PluginRegistry $registry,
    ): JsonResponse {
        $tenant = Tenant::with('agency.plan')->find($tenantId);

        if (! $tenant) {
            return response()->json(['error' => 'tenant_not_found'], 404);
        }

        $agency = $tenant->agency;

        if (! $agency) {
            return response()->json(['error' => 'agency_not_found'], 404);
        }

        // Collect all unique feature codes declared in registered blocks and themes.
        // This list grows automatically as new packs are registered in the plugin system.
        $featureCodes = collect($registry->blocks())
            ->map(fn ($def) => $def->featureCode)
            ->merge(collect($registry->themes())->map(fn ($def) => $def->featureCode))
            ->filter()
            ->unique()
            ->sort()
            ->values();

        $features = $featureCodes->mapWithKeys(
            fn (string $code) => [$code => $access->canUseFeature($agency, $code)]
        );

        return response()->json([
            'features' => $features->isEmpty() ? new \stdClass : $features,
            'meta' => [
                'tenant_id' => $tenant->id,
                'agency_id' => $agency->id,
            ],
        ]);
    }
}
