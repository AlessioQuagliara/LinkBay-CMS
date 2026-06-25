<?php

declare(strict_types=1);

namespace App\Enums;

enum ActivityLevel: string
{
    case High = 'high';
    case Medium = 'medium';
    case Low = 'low';

    public function label(): string
    {
        return match ($this) {
            self::High => 'Alta',
            self::Medium => 'Media',
            self::Low => 'Bassa',
        };
    }

    public function badgeColor(): string
    {
        return match ($this) {
            self::High => 'success',
            self::Medium => 'warning',
            self::Low => 'gray',
        };
    }
}
