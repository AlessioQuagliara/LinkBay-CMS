<?php

declare(strict_types=1);

namespace App\Mail\Tenant;

use App\Models\Tenant\BrandSetting;
use App\Models\Tenant\Customer;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class CustomerWelcomeMail extends Mailable implements ShouldQueue
{
    use Queueable, SerializesModels;

    public string $queue = 'emails';

    public int $tries = 3;

    public int $timeout = 60;

    public readonly BrandSetting $brand;

    public function __construct(public readonly Customer $customer)
    {
        $this->brand = BrandSetting::current();
    }

    public function envelope(): Envelope
    {
        $storeName = $this->brand->store_name ?: config('app.name');

        return new Envelope(
            to: $this->customer->email,
            subject: "Benvenuto/a in {$storeName}!",
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.tenant.customer-welcome',
        );
    }
}
