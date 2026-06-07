<?php

declare(strict_types=1);

namespace App\Mail;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class AgencyMemberInviteMail extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public readonly AgencyMember $member,
        public readonly Agency $agency,
        public readonly string $token,
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Sei stato invitato a '.$this->agency->brand_name,
        );
    }

    public function content(): Content
    {
        return new Content(
            markdown: 'emails.agency-member-invite',
            with: [
                'inviteUrl' => route('agency-invite.show', ['token' => $this->token]),
                'agencyName' => $this->agency->brand_name,
                'roleLabel' => $this->member->roleLabel(),
                'expiresAt' => now()->addHours(72)->format('d/m/Y H:i'),
            ],
        );
    }

    public function attachments(): array
    {
        return [];
    }
}
