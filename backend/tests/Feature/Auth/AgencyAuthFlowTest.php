<?php

declare(strict_types=1);

namespace Tests\Feature\Auth;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\Plan;
use App\Models\Central\User as CentralUser;
use App\Models\Tenant\User as TenantUser;
use Filament\Panel;
use Tests\CentralTestCase;

/**
 * Covers the critical auth-flow scenarios:
 *
 *  - Super admin login works without tenant context
 *  - Agency user login works only on the correct agency domain
 *  - Agency user fails cleanly on wrong domain
 *  - current_agency is never null on a successful agency-panel access
 *  - app.* central domain does not allow agency-panel access
 *  - Tenant user cannot access the agency panel
 *  - Agency::fromDomain() resolves correctly and rejects invalid suffixes
 */
class AgencyAuthFlowTest extends CentralTestCase
{
    private Plan $plan;

    protected function setUp(): void
    {
        parent::setUp();

        $this->plan = Plan::create([
            'name' => 'Test Plan',
            'slug' => 'test',
            'price' => 0,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => 1,
        ]);
    }

    // ── Agency::fromDomain() ──────────────────────────────────────────────────

    public function test_from_domain_resolves_by_custom_domain(): void
    {
        $agency = $this->makeAgency('acme', customDomain: 'acme.myshop.com');

        $found = Agency::fromDomain('acme.myshop.com');

        $this->assertNotNull($found);
        $this->assertSame($agency->id, $found->id);
    }

    public function test_from_domain_resolves_by_slug_on_central_subdomain(): void
    {
        $agency = $this->makeAgency('acme');

        $centralDomain = config('app.central_domain', 'linkbay-cms.test');
        $found = Agency::fromDomain('acme.'.$centralDomain);

        $this->assertNotNull($found);
        $this->assertSame($agency->id, $found->id);
    }

    public function test_from_domain_returns_null_for_unknown_domain(): void
    {
        $this->makeAgency('acme');

        $found = Agency::fromDomain('nobody.linkbay-cms.test');

        $this->assertNull($found);
    }

    public function test_from_domain_does_not_match_slug_on_wrong_tld(): void
    {
        $this->makeAgency('acme');

        // 'acme' is a valid slug but acme.attacker.com must NOT match it
        $found = Agency::fromDomain('acme.attacker.com');

        $this->assertNull($found);
    }

    public function test_from_domain_does_not_match_multi_level_subdomain(): void
    {
        $this->makeAgency('acme');

        $centralDomain = config('app.central_domain', 'linkbay-cms.test');
        // deep.acme.linkbay-cms.test must not resolve to the 'acme' agency
        $found = Agency::fromDomain('deep.acme.'.$centralDomain);

        $this->assertNull($found);
    }

    // ── Central\User::canAccessPanel ─────────────────────────────────────────

    public function test_super_admin_can_access_admin_panel_without_agency_context(): void
    {
        $admin = $this->makeSuperAdmin();
        $panel = $this->makePanelStub('admin');

        $this->assertTrue($admin->canAccessPanel($panel));
    }

    public function test_super_admin_can_still_access_agency_panel_for_support(): void
    {
        $admin = $this->makeSuperAdmin();

        // Even with no agency in context, super admin impersonation must work
        app()->instance('current_agency', null);

        $panel = $this->makePanelStub('agency');

        $this->assertTrue($admin->canAccessPanel($panel));
    }

    public function test_agency_owner_can_access_agency_panel_on_correct_domain(): void
    {
        $agency = $this->makeAgency('acme');
        $owner = $this->makeOwner($agency);

        app()->instance('current_agency', $agency);

        $panel = $this->makePanelStub('agency');

        $this->assertTrue($owner->canAccessPanel($panel));
    }

    public function test_agency_owner_cannot_access_agency_panel_when_current_agency_is_null(): void
    {
        $agency = $this->makeAgency('acme');
        $owner = $this->makeOwner($agency);

        app()->instance('current_agency', null);

        $panel = $this->makePanelStub('agency');

        $this->assertFalse($owner->canAccessPanel($panel));
    }

