<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class Translation extends Model
{
    protected $table = 'translations';

    protected $fillable = [
        'translatable_type',
        'translatable_id',
        'locale',
        'field',
        'value',
    ];

    public function translatable()
    {
        return $this->morphTo();
    }

    public function scopeForLocale(Builder $query, string $locale): Builder
    {
        return $query->where('locale', $locale);
    }
}
