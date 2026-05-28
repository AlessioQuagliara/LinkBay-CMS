<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

class InsufficientCreditsException extends RuntimeException
{
    public function __construct(
        public readonly int $balance,
        public readonly int $required,
    ) {
        parent::__construct("Insufficient AI credits. Balance: {$balance}, Required: {$required}");
    }
}
