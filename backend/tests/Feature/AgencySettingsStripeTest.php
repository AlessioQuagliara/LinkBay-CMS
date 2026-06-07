<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\AgencySettings;
use App\Models\Central\Agency;
use App\Services\StripeConnectService;
use Illuminate\Support\Facades\Log;
use Tests\CentralTestCase;

/**
 * Covers AgencySettings::getStripeConnectUrl() across all three relevant states:
 *
 *  - Agency already onboarded → returns null immediately, no service call.
 *  - Agency not onboarded and service succeeds → returns the onboarding URL.
 *  - Agency not onboarded and service throws → returns null, logs error with context.
 */
class AgencySettingsStripeTest extends CentralTestCase
{
    private function makeAgency(bool $onboarded = false): Agency
    {
        return Agency::create([
            'name' => 'Test Agency',
            'slug' => 'test-agency',
            'brand_name' => 'Test Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
            'stripe_connect_onboarded' => $onboarded,
        ]);
    }

    /** Build the page instance with the given agency bound in the container. */
    private function makePage(Agency $agency): AgencySettings
    {
        app()->instance('current_agency', $agency);

        return app(AgencySettings::class);
    }

    // ── Already onboarded ─────────────────────────────────────────────────────

    public function test_returns_null_when_agency_is_already_onboarded(): void
    {
        $agency = $this->makeAgency(onboarded: true);
        $page = $this->makePage($agency);

        $this->mock(StripeConnectService::class)
            ->shouldNotReceive('createOnboardingLink');

        $this->assertNull($page->getStripeConnectUrl());
    }

    // ── Not onboarded — service succeeds ─────────────────────────────────────

    public function test_returns_onboarding_url_when_service_succeeds(): void
    {
        $agency = $this->makeAgency(onboarded: false);
        $page = $this->makePage($agency);

        $this->mock(StripeConnectService::class)
            ->shouldReceive('createOnboardingLink')
            ->once()
            ->with($agency)
            ->andReturn('https://connect.stripe.com/setup/e/acct_test/xyz');

        $this->assertSame(
            'https://connect.stripe.com/setup/e/acct_test/xyz',
            $page->getStripeConnectUrl(),
        );
    }

    // ── Not onboarded — service throws ───────────────────────────────────────

    public function test_returns_null_and_logs_error_when_service_throws(): void
    {
        $agency = $this->makeAgency(onboarded: false);
        $page = $this->makePage($agency);

        $this->mock(StripeConnectService::class)
            ->shouldReceive('createOnboardingLink')
            ->once()
            ->andThrow(new \RuntimeException('No API key provided'));

        Log::shouldReceive('error')
            ->once()
            ->with(
                'StripeConnect onboarding link failed',
                \Mockery::on(fn (array $ctx) => $ctx['agency_id'] === $agency->id
                    && str_contains((string) $ctx['error'], 'No API key provided')
                ),
            );

        $this->assertNull($page->getStripeConnectUrl());
    }

    // ── No agency in context ──────────────────────────────────────────────────

    public function test_returns_null_when_no_agency_is_bound(): void
    {
        app()->instance('current_agency', null);
        $page = app(AgencySettings::class);

        $this->mock(StripeConnectService::class)
            ->shouldNotReceive('createOnboardingLink');

        $this->assertNull($page->getStripeConnectUrl());
    }
}
