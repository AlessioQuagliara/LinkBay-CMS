<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Mail\ClientInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyClientContact;
use App\Models\Central\Tenant;
use App\Services\ClientInviteService;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers ClientInviteService and the invite HTTP flow.
 *
 * TenantUser provisioning (acceptInvite) requires a running tenant DB so it is
 * tested at the HTTP level in a separate integration test. These tests cover:
 *   - Token generation, storage, and expiry helpers
 *   - Mail dispatch
 *   - findByToken
 *   - invalidate
 *   - HTTP show/redirect behaviour
 */
class ClientInviteTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        return Agency::create([
            'name' => 'Test Agency',
            'slug' => 'test-agency',
            'brand_name' => 'Test Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    /**
     * Returns an unsaved Tenant model. The service only reads ->id and ->name,
     * so no DB record is needed. This avoids the 'tenants' table which lands on
     * the default sqlite connection in tests (not 'central').
     */
    private function fakeTenant(): Tenant
    {
        $tenant = new Tenant;
        $tenant->id = 'store-test-'.uniqid();
        $tenant->name = 'Test Store';

        return $tenant;
    }

    private function makeContact(Agency $agency): AgencyClientContact
    {
        $client = AgencyClient::create([
            'agency_id' => $agency->id,
            'name' => 'ACME Ltd',
            'billing_email' => 'acme@example.com',
            'status' => 'active',
        ]);

        return AgencyClientContact::create([
            'agency_client_id' => $client->id,
            'name' => 'Alice',
            'email' => 'alice@example.com',
            'can_access_tenant' => false,
        ]);
    }

    // ── Service: token generation ─────────────────────────────────────────────

    public function test_generate_invite_stores_token_and_expiry(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $tenant = $this->fakeTenant();
        $contact = $this->makeContact($agency);

        app(ClientInviteService::class)->generateInvite($contact, $tenant);

        $contact->refresh();

        $this->assertNotNull($contact->invite_token);
        $this->assertEquals(64, strlen($contact->invite_token));
        $this->assertEquals($tenant->id, $contact->invite_tenant_id);
        $this->assertTrue($contact->invite_expires_at->isFuture());
    }

    public function test_generate_invite_sends_mail_to_contact_email(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $tenant = $this->fakeTenant();
        $contact = $this->makeContact($agency);

        app(ClientInviteService::class)->generateInvite($contact, $tenant);

        Mail::assertSent(ClientInviteMail::class, fn ($mail) => $mail->hasTo('alice@example.com'));
    }

    public function test_find_by_token_returns_contact(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $tenant = $this->fakeTenant();
        $contact = $this->makeContact($agency);
        $service = app(ClientInviteService::class);

        $service->generateInvite($contact, $tenant);
        $contact->refresh();

        $found = $service->findByToken($contact->invite_token);

        $this->assertNotNull($found);
        $this->assertEquals($contact->id, $found->id);
    }

    public function test_find_by_token_returns_null_for_unknown_token(): void
    {
        $result = app(ClientInviteService::class)->findByToken('nonexistent_token_xyz');

        $this->assertNull($result);
    }

    public function test_is_invite_expired_detects_past_expiry(): void
    {
        $agency = $this->makeAgency();
        $contact = $this->makeContact($agency);

        $contact->update([
            'invite_token' => 'sometoken',
            'invite_tenant_id' => 'store-fake',
            'invite_expires_at' => now()->subHour(),
        ]);

        $this->assertTrue($contact->isInviteExpired());
        $this->assertFalse($contact->hasPendingInvite());
    }

    public function test_has_pending_invite_detects_active_token(): void
    {
        $agency = $this->makeAgency();
        $contact = $this->makeContact($agency);

        $contact->update([
            'invite_token' => 'sometoken',
            'invite_tenant_id' => 'store-fake',
            'invite_expires_at' => now()->addHours(72),
        ]);

        $this->assertTrue($contact->hasPendingInvite());
        $this->assertFalse($contact->isInviteExpired());
    }

    public function test_invalidate_clears_token_fields(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $tenant = $this->fakeTenant();
        $contact = $this->makeContact($agency);
        $service = app(ClientInviteService::class);

        $service->generateInvite($contact, $tenant);
        $service->invalidate($contact);

        $contact->refresh();

        $this->assertNull($contact->invite_token);
        $this->assertNull($contact->invite_tenant_id);
        $this->assertNull($contact->invite_expires_at);
    }

    // ── HTTP: show route ──────────────────────────────────────────────────────

    public function test_show_returns_200_for_valid_token(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $tenant = $this->fakeTenant();
        $contact = $this->makeContact($agency);
        app(ClientInviteService::class)->generateInvite($contact, $tenant);
        $contact->refresh();

        $response = $this->get(route('client-invite.show', $contact->invite_token));

        $response->assertStatus(200);
        $response->assertViewIs('client-invite.show');
    }

    public function test_show_redirects_for_unknown_token(): void
    {
        $response = $this->get(route('client-invite.show', 'badtoken'));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    public function test_show_redirects_for_expired_token(): void
    {
        $agency = $this->makeAgency();
        $contact = $this->makeContact($agency);

        $contact->update([
            'invite_token' => 'expiredtoken',
            'invite_tenant_id' => 'store-fake',
            'invite_expires_at' => now()->subHour(),
        ]);

        $response = $this->get(route('client-invite.show', 'expiredtoken'));

        $response->assertRedirect(route('client-invite.invalid'));
    }
}
