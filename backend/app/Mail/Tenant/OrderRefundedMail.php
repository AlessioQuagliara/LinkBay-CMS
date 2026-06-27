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

class OrderRefundedMail extends Mailable implements ShouldQueue
{
    use Queueable, SerializesModels;

    public string $queue = 'emails';

    public int $tries = 3;

    public int $timeout = 60;

    public readonly BrandSetting $brand;

    public readonly string $orderNumber;

    public function __construct(
        public readonly Order $order,
        public readonly float $refundAmount,
    ) {
        $this->brand = BrandSetting::current();
        $this->orderNumber = '#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT);
        $this->order->loadMissing(['customer']);
    }

    public function envelope(): Envelope
    {
        return new Envelope(
            to: $this->order->customer?->email ?? '',
            subject: "Rimborso elaborato per ordine {$this->orderNumber}",
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.tenant.order-refunded',
        );
    }
}
