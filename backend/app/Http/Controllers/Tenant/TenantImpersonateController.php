<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class TenantImpersonateController extends Controller
{
    /**
     * Generate a one-time impersonation token (5-minute TTL) and store it in cache.
     * Returns the token string so the caller can build the redirect URL.
     */
    public static function generateToken(string $agentEmail, string $tenantId): string
    {
        $token = Str::uuid()->toString();

        Cache::put('impersonate:'.$token, [
            'email' => $agentEmail,
            'tenant_id' => $tenantId,
        ], now()->addMinutes(5));

        return $token;
    }

    /**
     * Validate the impersonation token, authenticate the agency agent as a
     * Tenant\User, and redirect to the Tenant panel dashboard.
     */
    public function handle(string $token): RedirectResponse
    {
        $payload = Cache::pull('impersonate:'.$token);

        if (! $payload || ! isset($payload['email'])) {
            abort(403, 'Token di impersonazione non valido o scaduto.');
        }

        $user = User::firstOrCreate(
            ['email' => $payload['email']],
            [
                'name' => Str::before($payload['email'], '@'),
                'password' => Hash::make(Str::random(32)),
                'role' => User::ROLE_OWNER,
            ]
        );

        Auth::guard('tenant_web')->login($user);

        session()->regenerate();

        return redirect('/admin');
    }
}
