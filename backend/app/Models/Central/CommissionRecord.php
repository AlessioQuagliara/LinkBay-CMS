<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class CommissionRecord extends Model
{
    protected $connection = 'central';

    public const UPDATED_AT = null;  // append-only — solo created_at

    public const STATUS_PENDING  = 'pending';
    public const STATUS_SETTLED  = 'settled';
    public const STATUS_REFUNDED = 'refunded';
    public const STATUS_DISPUTED = 'disputed';
    public const STATUS_FAILED   = 'failed';

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'platform_fee_rule_id',
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'gross_amount_cents',
        'fee_pct',
        'fee_amount_cents',
        'net_to_agency_cents',
        'currency',
        'status',
        'settled_at',
        'refund_amount_cents',
        'metadata',
    ];

    protected $casts = [
        'fee_pct'    => 'decimal:4',
        'settled_at' => 'datetime',
        'metadata'   => 'array',
        'created_at' => 'datetime',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function feeRule()
    {
        return $this->belongsTo(PlatformFeeRule::class, 'platform_fee_rule_id');
    }

    // ── Formatters ────────────────────────────────────────────────────────────

    public function grossFormatted(): string
    {
        return '€' . number_format($this->gross_amount_cents / 100, 2, ',', '.');
    }

    public function feeFormatted(): string
    {
        return '€' . number_format($this->fee_amount_cents / 100, 2, ',', '.');
    }

    public function netFormatted(): string
    {
        return '€' . number_format($this->net_to_agency_cents / 100, 2, ',', '.');
    }

    public function feePctFormatted(): string
    {
        return number_format((float) $this->fee_pct * 100, 1, ',', '.') . '%';
    }

    // ── Mutation helpers ──────────────────────────────────────────────────────

    /**
     * Aggiorna solo la colonna status.
     * Usato da handler webhook per aggiornare record "append-only" (solo status cambia).
     */
    public function forceSetStatus(string $status): void
    {
        $this->getConnection()
             ->table('commission_records')
             ->where('id', $this->id)
             ->update(['status' => $status]);

        $this->status = $status;
    }

    /**
     * Crea il record di storno associato a questo (refund).
     * Append-only: non modifica il record originale.
     */
    public function createRefund(int $refundCents, ?string $reason = null): static
    {
        $refundFee = (int) round($refundCents * (float) $this->fee_pct);

        return static::create([
            'agency_id'            => $this->agency_id,
            'tenant_id'            => $this->tenant_id,
            'platform_fee_rule_id' => $this->platform_fee_rule_id,
            'gross_amount_cents'   => -$refundCents,
            'fee_pct'              => $this->fee_pct,
            'fee_amount_cents'     => -$refundFee,
            'net_to_agency_cents'  => -($refundCents - $refundFee),
            'currency'             => $this->currency,
            'status'               => self::STATUS_REFUNDED,
            'metadata'             => [
                'original_commission_id' => $this->id,
                'reason'                 => $reason,
            ],
        ]);
    }
}
