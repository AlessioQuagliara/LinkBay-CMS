<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\AgencySettings;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\Plan;
use App\Models\Central\User;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Tests\CentralTestCase;

/**
 * Covers Agency white-label feature: field persistence, feature gate,
 * file upload helpers, and AgencySettings page methods.
 *
 * Tests:
 *  1. Agency without plan cannot use white_label feature
 *  2. Agency with plan (white_label=false) cannot use white_label
 *  3. Agency with plan (white_label=true) can use white_label
 *  4. resolvedPrimaryColor() returns default when color not set
 *  5. resolvedPrimaryColor() returns stored hex color
 *  6. resolvedPrimaryColor() rejects non-hex values and returns default
 *  7. Agency brand fields can be saved (name, logo_url, primary_color)
 *  8. saveBrand() is blocked when agency lacks white_label entitlement
 *  9. saveBrand() updates agency fields when entitlement is active
 * 10. clearLogo() sets logo_url to null
 * 11. canAccessWhiteLabel() returns false when agency has no white_label plan
 * 12. canAccessWhiteLabel() returns true when agency has white_label plan
 */
class AgencyWhiteLabelTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    private function makePlan(array $limits = []): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
            'limits' => $limits,
        ]);
    }

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        $agency = Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        if ($plan) {
            $agency->update(['plan_id' => $plan->id]);
            $agency->load('plan');
        }

        return $agency;
    }

    private function makeOwnerAndBind(Agency $agency): User
    {
        self::$seq++;
        $user = User::create([
            'name' => 'Owner '.self::$seq,
            'email' => 'owner'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);
        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);
        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        return $user;
    }

    // ── Feature gate: canUseFeature ───────────────────────────────────────────

    public function test_agency_without_plan_cannot_use_white_label(): void
    {
        $agency = $this->makeAgency();

        $this->assertFalse($agency->canUseFeature('white_label'));
    }

    public function test_agency_plan_with_white_label_false_cannot_use_feature(): void
    {
        $plan = $this->makePlan(['white_label' => false]);
        $agency = $this->makeAgency($plan);

        $this->assertFalse($agency->canUseFeature('white_label'));
    }

    public function test_agency_plan_with_white_label_true_can_use_feature(): void
    {
        $plan = $this->makePlan(['white_label' => true]);
        $agency = $this->makeAgency($plan);

        $this->assertTrue($agency->canUseFeature('white_label'));
    }

    // ── resolvedPrimaryColor ──────────────────────────────────────────────────

    public function test_resolved_primary_color_returns_default_when_not_set(): void
    {
        $agency = $this->makeAgency();

        $this->assertEquals('#ff5758', $agency->resolvedPrimaryColor());
    }

    public function test_resolved_primary_color_returns_stored_hex(): void
    {
        $agency = $this->makeAgency();
        $agency->update(['primary_color' => '#3b82f6']);

        $this->assertEquals('#3b82f6', $agency->resolvedPrimaryColor());
    }

    public function test_resolved_primary_color_rejects_non_hex_and_returns_default(): void
    {
        $agency = $this->makeAgency();
        $agency->update(['primary_color' => 'blue']);

        $this->assertEquals('#ff5758', $agency->resolvedPrimaryColor());
    }

    // ── Agency brand fields persistence ───────────────────────────────────────

    public function test_agency_brand_fields_can_be_saved(): void
    {
        $agency = $this->makeAgency();
        $agency->update([
            'brand_name' => 'My Brand',
            'logo_url' => 'https://example.com/logo.png',
            'primary_color' => '#ff0000',
            'support_email' => 'support@example.com',
        ]);
        $agency->refresh();

        $this->assertEquals('My Brand', $agency->brand_name);
        $this->assertEquals('https://example.com/logo.png', $agency->logo_url);
        $this->assertEquals('#ff0000', $agency->primary_color);
        $this->assertEquals('support@example.com', $agency->support_email);
    }

    // ── AgencySettings page methods ───────────────────────────────────────────

    public function test_save_brand_blocked_without_white_label_entitlement(): void
    {
        $agency = $this->makeAgency(); // no plan → white_label = false
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;
        $page->brandData = ['brand_name' => 'New Brand'];

        $page->saveBrand();

        $agency->refresh();
        $this->assertNotEquals('New Brand', $agency->brand_name);
    }

    public function test_save_brand_updates_fields_when_white_label_active(): void
    {
        $plan = $this->makePlan(['white_label' => true]);
        $agency = $this->makeAgency($plan);
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;
        $page->brandData = [
            'brand_name' => 'White Label Brand',
            'primary_color' => '#aabbcc',
            'support_email' => 'help@brand.com',
            'logo_url' => null,
            'favicon_url' => null,
            'support_url' => null,
        ];

        $page->saveBrand();

        $agency->refresh();
        $this->assertEquals('White Label Brand', $agency->brand_name);
        $this->assertEquals('#aabbcc', $agency->primary_color);
        $this->assertEquals('help@brand.com', $agency->support_email);
    }

    public function test_save_brand_with_logo_file_stores_and_updates_logo_url(): void
    {
        Storage::fake('public');

        $plan = $this->makePlan(['white_label' => true]);
        $agency = $this->makeAgency($plan);
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;
        $page->brandData = [
            'brand_name' => 'Upload Test',
            'primary_color' => '#ff5758',
            'support_email' => null,
            'logo_url' => null,
            'favicon_url' => null,
            'support_url' => null,
        ];
        $page->logoFile = UploadedFile::fake()->image('logo.png', 200, 50);

        $page->saveBrand();

        $agency->refresh();
        $this->assertNotNull($agency->logo_url);
        $this->assertStringContainsString("agency/{$agency->id}/logo", $agency->logo_url);
    }

    public function test_clear_logo_sets_logo_url_to_null(): void
    {
        $plan = $this->makePlan(['white_label' => true]);
        $agency = $this->makeAgency($plan);
        $agency->update(['logo_url' => 'https://example.com/old-logo.png']);
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;
        $page->brandData = ['logo_url' => 'https://example.com/old-logo.png'];

        $page->clearLogo();

        $agency->refresh();
        $this->assertNull($agency->logo_url);
    }

    // ── canAccessWhiteLabel ───────────────────────────────────────────────────

    public function test_can_access_white_label_returns_false_without_plan(): void
    {
        $agency = $this->makeAgency();
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;

        $this->assertFalse($page->canAccessWhiteLabel());
    }

    public function test_can_access_white_label_returns_true_with_plan(): void
    {
        $plan = $this->makePlan(['white_label' => true]);
        $agency = $this->makeAgency($plan);
        $this->makeOwnerAndBind($agency);

        $page = new AgencySettings;

        $this->assertTrue($page->canAccessWhiteLabel());
    }
}
