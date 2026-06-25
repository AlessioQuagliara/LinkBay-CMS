<?php

declare(strict_types=1);

namespace App\Services;

use App\Mail\AgencyMemberInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\AuditEvent;
use App\Models\Central\UsageEvent;
use App\Models\Central\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;

class AgencyMemberService
{
    public const TTL_HOURS = 72;

    public function __construct(
        private readonly AuditEventService $audit,
        private readonly UsageEventService $usage,
    ) {}

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

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_INVITED,
            agencyId: $agency->id,
            userId: $invitedBy->id,
            subjectType: 'agency_member',
            subjectId: $member->id,
            newValues: ['email' => $email, 'role' => $role],
        );

        $this->usage->track(
            eventType: UsageEvent::EVENT_TEAM_MEMBER_INVITED,
            agencyId: $agency->id,
            userId: $invitedBy->id,
            meta: ['role' => $role],
        );

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

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_ACCEPTED,
            agencyId: $member->agency_id,
            userId: $user->id,
            subjectType: 'agency_member',
            subjectId: $member->id,
            newValues: ['name' => $name, 'role' => $member->role],
        );

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
        $oldRole = $member->role;

        if ($newRole === AgencyMember::ROLE_OWNER) {
            // Demote existing owner(s) to admin.
            AgencyMember::where('agency_id', $member->agency_id)
                ->where('role', AgencyMember::ROLE_OWNER)
                ->where('id', '!=', $member->id)
                ->update(['role' => AgencyMember::ROLE_ADMIN]);
        }

        $member->update(['role' => $newRole]);

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_ROLE_CHANGED,
            agencyId: $member->agency_id,
            subjectType: 'agency_member',
            subjectId: $member->id,
            oldValues: ['role' => $oldRole],
            newValues: ['role' => $newRole],
        );
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

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_SUSPENDED,
            agencyId: $member->agency_id,
            subjectType: 'agency_member',
            subjectId: $member->id,
            oldValues: ['status' => AgencyMember::STATUS_ACTIVE],
            newValues: ['status' => AgencyMember::STATUS_SUSPENDED],
            metadata: ['email' => $member->user?->email ?? $member->invited_email],
        );
    }

    /**
     * Reactivate a suspended member.
     */
    public function reactivateMember(AgencyMember $member): void
    {
        $member->update(['status' => AgencyMember::STATUS_ACTIVE]);

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_REACTIVATED,
            agencyId: $member->agency_id,
            subjectType: 'agency_member',
            subjectId: $member->id,
            oldValues: ['status' => AgencyMember::STATUS_SUSPENDED],
            newValues: ['status' => AgencyMember::STATUS_ACTIVE],
        );
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

        // Capture data before deletion so it appears in the audit log.
        $agencyId = $member->agency_id;
        $memberId = $member->id;
        $email = $member->user?->email ?? $member->invited_email;
        $role = $member->role;

        $member->delete();

        $this->audit->log(
            event: AuditEvent::EVENT_MEMBER_REMOVED,
            agencyId: $agencyId,
            subjectType: 'agency_member',
            subjectId: $memberId,
            oldValues: ['email' => $email, 'role' => $role],
        );
    }
}
