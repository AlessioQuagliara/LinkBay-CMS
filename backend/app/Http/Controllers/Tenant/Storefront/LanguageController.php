<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Storefront;

use App\Http\Controllers\Controller;
use App\Models\Tenant\StoreLanguage;
use Illuminate\Http\JsonResponse;

class LanguageController extends Controller
{
    public function index(): JsonResponse
    {
        $languages = StoreLanguage::active()
            ->orderByDesc('is_default')
            ->orderBy('locale')
            ->get(['id', 'locale', 'is_default', 'is_active']);

        return response()->json(['data' => $languages]);
    }
}
