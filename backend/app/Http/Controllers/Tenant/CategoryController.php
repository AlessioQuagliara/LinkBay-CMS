<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Category;
use Illuminate\Http\JsonResponse;

class CategoryController extends Controller
{
    public function index(): JsonResponse
    {
        $categories = Category::with('children')
            ->active()
            ->root()
            ->orderBy('sort_order')
            ->get();

        return response()->json(['data' => $categories]);
    }

    public function products(string $slug): JsonResponse
    {
        $category = Category::where('slug', $slug)->active()->firstOrFail();

        $products = $category->products()
            ->with(['productImages' => fn ($q) => $q->where('is_primary', true)])
            ->active()
            ->paginate(20);

        return response()->json([
            'data' => $products->items(),
            'meta' => [
                'category' => $category->only(['id', 'name', 'slug', 'description']),
                'total' => $products->total(),
                'per_page' => $products->perPage(),
                'current_page' => $products->currentPage(),
                'last_page' => $products->lastPage(),
            ],
        ]);
    }
}
