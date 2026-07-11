<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class Setting extends Model
{
    // 'key' (string) is the real primary key — see the migration, no 'id'
    // column exists. Without these three, Eloquent assumes an auto-increment
    // 'id' and appends "returning id" to inserts, which SQLite tolerates but
    // Postgres hard-fails on ("column id does not exist") — found via live
    // tenant-provisioning testing, 2026-07-09.
    protected $primaryKey = 'key';

    public $incrementing = false;

    protected $keyType = 'string';

    protected $fillable = ['key', 'value', 'group'];

    public $timestamps = false;

    protected $casts = [
        'value' => 'json',
    ];

    public static function get(string $key, mixed $default = null): mixed
    {
        return static::where('key', $key)->value('value') ?? $default;
    }

    public static function set(string $key, mixed $value, string $group = 'general'): void
    {
        static::updateOrCreate(
            ['key' => $key],
            ['value' => $value, 'group' => $group]
        );
    }
}
