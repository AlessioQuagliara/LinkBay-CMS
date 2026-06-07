<?php

use App\Http\Controllers\Agency\RegisterController;
use App\Http\Controllers\AgencyMemberInviteController;
use App\Http\Controllers\CareersController;
use App\Http\Controllers\ClientInviteController;
use App\Http\Controllers\ContactController;
use Illuminate\Support\Facades\Route;

// ── Agency public registration (accessible on api.localhost) ──────────────────
Route::prefix('agency')->name('agency.')->group(function () {
    Route::get('/register', [RegisterController::class, 'show'])->name('register');
    Route::post('/register', [RegisterController::class, 'store'])->name('register.store');
    Route::get('/find', function () {
        return view('agency.auth.find');
    })->name('find');
});

// ── Contact form ──────────────────────────────────────────────────────────────
Route::get('/contact', [ContactController::class, 'show'])->name('contact.show');
Route::post('/contact', [ContactController::class, 'store'])->name('contact.store');
Route::get('/contact/success', [ContactController::class, 'success'])->name('contact.success');

// ── Careers: public job application form ──────────────────────────────────────
Route::prefix('careers')->name('careers.')->group(function () {
    Route::get('/apply/{job:slug}', [CareersController::class, 'apply'])->name('apply');
    Route::post('/apply/{job:slug}', [CareersController::class, 'submit'])->name('submit');
    Route::get('/apply/{slug}/success', [CareersController::class, 'success'])->name('success');
});

// ── Admin: protected CV download ───────────────────────────────────────────────
Route::middleware('auth')
    ->get('/admin/careers/applications/{application}/cv', [CareersController::class, 'downloadCv'])
    ->name('admin.careers.cv.download');

// ── Agency member invite (team invitations) ───────────────────────────────────
Route::prefix('agency-invite')->name('agency-invite.')->group(function () {
    Route::get('/accepted', [AgencyMemberInviteController::class, 'accepted'])->name('accepted');
    Route::get('/invalid', [AgencyMemberInviteController::class, 'invalid'])->name('invalid');
    Route::get('/{token}', [AgencyMemberInviteController::class, 'show'])->name('show');
    Route::post('/{token}', [AgencyMemberInviteController::class, 'accept'])->name('accept');
});

// ── Client invite (agency → client store access) ──────────────────────────────
Route::prefix('client-invite')->name('client-invite.')->group(function () {
    Route::get('/accepted', [ClientInviteController::class, 'accepted'])->name('accepted');
    Route::get('/invalid', [ClientInviteController::class, 'invalid'])->name('invalid');
    Route::get('/{token}', [ClientInviteController::class, 'show'])->name('show');
    Route::post('/{token}', [ClientInviteController::class, 'accept'])->name('accept');
});

// ── Default welcome (not used in production) ──────────────────────────────────
Route::get('/', function () {
    return redirect(config('app.frontend_url', 'http://localhost:3000'));
});
