<?php

declare(strict_types=1);

namespace App\Plugins\Exceptions;

use RuntimeException;

class DuplicatePluginKeyException extends RuntimeException
{
    public static function forBlock(string $key): self
    {
        return new self("Block key '{$key}' is already registered in the PluginRegistry. Each block key must be unique.");
    }

    public static function forTheme(string $key): self
    {
        return new self("Theme key '{$key}' is already registered in the PluginRegistry. Each theme key must be unique.");
    }
}
