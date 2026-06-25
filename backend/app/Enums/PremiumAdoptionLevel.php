<?php

declare(strict_types=1);

namespace App\Enums;

enum PremiumAdoptionLevel: string
{
    /** No active entitlements. */
    case None = 'none';

    /** Has active entitlements but premium usage below threshold — not getting value. */
    case Partial = 'partial';

    /** Has active entitlements and uses premium features regularly. */
    case Good = 'good';

    public function label(): string
    {
        return match ($this) {
            self::None => 'Nulla',
            self::Partial => 'Parziale',
            self::Good => 'Buona',
        };
    }

    public function badgeColor(): string
    {
        return match ($this) {
            self::None => 'gray',
            self::Partial => 'warning',
            self::Good => 'success',
        };
    }
}
