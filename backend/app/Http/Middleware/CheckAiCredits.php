<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use App\Exceptions\InsufficientCreditsException;
use App\Models\Central\Agency;
use App\Services\AiCreditsService;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckAiCredits
{
    public function __construct(private readonly AiCreditsService $credits) {}

    public function handle(Request $request, Closure $next, int $required = 1): Response
    {
        $agency = $this->resolveAgency($request);

        if ($agency && !$this->credits->hasCredits($agency, $required)) {
            $balance = $this->credits->getBalance($agency);

            return response()->json([
                'error' => 'insufficient_credits',
                'balance' => $balance,
                'required' => $required,
                'purchase_url' => url('/credits/buy?agency=' . $agency->id),
            ], 402);
        }

        try {
            return $next($request);
        } catch (InsufficientCreditsException $e) {
            return response()->json([
                'error' => 'insufficient_credits',
                'balance' => $e->balance,
                'required' => $e->required,
                'purchase_url' => url('/credits/buy?agency=' . ($agency?->id ?? '')),
            ], 402);
        }
    }

    private function resolveAgency(Request $request): ?Agency
    {
        try {
            if (tenancy()->initialized()) {
                return tenant()->agency;
            }
        } catch (\Throwable) {}

        return $request->user()?->agency ?? null;
    }
}
