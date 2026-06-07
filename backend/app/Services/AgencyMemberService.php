<?php

declare(strict_types=1);

namespace App\Services;

use App\Mail\AgencyMemberInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;

class AgencyMemberService
{
    public const TTL_HOURS = 72;

    /**
     * Create a pending AgencyMember record, generate an invite token, and
     * dispatch the invitation email.
     *
     * If the email is already an active member of this agency, throws to avoid
     * duplicate records.
     *
     * @throws \RuntimeException for duplicate active memberships
     */
    public function inviteMember(
        Agency $agency,
        string $email,
        string $role,
        User $invitedBy,
    ): AgencyMember {
        $existing = AgencyMember::where('agency_id', $agency->id)
            ->whereHas('user', fn ($q) => $q->where('email', $email))
            ->where('status', AgencyMember::STATUS_ACTIVE)
            ->first();

        if ($existing) {
            throw new \RuntimeException("'{$email}' è già un membro attivo di questa agency.");
        }

        // Re-use or create a pending slot (idempotent resend).
        $member = AgencyMember::firstOrNew([
            'agency_id' => $agency->id,
            'invited_email' => $email,
            'status' => AgencyMember::STATUS_PENDING,
        ]);

        $token = Str::random(64);

        $member->fill([
            'role' => $role,
            'invited_by_user_id' => $invitedBy->id,
            'invited_at' => now(),
            'invite_token' => $token,
            'invite_expires_at' => now()->addHours(self::TTL_HOURS),
        ])->save();

        Mail::to($email)->send(new AgencyMemberInviteMail($member, $agency, $token));

        return $member;
    }

    /**
     * Find a pending AgencyMember by its invite token.
     */
    public function findByToken(string $token): ?AgencyMember
    {
        return AgencyMember::where('invite_token', $token)
            ->where('status', AgencyMember::STATUS_PENDING)
            ->first();
    }

    /**
     * Accept a pending invite.
     *
     * - If a User with invited_email already exists, attaches them.
     * - Otherwise creates a new User with the supplied name + password.
     * - Marks the member active and consumes the token.
     */
    public function acceptInvite(AgencyMember $member, string $name, string $password): User
    {
        $user = User::where('email', $member->invited_email)->first()
            ?? User::create([
                'name' => $name,
                'email' => $member->invited_email,
                'password' => Hash::make($password),
            ]);

        $member->update([
            'user_id' => $user->id,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
            'invite_token' => null,
            'invite_expires_at' => null,
        ]);

        return $user;
    }

    /**
     * Change a member's role.
     *
     * If the new role is 'owner', the current owner of the agency is demoted to
     * 'admin'. Only one owner is allowed per agency.
     */
    public function changeRole(AgencyMember $member, string $newRole): void
    {
        if ($newRole === AgencyMember::ROLE_OWNER) {
            // Demote existing owner(s) to admin.
            AgencyMember::where('agency_id', $member->agency_id)
                ->where('role', AgencyMember::ROLE_OWNER)
                ->where('id', '!=', $member->id)
                ->update(['role' => AgencyMember::ROLE_ADMIN]);
        }

        $member->update(['role' => $newRole]);
    }

    /**
     * Suspend a member. Cannot suspend the owner.
     *
     * @throws \RuntimeException when trying to suspend the agency owner
     */
    public function suspendMember(AgencyMember $member): void
    {
        if ($member->isOwner()) {
            throw new \RuntimeException('Non è possibile sospendere il proprietario dell\'agency.');
        }

        $member->update(['status' => AgencyMember::STATUS_SUSPENDED]);
    }

    /**
     * Reactivate a suspended member.
     */
    public function reactivateMember(AgencyMember $member): void
    {
        $member->update(['status' => AgencyMember::STATUS_ACTIVE]);
    }

    /**
     * Remove a member from the agency entirely.
     *
     * @throws \RuntimeException when trying to remove the only owner
     */
    public function removeMember(AgencyMember $member): void
    {
        if ($member->isOwner()) {
            throw new \RuntimeException('Non è possibile rimuovere il proprietario. Trasferisci prima la proprietà.');
        }

        $member->delete();
    }
}
