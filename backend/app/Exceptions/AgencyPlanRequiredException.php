<?php

declare(strict_types=1);

namespace App\Exceptions;

use RuntimeException;

class AgencyPlanRequiredException extends RuntimeException
{
    public function __construct()
    {
        parent::__construct('Un piano attivo è necessario per creare un nuovo store.');
    }
}
