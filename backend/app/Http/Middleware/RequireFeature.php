<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Exceptions\FeatureNotAvailableException;
use App\Models\Central\Agency;
use App\Services\FeatureService;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class RequireFeature
{
    public function __construct(private readonly FeatureService $features) {}

    public function handle(Request $request, Closure $next, string $feature): Response
    {
        $agency = $this->resolveAgency();

        if (! $agency) {
            return $next($request);
        }

        try {
            $this->features->enforce($agency, $feature);
        } catch (FeatureNotAvailableException $e) {
            if ($request->expectsJson() || $request->is('api/*') || $request->is('central/api/*')) {
                return response()->json([
                    'error' => 'feature_not_available',
                    'feature' => $feature,
                    'message' => $e->getMessage(),
                    'upgrade_url' => url('/pricing'),
                ], 403);
            }

            return redirect()->route('filament.agency.pages.agency-billing')
                ->with('upgrade_prompt', "Upgrade your plan to access {$feature}");
        }

        return $next($request);
    }

    private function resolveAgency(): ?Agency
    {
        // For tenant-panel routes, the agency comes from the tenant relation.
        try {
            if (tenancy()->initialized()) {
                return tenant()->agency;
            }
        } catch (\Throwable) {
        }

        // For agency-panel routes, EnsureValidAgencyDomain has already bound it.
        if (app()->bound('current_agency')) {
            $agency = app('current_agency');

            if ($agency instanceof Agency) {
                return $agency;
            }
        }

        return null;
    }
}
