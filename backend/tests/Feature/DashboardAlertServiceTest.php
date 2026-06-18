<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\AgencySubscription;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\Plan;
use App\Models\Central\TermsAcceptance;
use App\Models\Central\User;
use App\Services\DashboardAlertService;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Covers DashboardAlertService alert resolution logic end-to-end.
 *
 * Tests:
 *  1.  Past-due subscription → subscription_past_due danger alert
 *  2.  Cancelled subscription → subscription_cancelled danger alert
 *  3.  Active subscription → no billing alert
 *  4.  Stripe not configured → stripe_not_configured warning
 *  5.  Stripe account exists but not onboarded → stripe_not_onboarded warning
 *  6.  Stripe fully configured → no stripe alert
 *  7.  stripe_not_configured takes priority over stripe_not_onboarded (mutually exclusive)
 *  8.  AI credits ≤ threshold → ai_credits_low warning
 *  9.  AI credits above threshold → no AI credits alert
 * 10.  Terms not accepted → terms_pending info alert
 * 11.  Terms accepted → no terms alert
 * 12.  No stores + has plan → no_stores info alert
 * 13.  No stores + no plan → no alert (PlanUpsellWidget handles this)
 * 14.  Active stores present → no no_stores alert
 * 15.  Multiple alerts are ordered by priority (lower number first)
 * 16.  Regular member sees no alerts
 * 17.  Null member sees no alerts
 * 18.  Admin sees billing alert but ctaOwnerOnly is flagged
 * 19.  Lifetime subscription cancelled state does not trigger billing alert
 */
class DashboardAlertServiceTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null, array $overrides = []): Agency
    {
        self::$seq++;

        return Agency::create(array_merge([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ], $overrides));
    }

    private function makePlan(): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 29,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
        ]);
    }

    private function makeUser(Agency $agency, string $role): User
    {
        self::$seq++;

        $user = User::create([
            'name' => 'User '.self::$seq,
            'email' => 'user'.self::$seq.'@test.com',
            'password' => bcrypt('password'),
        ]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    private function makeMember(Agency $agency, string $role): AgencyMember
    {
        $this->makeUser($agency, $role);

        return AgencyMember::where('agency_id', $agency->id)
            ->where('role', $role)
            ->latest()
            ->first();
    }

    private function makeSubscription(Agency $agency, string $status, string $billingType = 'monthly'): AgencySubscription
    {
        return AgencySubscription::create([
            'agency_id' => $agency->id,
            'status' => $status,
            'billing_type' => $billingType,
        ]);
    }

    /**
     * Add AI credit balance directly via the ledger, bypassing the service.
     */
    private function addCredits(Agency $agency, int $amount): void
    {
        AiCreditLedger::create([
            'agency_id' => $agency->id,
            'amount' => $amount,
            'balance_after' => $amount,
            'type' => AiCreditLedger::TYPE_BONUS,
            'description' => 'Test credits',
            'created_at' => now(),
        ]);
    }

    /**
     * Insert a tenant row directly to avoid stancl/tenancy DB-provisioning hooks.
     */
    private function addStore(Agency $agency): void
    {
        self::$seq++;
        DB::connection('central')->table('tenants')->insert([
            'id' => 'test-store-'.self::$seq,
            'name' => 'Test Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }

    private function acceptTerms(Agency $agency): void
    {
        TermsAcceptance::create([
            'agency_id' => $agency->id,
            'user_id' => 1,
            'terms_version' => TermsAcceptance::currentVersion(),
            'ip_address' => '127.0.0.1',
            'accepted_at' => now(),
        ]);
    }

    private function service(): DashboardAlertService
    {
        return app(DashboardAlertService::class);
    }

    // ── Subscription alerts ───────────────────────────────────────────────────

    public function test_past_due_subscription_shows_danger_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->makeSubscription($agency, 'past_due');

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'subscription_past_due'));
        $this->assertEquals('danger', $alerts->firstWhere('key', 'subscription_past_due')->severity);
    }

    public function test_cancelled_subscription_shows_danger_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->makeSubscription($agency, 'canceled');

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'subscription_cancelled'));
        $this->assertEquals('danger', $alerts->firstWhere('key', 'subscription_cancelled')->severity);
    }

    public function test_active_subscription_shows_no_billing_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->makeSubscription($agency, 'active');
        $this->acceptTerms($agency);

        // Stripe fully configured so stripe alerts don't interfere
        $agency->update(['stripe_connect_account_id' => 'acct_ok', 'stripe_connect_onboarded' => true]);
        $this->addCredits($agency, 500);
        $this->addStore($agency);

        $alerts = $this->service()->resolve($agency, $member);

        $billingKeys = ['subscription_past_due', 'subscription_cancelled'];
        $this->assertEmpty($alerts->whereIn('key', $billingKeys));
    }

    public function test_lifetime_subscription_cancelled_does_not_trigger_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        // Lifetime billing type — status canceled does not mean the service ends
        $this->makeSubscription($agency, 'canceled', 'lifetime');

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'subscription_cancelled'));
    }

    // ── Stripe Connect alerts ─────────────────────────────────────────────────

    public function test_stripe_not_configured_shows_warning(): void
    {
        $agency = $this->makeAgency(null, ['stripe_connect_account_id' => null]);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'stripe_not_configured'));
        $this->assertEquals('warning', $alerts->firstWhere('key', 'stripe_not_configured')->severity);
    }

    public function test_stripe_not_onboarded_shows_warning(): void
    {
        $agency = $this->makeAgency(null, [
            'stripe_connect_account_id' => 'acct_partial',
            'stripe_connect_onboarded' => false,
        ]);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'stripe_not_onboarded'));
        $this->assertEmpty($alerts->where('key', 'stripe_not_configured'));
    }

    public function test_stripe_fully_configured_shows_no_stripe_alert(): void
    {
        $agency = $this->makeAgency(null, [
            'stripe_connect_account_id' => 'acct_ok',
            'stripe_connect_onboarded' => true,
        ]);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->acceptTerms($agency);
        $this->addCredits($agency, 500);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'stripe_not_configured'));
        $this->assertEmpty($alerts->where('key', 'stripe_not_onboarded'));
    }

    public function test_stripe_not_configured_is_mutually_exclusive_with_not_onboarded(): void
    {
        // When no account at all, only stripe_not_configured should appear (not both)
        $agency = $this->makeAgency(null, ['stripe_connect_account_id' => null]);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'stripe_not_onboarded'),
            'stripe_not_onboarded must not appear when there is no account at all');
    }

    // ── AI credits alerts ─────────────────────────────────────────────────────

    public function test_low_ai_credits_shows_warning(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        // No credits added → balance = 0, which is ≤ threshold (100)

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'ai_credits_low'));
        $this->assertEquals('warning', $alerts->firstWhere('key', 'ai_credits_low')->severity);
    }

    public function test_ai_credits_exactly_at_threshold_shows_warning(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->addCredits($agency, DashboardAlertService::LOW_CREDITS_THRESHOLD);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'ai_credits_low'));
    }

    public function test_sufficient_ai_credits_shows_no_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->addCredits($agency, DashboardAlertService::LOW_CREDITS_THRESHOLD + 1);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'ai_credits_low'));
    }

    // ── Terms acceptance alerts ───────────────────────────────────────────────

    public function test_terms_not_accepted_shows_info_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        // No TermsAcceptance record created → hasAccepted() returns false

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'terms_pending'));
        $this->assertEquals('info', $alerts->firstWhere('key', 'terms_pending')->severity);
    }

    public function test_terms_accepted_shows_no_alert(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->acceptTerms($agency);
        $this->addCredits($agency, 500);
        $agency->update(['stripe_connect_account_id' => 'acct_ok', 'stripe_connect_onboarded' => true]);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'terms_pending'));
    }

    // ── No stores alerts ──────────────────────────────────────────────────────

    public function test_no_stores_with_plan_shows_info_alert(): void
    {
        $plan = $this->makePlan();
        $agency = $this->makeAgency($plan);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(1, $alerts->where('key', 'no_stores'));
        $this->assertEquals('info', $alerts->firstWhere('key', 'no_stores')->severity);
    }

    public function test_no_stores_without_plan_shows_no_alert(): void
    {
        $agency = $this->makeAgency(); // plan_id = null
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'no_stores'));
    }

    public function test_active_stores_resolves_no_stores_alert(): void
    {
        $plan = $this->makePlan();
        $agency = $this->makeAgency($plan);
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);
        $this->addStore($agency);

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertEmpty($alerts->where('key', 'no_stores'));
    }

    // ── Ordering ──────────────────────────────────────────────────────────────

    public function test_multiple_alerts_are_ordered_by_priority(): void
    {
        $agency = $this->makeAgency(); // no plan → no no_stores, stripe alert will appear
        $member = $this->makeMember($agency, AgencyMember::ROLE_OWNER);

        // Create subscription in past_due state (priority 10)
        $this->makeSubscription($agency, 'past_due');
        // Stripe not configured (priority 20)
        // AI credits low (priority 30) — balance = 0 by default
        // Terms not accepted (priority 40) — no TermsAcceptance record

        $alerts = $this->service()->resolve($agency, $member);

        $priorities = $alerts->pluck('priority')->toArray();
        $sorted = $priorities;
        sort($sorted);

        $this->assertEquals($sorted, $priorities, 'Alerts must be in ascending priority order');
        $this->assertEquals('subscription_past_due', $alerts->first()->key,
            'Most urgent alert must appear first');
    }

    // ── Access control ────────────────────────────────────────────────────────

    public function test_member_sees_no_alerts(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_MEMBER);

        $this->makeSubscription($agency, 'past_due');

        $alerts = $this->service()->resolve($agency, $member);

        $this->assertCount(0, $alerts);
    }

    public function test_null_member_sees_no_alerts(): void
    {
        $agency = $this->makeAgency();
        $this->makeSubscription($agency, 'past_due');

        $alerts = $this->service()->resolve($agency, null);

        $this->assertCount(0, $alerts);
    }

    public function test_admin_sees_billing_alert_with_cta_owner_only_flag(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_ADMIN);
        $this->makeSubscription($agency, 'past_due');

        $alerts = $this->service()->resolve($agency, $member);

        $billingAlert = $alerts->firstWhere('key', 'subscription_past_due');
        $this->assertNotNull($billingAlert, 'Admin must still see the billing alert');
        $this->assertTrue($billingAlert->ctaOwnerOnly,
            'Billing alert CTA must be flagged owner-only so the view shows "contact owner" for admins');
    }

    public function test_admin_sees_stripe_alert_with_usable_cta(): void
    {
        // AgencySettings is accessible to owner+admin, so no ctaOwnerOnly flag
        $agency = $this->makeAgency(null, ['stripe_connect_account_id' => null]);
        $member = $this->makeMember($agency, AgencyMember::ROLE_ADMIN);

        $alerts = $this->service()->resolve($agency, $member);

        $stripeAlert = $alerts->firstWhere('key', 'stripe_not_configured');
        $this->assertNotNull($stripeAlert);
        $this->assertFalse($stripeAlert->ctaOwnerOnly,
            'Stripe settings CTA must be usable by admins (not owner-only)');
    }
}
