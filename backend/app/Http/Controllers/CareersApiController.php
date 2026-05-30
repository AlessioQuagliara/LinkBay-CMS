<?php

namespace App\Http\Controllers;

use App\Models\Central\JobPosition;
use Illuminate\Http\JsonResponse;

class CareersApiController extends Controller
{
    public function positions(): JsonResponse
    {
        $positions = JobPosition::published()
            ->orderByDesc('featured')
            ->orderBy('sort_order')
            ->orderByDesc('published_at')
            ->get([
                'id', 'title', 'slug', 'department', 'location',
                'work_mode', 'employment_type', 'summary', 'featured',
            ]);

        return response()->json(['data' => $positions]);
    }
}
