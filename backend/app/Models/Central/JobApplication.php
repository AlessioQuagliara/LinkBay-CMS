<?php

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class JobApplication extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'job_position_id',
        'full_name',
        'email',
        'phone',
        'location',
        'linkedin_url',
        'portfolio_url',
        'motivation',
        'experience_summary',
        'cv_path',
        'status',
        'admin_notes',
        'ip_address',
    ];

    public function position(): BelongsTo
    {
        return $this->belongsTo(JobPosition::class, 'job_position_id');
    }
}
