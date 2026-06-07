<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Models\Central\Agency;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Guards every agency-panel route: resolves the agency from the request
 * hostname and fails-closed (404) when no agency matches.
 *
 * This is the single authoritative source for the 'current_agency' container
 * binding during HTTP requests. All downstream code (panel branding, resources,
 * other middleware) reads app('current_agency') rather than doing their own
 * hostname lookups.
 */
class EnsureValidAgencyDomain
{
    public function handle(Request $request, Closure $next): Response
    {
        // Always resolve from the request host — this is the authoritative
        // source of the agency context for this request. Do NOT rely on a
        // previously-cached container binding; in persistent processes (Octane)
        // or tests the container outlives a single request.
        $agency = Agency::fromDomain($request->getHost());

        if (! $agency) {
            abort(404, 'No agency found for this domain.');
        }

        // Bind for the rest of this request's lifecycle.
        app()->instance('current_agency', $agency);

        return $next($request);
    }
}
