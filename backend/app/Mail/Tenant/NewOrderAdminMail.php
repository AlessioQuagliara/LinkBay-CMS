<?php

declare(strict_types=1);

namespace App\Mail\Tenant;

use App\Models\Tenant\BrandSetting;
use App\Models\Tenant\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class NewOrderAdminMail extends Mailable implements ShouldQueue
{
    use Queueable, SerializesModels;

    public string $queue = 'emails';

    public int $tries = 3;

    public int $timeout = 60;

    public readonly BrandSetting $brand;

    public readonly string $orderNumber;

    public function __construct(
        public readonly Order $order,
        public readonly string $adminEmail,
    ) {
        $this->brand = BrandSetting::current();
        $this->orderNumber = '#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT);
        $this->order->loadMissing(['customer', 'items.product']);
    }

    public function envelope(): Envelope
    {
        $total = number_format((float) $this->order->total, 2, ',', '.');

        return new Envelope(
            to: $this->adminEmail,
            subject: "Nuovo ordine {$this->orderNumber} — €{$total}",
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.tenant.new-order-admin',
        );
    }
}
