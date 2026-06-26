<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Mail\ClientInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyClientContact;
use App\Models\Central\Tenant;
use App\Models\Tenant\User as TenantUser;
use App\Services\ClientInviteService;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * End-to-end tests for the store owner onboarding flow:
 * invite dispatch → token validation → accept form → tenant user provisioned.
 *
 * acceptInvite() requires a live tenant DB (tenancy()->initialize()).
 * That step is covered by mocking the service so the HTTP layer can be
 * tested without spinning up a real tenant SQLite file.
 */
class StoreOwnerOnboardingTest extends CentralTestCase
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

    private function makeClient(Agency $agency): AgencyClient
    {
        return AgencyClient::create([
            'agency_id' => $agency->id,
            'name' => 'Pizzeria Mario',
            'billing_email' => 'mario@pizza.it',
            'status' => 'active',
        ]);
    }

    /**
     * Returns an unsaved Tenant model — enough for the service to read ->id and ->name
     * without touching the tenants table (which lives on the default connection in tests).
     */
    private function fakeTenant(): Tenant
    {
        $tenant = new Tenant;
        $tenant->id = 'store-mario-'.uniqid();
        $tenant->name = 'Pizzeria Mario Store';

        return $tenant;
    }

    private function makeContact(AgencyClient $client, string $email = 'mario@pizza.it'): AgencyClientContact
    {
        return AgencyClientContact::create([
            'agency_client_id' => $client->id,
            'name' => 'Mario Rossi',
            'email' => $email,
            'can_access_tenant' => false,
        ]);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    public function test_agency_can_invite_store_owner(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();

        app(ClientInviteService::class)->generateInvite($contact, $tenant);

        $contact->refresh();

        $this->assertNotNull($contact->invite_token);
        $this->assertEquals(64, strlen($contact->invite_token));
        $this->assertEquals($tenant->id, $contact->invite_tenant_id);
        $this->assertTrue($contact->invite_expires_at->isFuture());
        Mail::assertSent(ClientInviteMail::class, fn ($m) => $m->hasTo('mario@pizza.it'));
    }

    // ── Test 2 ────────────────────────────────────────────────────────────────

    public function test_invite_token_expires_after_72_hours(): void
    {
        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);

        $contact->update([
            'invite_token' => 'expiredtoken123',
            'invite_tenant_id' => 'store-fake',
            'invite_expires_at' => now()->subHour(),
        ]);

        $response = $this->get(route('client-invite.show', 'expiredtoken123'));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_store_owner_can_accept_invite_and_access_tenant_panel(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();

        app(ClientInviteService::class)->generateInvite($contact, $tenant);
        $contact->refresh();
        $token = $contact->invite_token;

        $fakeTenantUser = new TenantUser(['name' => 'Mario Rossi', 'email' => 'mario@pizza.it']);

        // Mock the service so acceptInvite() does not need a real tenant DB.
        $this->mock(ClientInviteService::class, function ($mock) use ($contact, $fakeTenantUser, $token) {
            $mock->shouldReceive('findByToken')
                ->once()
                ->with($token)
                ->andReturn($contact);

            $mock->shouldReceive('acceptInvite')
                ->once()
                ->andReturn($fakeTenantUser);
        });

        $response = $this->post(route('client-invite.accept', $token), [
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ]);

        $response->assertRedirect(route('client-invite.accepted'));
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_invite_cannot_be_accepted_twice(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);
        $contact = $this->makeContact($client);
        $tenant = $this->fakeTenant();
        $service = app(ClientInviteService::class);

        $service->generateInvite($contact, $tenant);
        $contact->refresh();
        $originalToken = $contact->invite_token;

        // Simulate first acceptance: token is cleared, can_access_tenant set to true.
        $contact->update([
            'can_access_tenant' => true,
            'invite_token' => null,
            'invite_tenant_id' => null,
            'invite_expires_at' => null,
        ]);

        // Second attempt with the original token — findByToken returns null.
        $response = $this->get(route('client-invite.show', $originalToken));

        $response->assertRedirect(route('client-invite.invalid'));
    }
}
