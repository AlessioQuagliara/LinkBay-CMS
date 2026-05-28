<?php

declare(strict_types=1);

use App\Http\Controllers\Central\PlanController;
use App\Http\Controllers\Central\TenantController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::prefix('central/api')->middleware(['api', 'auth:sanctum'])->group(function () {

    // Tenants
    Route::get('/tenants', [TenantController::class, 'index']);
    Route::post('/tenants', [TenantController::class, 'store']);
    Route::get('/tenants/{id}', [TenantController::class, 'show']);
    Route::put('/tenants/{id}', [TenantController::class, 'update']);
    Route::delete('/tenants/{id}', [TenantController::class, 'destroy']);

    // Plans
    Route::get('/plans', [PlanController::class, 'index']);
    Route::post('/plans', [PlanController::class, 'store']);
    Route::get('/plans/{plan}', [PlanController::class, 'show']);
    Route::put('/plans/{plan}', [PlanController::class, 'update']);
    Route::delete('/plans/{plan}', [PlanController::class, 'destroy']);
});

// Stripe Connect redirect callbacks (no auth, web middleware)
Route::get('/agency/stripe/onboard/return', fn () => redirect()->route('filament.agency.pages.agency-settings')
    ->with('success', 'Account Stripe collegato con successo!')
)->name('agency.stripe.onboard.return');

Route::get('/agency/stripe/onboard/refresh', fn () => redirect()->route('filament.agency.pages.agency-settings')
    ->with('warning', 'Onboarding Stripe da completare.')
)->name('agency.stripe.onboard.refresh');
