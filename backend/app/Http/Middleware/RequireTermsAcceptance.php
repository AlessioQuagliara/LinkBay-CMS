<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Models\Central\Agency;
use App\Models\Central\TermsAcceptance;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class RequireTermsAcceptance
{
    public function handle(Request $request, Closure $next): Response
    {
        $agency = $this->resolveAgency();

        if (! $agency) {
            return $next($request);
        }

        $currentPath = $request->path();

        // Rotte sempre accessibili senza T&C accettati
        $bypassed = [
            'dashboard/terms-acceptance',
            'dashboard/logout',
            'dashboard/login',
        ];

        foreach ($bypassed as $prefix) {
            if (str_starts_with($currentPath, $prefix)) {
                return $next($request);
            }
        }

        $currentVersion = TermsAcceptance::currentVersion();

        // Fast-path: campo in-memory già aggiornato al momento dell'accettazione
        if ($agency->terms_accepted_version === $currentVersion) {
            return $next($request);
        }

        // DB check completo
        if (TermsAcceptance::hasAccepted($agency->id)) {
            $agency->terms_accepted_version = $currentVersion; // aggiorna in-memory

            return $next($request);
        }

        return redirect()->to('/dashboard/terms-acceptance');
    }

    private function resolveAgency(): ?Agency
    {
        // EnsureValidAgencyDomain (earlier in the middleware stack) is the
        // authoritative resolver and has already bound the agency instance.
        if (app()->bound('current_agency')) {
            $agency = app('current_agency');

            if ($agency instanceof Agency) {
                return $agency;
            }
        }

        return null;
    }
}
