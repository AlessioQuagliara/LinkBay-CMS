<?php

declare(strict_types=1);

namespace App\Services;

use App\Mail\ClientInviteMail;
use App\Models\Central\AgencyClientContact;
use App\Models\Central\Tenant;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;

class ClientInviteService
{
    public const TTL_HOURS = 72;

    /**
     * Generate a fresh invite token for a contact→tenant pair, persist it,
     * and dispatch the invitation email.
     */
    public function generateInvite(AgencyClientContact $contact, Tenant $tenant): string
    {
        $token = Str::random(64);

        $contact->update([
            'invite_token' => $token,
            'invite_tenant_id' => $tenant->id,
            'invite_expires_at' => now()->addHours(self::TTL_HOURS),
        ]);

        Mail::to($contact->email)->send(new ClientInviteMail($contact, $tenant, $token));

        return $token;
    }

    /**
     * Find a contact by invite token, returning null when not found.
     */
    public function findByToken(string $token): ?AgencyClientContact
    {
        return AgencyClientContact::where('invite_token', $token)->first();
    }

    /**
     * Provision a TenantUser in the contact's target store, mark the contact
     * as having access, and consume the token.
     *
     * @throws \RuntimeException when token has no associated tenant
     */
    public function acceptInvite(AgencyClientContact $contact, string $password): User
    {
        $tenant = $contact->inviteTenant;

        if (! $tenant) {
            throw new \RuntimeException("Invite has no associated tenant for contact #{$contact->id}");
        }

        tenancy()->initialize($tenant);

        try {
            $tenantUser = User::updateOrCreate(
                ['email' => $contact->email],
                ['name' => $contact->name, 'password' => $password],
            );
        } finally {
            tenancy()->end();
        }

        $contact->update([
            'can_access_tenant' => true,
            'invite_token' => null,
            'invite_expires_at' => null,
        ]);

        return $tenantUser;
    }

    /**
     * Revoke any pending invite on a contact without provisioning access.
     */
    public function invalidate(AgencyClientContact $contact): void
    {
        $contact->update([
            'invite_token' => null,
            'invite_tenant_id' => null,
            'invite_expires_at' => null,
        ]);
    }
}
