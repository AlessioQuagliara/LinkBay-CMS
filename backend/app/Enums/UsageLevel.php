<?php

declare(strict_types=1);

namespace App\Enums;

enum UsageLevel: string
{
    case High = 'high';
    case Medium = 'medium';
    case Low = 'low';

    public function label(): string
    {
        return match ($this) {
            self::High => 'Alto',
            self::Medium => 'Medio',
            self::Low => 'Basso',
        };
    }

    public function badgeColor(): string
    {
        return match ($this) {
            self::High => 'info',
            self::Medium => 'warning',
            self::Low => 'gray',
        };
    }
}
