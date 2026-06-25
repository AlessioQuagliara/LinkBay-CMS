<?php

declare(strict_types=1);

use App\Http\Controllers\AiCreditsController;
use App\Http\Controllers\CareersApiController;
use App\Http\Controllers\StorefrontFeaturesController;
use App\Http\Controllers\StripeWebhookController;
use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken;
use Illuminate\Support\Facades\Route;

// Stripe webhook — deve essere senza CSRF e auth
Route::post('/stripe/webhook', [StripeWebhookController::class, 'handle'])
    ->withoutMiddleware([VerifyCsrfToken::class])
    ->name('stripe.webhook');

// ── Storefront: public feature flags for a given tenant (Next.js SSR) ────────
Route::get('/storefront/{tenantId}/features', StorefrontFeaturesController::class)
    ->name('api.storefront.features');

// ── Careers: public published positions for Next.js ───────────────────────────
Route::get('/careers/positions', [CareersApiController::class, 'positions'])
    ->name('api.careers.positions');

// AI Credits public API
Route::prefix('ai-credits')->group(function () {
    Route::get('/packages', [AiCreditsController::class, 'packages']);
    Route::get('/success', [AiCreditsController::class, 'success'])->name('ai.credits.success');
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/checkout/{package}', [AiCreditsController::class, 'createCheckout']);
    });
});
