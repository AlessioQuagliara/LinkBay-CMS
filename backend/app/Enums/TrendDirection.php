<?php

declare(strict_types=1);

namespace App\Enums;

enum TrendDirection: string
{
    case Growing = 'growing';
    case Stable = 'stable';
    case Declining = 'declining';

    public function label(): string
    {
        return match ($this) {
            self::Growing => '↑ Crescita',
            self::Stable => '→ Stabile',
            self::Declining => '↓ Calo',
        };
    }

    public function badgeColor(): string
    {
        return match ($this) {
            self::Growing => 'success',
            self::Stable => 'gray',
            self::Declining => 'danger',
        };
    }
}
