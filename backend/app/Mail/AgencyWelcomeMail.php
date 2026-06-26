<?php

declare(strict_types=1);

namespace App\Mail;

use App\Models\Central\Agency;
use App\Models\Central\User;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class AgencyWelcomeMail extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public readonly Agency $agency,
        public readonly User $owner,
        public readonly string $loginUrl,
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Benvenuto su LinkBay CMS — ' . $this->agency->name,
        );
    }

    public function content(): Content
    {
        return new Content(
            markdown: 'emails.agency.welcome',
            with: [
                'agencyName' => $this->agency->name,
                'ownerName'  => $this->owner->name,
                'loginUrl'   => $this->loginUrl,
                'isPending'  => $this->agency->status === 'pending',
            ],
        );
    }
}
