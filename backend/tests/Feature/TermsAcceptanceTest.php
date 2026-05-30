<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\Plan;
use App\Models\Central\TermsAcceptance;
use Tests\CentralTestCase;

class TermsAcceptanceTest extends CentralTestCase
{
    private Agency $agency;

    protected function setUp(): void
    {
        parent::setUp();

        $plan = Plan::create(['name' => 'Test', 'slug' => 'test', 'price' => 0, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 1]);

        $this->agency = Agency::create([
            'name'       => 'TestAg',
            'slug'       => 'test-ag',
            'brand_name' => 'TestAg',
            'plan_id'    => $plan->id,
            'billing_type' => 'monthly',
            'status'     => 'active',
        ]);
    }

    public function test_hasAccepted_returns_false_when_no_record(): void
    {
        $this->assertFalse(TermsAcceptance::hasAccepted($this->agency->id));
    }

    public function test_hasAccepted_returns_true_after_accept(): void
    {
        TermsAcceptance::create([
            'agency_id'     => $this->agency->id,
            'user_id'       => 1,
            'terms_version' => 'test-v1', // TERMS_VERSION da phpunit.xml
            'ip_address'    => '127.0.0.1',
            'accepted_at'   => now(),
        ]);

        $this->assertTrue(TermsAcceptance::hasAccepted($this->agency->id));
    }

    public function test_hasAccepted_returns_false_for_old_version(): void
    {
        // Accettazione con versione vecchia
        TermsAcceptance::create([
            'agency_id'     => $this->agency->id,
            'user_id'       => 1,
            'terms_version' => 'old-v0',
            'ip_address'    => '127.0.0.1',
            'accepted_at'   => now(),
        ]);

        // La versione corrente è 'test-v1' (da phpunit.xml env)
        $this->assertFalse(TermsAcceptance::hasAccepted($this->agency->id));
    }

    public function test_currentVersion_uses_config(): void
    {
        $this->assertEquals('test-v1', TermsAcceptance::currentVersion());
    }

    public function test_unique_constraint_prevents_duplicate_acceptance(): void
    {
        TermsAcceptance::create(['agency_id' => $this->agency->id, 'user_id' => 1, 'terms_version' => 'test-v1', 'ip_address' => '127.0.0.1', 'accepted_at' => now()]);

        $this->expectException(\Illuminate\Database\UniqueConstraintViolationException::class);

        TermsAcceptance::create(['agency_id' => $this->agency->id, 'user_id' => 2, 'terms_version' => 'test-v1', 'ip_address' => '127.0.0.2', 'accepted_at' => now()]);
    }
}
