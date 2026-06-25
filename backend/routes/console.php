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

// Riprocessa billing_events bloccati — ogni 15 minuti
Schedule::command('billing:reprocess-stuck-events', ['--minutes=15'])
    ->everyFifteenMinutes()
    ->name('billing:reprocess-stuck-events')
    ->withoutOverlapping()
    ->runInBackground();

// Scade entitlements con ends_at passato — ogni ora
Schedule::command('entitlements:expire')
    ->hourly()
    ->name('entitlements:expire')
    ->withoutOverlapping();

// Valuta early warnings per tutte le agency — ogni giorno alle 07:00
Schedule::command('agency:health-alerts', ['--days' => 30])
    ->dailyAt('07:00')
    ->name('agency:health-alerts')
    ->withoutOverlapping()
    ->runInBackground();
