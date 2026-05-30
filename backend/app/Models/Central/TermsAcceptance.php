<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class TermsAcceptance extends Model
{
    protected $connection = 'central';

    public $timestamps = false;

    protected $fillable = [
        'agency_id',
        'user_id',
        'terms_version',
        'ip_address',
        'user_agent',
        'accepted_at',
    ];

    protected $casts = [
        'accepted_at' => 'datetime',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public static function currentVersion(): string
    {
        return config('app.terms_version', '2026-01');
    }

    public static function hasAccepted(int $agencyId): bool
    {
        return static::where('agency_id', $agencyId)
            ->where('terms_version', static::currentVersion())
            ->exists();
    }

    public static function record(Agency $agency, int $userId, string $ip, ?string $ua): static
    {
        return static::create([
            'agency_id'     => $agency->id,
            'user_id'       => $userId,
            'terms_version' => static::currentVersion(),
            'ip_address'    => $ip,
            'user_agent'    => $ua,
            'accepted_at'   => now(),
        ]);
    }
}
