<?php

use App\Services\AiCreditsService;
use App\Services\StripeConnectService;
use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Schedule;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

// Bonus mensile AI credits — 1° del mese alle 00:05
Schedule::call(fn () => app(AiCreditsService::class)->applyMonthlyBonus())
    ->monthlyOn(1, '00:05')
    ->name('ai-credits:monthly-bonus')
    ->withoutOverlapping();

// Sync onboarding Stripe Connect — ogni giorno
Schedule::call(fn () => app(StripeConnectService::class)->syncOnboardingStatus())
    ->daily()
    ->name('stripe:sync-onboarding')
    ->withoutOverlapping();
