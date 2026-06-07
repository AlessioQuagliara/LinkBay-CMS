<?php

declare(strict_types=1);

namespace App\Mail;

use App\Models\Central\AgencyClientContact;
use App\Models\Central\Tenant;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class ClientInviteMail extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public readonly AgencyClientContact $contact,
        public readonly Tenant $tenant,
        public readonly string $token,
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Accesso al tuo store — '.$this->tenant->name,
        );
    }

    public function content(): Content
    {
        return new Content(
            markdown: 'emails.client-invite',
            with: [
                'inviteUrl' => route('client-invite.show', ['token' => $this->token]),
                'storeName' => $this->tenant->name,
                'contactName' => $this->contact->name,
                'expiresAt' => now()->addHours(72)->format('d/m/Y H:i'),
            ],
        );
    }

    public function attachments(): array
    {
        return [];
    }
}
