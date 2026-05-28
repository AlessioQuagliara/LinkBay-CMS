<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

class FeatureNotAvailableException extends RuntimeException
{
    public function __construct(public readonly string $feature)
    {
        parent::__construct("Upgrade your plan to access {$feature}");
    }
}
