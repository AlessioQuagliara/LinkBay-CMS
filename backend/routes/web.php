<?php

use App\Http\Controllers\Agency\RegisterController;
use Illuminate\Support\Facades\Route;

// ── Agency public registration (accessible on api.localhost) ──────────────────
Route::prefix('agency')->name('agency.')->group(function () {
    Route::get('/register', [RegisterController::class, 'show'])->name('register');
    Route::post('/register', [RegisterController::class, 'store'])->name('register.store');
});

// ── Default welcome (not used in production) ──────────────────────────────────
Route::get('/', function () {
    return redirect(config('app.frontend_url', 'http://localhost:3000'));
});
