<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class AgencyInvoice extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_id',
        'stripe_invoice_id',
        'amount_due',
        'amount_paid',
        'currency',
        'status',
        'invoice_pdf_url',
        'period_start',
        'period_end',
        'paid_at',
        'line_items',
    ];

    protected $casts = [
        'amount_due' => 'integer',
        'amount_paid' => 'integer',
        'period_start' => 'datetime',
        'period_end' => 'datetime',
        'paid_at' => 'datetime',
        'line_items' => 'array',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function amountDueEur(): string
    {
        return '€'.number_format($this->amount_due / 100, 2, ',', '.');
    }

    public function amountPaidEur(): string
    {
        return '€'.number_format($this->amount_paid / 100, 2, ',', '.');
    }

    public function isPaid(): bool
    {
        return $this->status === 'paid';
    }

    public function statusColor(): string
    {
        return match ($this->status) {
            'paid' => 'success',
            'open' => 'warning',
            'void' => 'gray',
            'uncollectible' => 'danger',
            default => 'gray',
        };
    }
}
