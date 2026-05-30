<?php

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class ContactSubmission extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'name',
        'company',
        'email',
        'store_count',
        'message',
        'status',
        'ip_address',
    ];
}
