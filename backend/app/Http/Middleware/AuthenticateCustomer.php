<?php

declare(strict_types=1);

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AuthenticateCustomer
{
    public function handle(Request $request, Closure $next): Response
    {
        if (! auth('customer')->check()) {
            if ($request->expectsJson()) {
                return response()->json(['message' => 'Unauthenticated.'], 401);
            }

            return redirect('/account/login');
        }

        return $next($request);
    }
}
