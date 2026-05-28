<?php

declare(strict_types=1);

use App\Http\Controllers\AiCreditsController;
use App\Http\Controllers\StripeWebhookController;
use Illuminate\Support\Facades\Route;

// Stripe webhook — deve essere senza CSRF e auth
Route::post('/stripe/webhook', [StripeWebhookController::class, 'handle'])
    ->withoutMiddleware([\Illuminate\Foundation\Http\Middleware\VerifyCsrfToken::class])
    ->name('stripe.webhook');

// AI Credits public API
Route::prefix('ai-credits')->group(function () {
    Route::get('/packages', [AiCreditsController::class, 'packages']);
    Route::get('/success', [AiCreditsController::class, 'success'])->name('ai.credits.success');
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/checkout/{package}', [AiCreditsController::class, 'createCheckout']);
    });
});
