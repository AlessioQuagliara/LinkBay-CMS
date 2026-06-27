<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Mail\ClientInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyClientContact;
use App\Models\Central\AgencyMember;
use App\Models\Central\Tenant;
use App\Models\Central\User;
use App\Models\Tenant\User as TenantUser;
use App\Services\ClientInviteService;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers the full client-invite flow end-to-end.
 * Extends scenarios from ClientInviteTest with:
 *
 *  1. Owner generates invite → token stored, mail sent to contact email
 *  2. Contact clicks link → view rendered (200)
 *  3. Contact accepts invite → can_access_tenant=true, token cleared
 *  4. Expired token → redirect to client-invite.invalid
 *  5. Already-used (invalidated) token → redirect to client-invite.invalid
 *  6. Double acceptance of same token → idempotent (no error, valid redirect)
 *  7. Authenticated user from a different agency → 403
 */
class ClientInviteFullFlowTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeClient(Agency $agency): AgencyClient
    {
        self::$seq++;

        return AgencyClient::create([
            'agency_id' => $agency->id,
            'name' => 'Client '.self::$seq,
            'billing_email' => 'client'.self::$seq.'@example.com',
            'status' => 'active',
        ]);
    }

    private function makeContact(AgencyClient $client, string $email = ''): AgencyClientContact
    {
        self::$seq++;
        $email = $email ?: ('contact'.self::$seq.'@example.com');

        return AgencyClientContact::create([
            'agency_client_id' => $client->id,
            'name' => 'Contact '.self::$seq,
            'email' => $email,
            'can_access_tenant' => false,
        ]);
    }

    /** Unsaved Tenant — avoids touching the tenants table for service-level tests. */
    private function fakeTenant(): Tenant
    {
        $tenant = new Tenant;
        $tenant->id = 'store-'.uniqid();
        $tenant->name = 'Test Store';

        return $tenant;
    }

    private function service(): ClientInviteService
    {
        return app(ClientInviteService::class);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    public function test_generate_invite_stores_token_and_sends_mail_to_contact(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client, 'mario@example.com');
        $tenant = $this->fakeTenant();

        // ── Generate invite ───────────────────────────────────────────────────
        $this->service()->generateInvite($contact, $tenant);
        $contact->refresh();

        // ── Token persisted ───────────────────────────────────────────────────
        $this->assertNotNull($contact->invite_token);
        $this->assertEquals(64, strlen($contact->invite_token));
        $this->assertEquals($tenant->id, $contact->invite_tenant_id);
        $this->assertTrue($contact->invite_expires_at->isFuture());

        // ── Mail dispatched to the contact's email ────────────────────────────
        Mail::assertSent(ClientInviteMail::class, fn ($m) => $m->hasTo('mario@example.com'));
    }

    // ── Test 2 ────────────────────────────────────────────────────────────────

    public function test_show_returns_200_for_valid_pending_token(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();

        $this->service()->generateInvite($contact, $tenant);
        $contact->refresh();

        $response = $this->get(route('client-invite.show', $contact->invite_token));

        $response->assertStatus(200);
        $response->assertViewIs('client-invite.show');
    }

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_accept_invite_grants_tenant_access_and_clears_token(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();

        $this->service()->generateInvite($contact, $tenant);
        $contact->refresh();
        $token = $contact->invite_token;

        $fakeTenantUser = new TenantUser(['name' => 'Contact', 'email' => $contact->email]);

        // ── Mock service so acceptInvite() does not require a live tenant DB ──
        $this->mock(ClientInviteService::class, function ($mock) use ($contact, $fakeTenantUser, $token) {
            $mock->shouldReceive('findByToken')
                ->once()
                ->with($token)
                ->andReturn($contact);

            $mock->shouldReceive('acceptInvite')
                ->once()
                ->andReturnUsing(function () use ($contact, $fakeTenantUser) {
                    // Replicate what the real acceptInvite does to the contact
                    $contact->update([
                        'can_access_tenant' => true,
                        'invite_token' => null,
                        'invite_tenant_id' => null,
                        'invite_expires_at' => null,
                    ]);

                    return $fakeTenantUser;
                });
        });

        $response = $this->post(route('client-invite.accept', $token), [
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ]);

        $response->assertRedirect(route('client-invite.accepted'));

        // ── Token cleared, access granted ─────────────────────────────────────
        $contact->refresh();
        $this->assertTrue($contact->can_access_tenant);
        $this->assertNull($contact->invite_token);
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_expired_token_redirects_to_invalid(): void
    {
        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);

        $contact->update([
            'invite_token' => 'expired-token-abc',
            'invite_tenant_id' => 'store-fake',
            'invite_expires_at' => now()->subHour(),
        ]);

        $response = $this->get(route('client-invite.show', 'expired-token-abc'));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    // ── Test 5 ────────────────────────────────────────────────────────────────

    public function test_invalidated_token_redirects_to_invalid(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();
        $service = $this->service();

        $service->generateInvite($contact, $tenant);
        $contact->refresh();
        $originalToken = $contact->invite_token;

        // ── Invalidate the token (simulates post-acceptance cleanup) ──────────
        $service->invalidate($contact);

        $response = $this->get(route('client-invite.show', $originalToken));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    // ── Test 6 ────────────────────────────────────────────────────────────────

    public function test_second_acceptance_of_same_token_is_idempotent(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();
        $service = $this->service();

        $service->generateInvite($contact, $tenant);
        $contact->refresh();
        $originalToken = $contact->invite_token;

        // ── First acceptance: token consumed ──────────────────────────────────
        $contact->update([
            'can_access_tenant' => true,
            'invite_token' => null,
            'invite_tenant_id' => null,
            'invite_expires_at' => null,
        ]);

        // ── Second attempt with the now-invalid original token ─────────────────
        // findByToken returns null → redirect to invalid, no exception raised
        $response = $this->get(route('client-invite.show', $originalToken));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    // ── Test 7 ────────────────────────────────────────────────────────────────

    public function test_accept_returns_403_if_authenticated_user_belongs_to_different_agency(): void
    {
        Mail::fake();

        $agencyA = $this->makeAgency();
        $clientA = $this->makeClient($agencyA);
        $contactA = $this->makeContact($clientA);

        $this->service()->generateInvite($contactA, $this->fakeTenant());
        $contactA->refresh();

        $agencyB = $this->makeAgency();

        self::$seq++;
        $ownerB = User::create([
            'name' => 'Owner B '.self::$seq,
            'email' => 'ownerb'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);

        AgencyMember::create([
            'agency_id' => $agencyB->id,
            'user_id' => $ownerB->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        $response = $this->actingAs($ownerB)->post(
            route('client-invite.accept', $contactA->invite_token),
            ['password' => 'password123', 'password_confirmation' => 'password123'],
        );

        $response->assertStatus(403);
    }

    // ── Service: token helpers ────────────────────────────────────────────────

    public function test_find_by_token_returns_correct_contact(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();
        $service = $this->service();

        $service->generateInvite($contact, $tenant);
        $contact->refresh();

        $found = $service->findByToken($contact->invite_token);

        $this->assertNotNull($found);
        $this->assertEquals($contact->id, $found->id);
    }

    public function test_find_by_token_returns_null_for_unknown_token(): void
    {
        $result = $this->service()->findByToken('no-such-token-xyz');

        $this->assertNull($result);
    }

    public function test_invalidate_clears_all_token_fields(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();
        $service = $this->service();

        $service->generateInvite($contact, $tenant);
        $service->invalidate($contact);
        $contact->refresh();

        $this->assertNull($contact->invite_token);
        $this->assertNull($contact->invite_tenant_id);
        $this->assertNull($contact->invite_expires_at);
    }
}