    public function test_agency_owner_cannot_access_agency_panel_on_wrong_domain(): void
    {
        $agency1 = $this->makeAgency('acme');
        $agency2 = $this->makeAgency('beta');
        $owner1 = $this->makeOwner($agency1);

        // Simulates arriving on agency2's domain with agency1's credentials
        app()->instance('current_agency', $agency2);

        $panel = $this->makePanelStub('agency');

        $this->assertFalse($owner1->canAccessPanel($panel));
    }

    public function test_central_user_cannot_access_tenant_panel(): void
    {
        $admin = $this->makeSuperAdmin();
        $panel = $this->makePanelStub('tenant');

        $this->assertFalse($admin->canAccessPanel($panel));
    }

    public function test_regular_central_user_cannot_access_admin_panel(): void
    {
        $user = $this->makeOwner($this->makeAgency('x'));
        $panel = $this->makePanelStub('admin');

        $this->assertFalse($user->canAccessPanel($panel));
    }

    // ── Tenant\User::canAccessPanel ───────────────────────────────────────────

    public function test_tenant_user_cannot_access_agency_panel(): void
    {
        $tenantUser = new TenantUser([
            'name' => 'Store User',
            'email' => 'store@example.com',
            'password' => bcrypt('password'),
        ]);

        // tenancy() is not initialised in the central test context
        $this->assertFalse($tenantUser->canAccessPanel($this->makePanelStub('agency')));
    }

    public function test_tenant_user_cannot_access_admin_panel(): void
    {
        $tenantUser = new TenantUser([
            'name' => 'Store User',
            'email' => 'store@example.com',
            'password' => bcrypt('password'),
        ]);

        $this->assertFalse($tenantUser->canAccessPanel($this->makePanelStub('admin')));
    }

    public function test_tenant_user_cannot_access_tenant_panel_when_tenancy_not_initialized(): void
    {
        $tenantUser = new TenantUser([
            'name' => 'Store User',
            'email' => 'store@example.com',
            'password' => bcrypt('password'),
        ]);

        // tenancy() is not initialised — must return false
        $this->assertFalse($tenantUser->canAccessPanel($this->makePanelStub('tenant')));
    }

    // ── EnsureValidAgencyDomain middleware ────────────────────────────────────

    public function test_agency_panel_returns_404_on_unknown_domain(): void
    {
        $this->makeAgency('acme');

        // Full domain URL is required so Symfony's Request::create() sets the
        // correct HTTP_HOST — path-only URLs always resolve to 'localhost'.
        $response = $this->get('http://unknown.linkbay-cms.test/dashboard/login');

        $response->assertNotFound();
    }

    public function test_agency_panel_is_accessible_on_valid_agency_domain(): void
    {
        $this->makeAgency('acme');

        $centralDomain = config('app.central_domain', 'linkbay-cms.test');

        $response = $this->get('http://acme.'.$centralDomain.'/dashboard/login');

        // 200 = login page; 302 = already authenticated
        $this->assertContains($response->getStatusCode(), [200, 302]);
    }

    public function test_agency_panel_returns_404_on_central_app_domain(): void
    {
        // app.linkbay-cms.test is listed as a central domain and must never
        // serve the agency panel, even if a slug 'app' existed.
        $response = $this->get('http://app.linkbay-cms.test/dashboard/login');

        $response->assertNotFound();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(string $slug, ?string $customDomain = null): Agency
    {
        return Agency::create([
            'name' => ucfirst($slug),
            'slug' => $slug,
            'brand_name' => ucfirst($slug),
            'plan_id' => $this->plan->id,
            'billing_type' => 'monthly',
            'status' => 'active',
            'custom_domain' => $customDomain,
        ]);
    }

    private function makeOwner(Agency $agency): CentralUser
    {
        $user = CentralUser::create([
            'name' => 'Owner of '.$agency->name,
            'email' => 'owner-'.$agency->slug.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => false,
        ]);

        $agency->update(['owner_user_id' => $user->id]);

        // AgencyMember record is now required for canAccessPanel() on the agency panel.
        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    private function makeSuperAdmin(): CentralUser
    {
        return CentralUser::create([
            'name' => 'Super Admin',
            'email' => 'admin@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => true,
        ]);
    }

    /**
     * Minimal Panel stub for canAccessPanel() tests — avoids booting the full
     * Filament panel machinery.
     */
    private function makePanelStub(string $id): Panel
    {
        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn($id);

        return $panel;
    }
}
