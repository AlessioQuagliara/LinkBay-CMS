<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Category;
use App\Models\Tenant\Product;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;

class ProductController extends Controller
{
    /** Storefront: paginated product list with search + filters. */
    public function storefront(Request $request): JsonResponse
    {
        $q = $request->string('q')->trim()->value();
        $sort = $request->input('sort', 'newest');

        $query = Product::with([
            'productImages' => fn ($q) => $q->where('is_primary', true)->limit(1),
            'categories:id,name,slug',
        ])->active()->withoutTrashed();

        // Full-text-style search across multiple columns
        if ($q !== '') {
            $query->where(function ($builder) use ($q): void {
                $builder
                    ->where('name', 'like', "%{$q}%")
                    ->orWhere('sku', 'like', "%{$q}%")
                    ->orWhere('description', 'like', "%{$q}%")
                    ->orWhereHas('categories', fn ($c) => $c->where('name', 'like', "%{$q}%"));
            });
        }

        // Filters
        $query
            ->when($request->input('category_slug'), fn ($builder, $slug) => $builder
                ->whereHas('categories', fn ($c) => $c->where('slug', $slug))
            )
            ->when($request->input('collection_slug'), fn ($builder, $slug) => $builder
                ->whereHas('collection', fn ($c) => $c->where('slug', $slug))
            )
            ->when($request->input('min_price'), fn ($builder, $price) => $builder
                ->where('price', '>=', (float) $price)
            )
            ->when($request->input('max_price'), fn ($builder, $price) => $builder
                ->where('price', '<=', (float) $price)
            )
            ->when($request->boolean('in_stock'), fn ($builder) => $builder
                ->where('stock', '>', 0)
            );

        // Sorting
        match ($sort) {
            'price_asc' => $query->orderBy('price'),
            'price_desc' => $query->orderByDesc('price'),
            'name_asc' => $query->orderBy('name'),
            default => $query->orderByDesc('created_at'),
        };

        $paginator = $query->paginate((int) $request->input('per_page', 24));

        $filtersApplied = array_filter([
            'q' => $q !== '' ? $q : null,
            'category_slug' => $request->input('category_slug'),
            'collection_slug' => $request->input('collection_slug'),
            'min_price' => $request->input('min_price'),
            'max_price' => $request->input('max_price'),
            'in_stock' => $request->boolean('in_stock') ?: null,
            'sort' => $sort !== 'newest' ? $sort : null,
        ]);

        return response()->json([
            'data' => $paginator->items(),
            'meta' => [
                'total' => $paginator->total(),
                'per_page' => $paginator->perPage(),
                'current_page' => $paginator->currentPage(),
                'last_page' => $paginator->lastPage(),
                'filters_applied' => (object) $filtersApplied,
            ],
        ]);
    }

    /** Search suggestions: max 5 products + 3 categories, cached 5 min. */
    public function suggestions(Request $request): JsonResponse
    {
        $term = $request->string('q')->trim()->value();

        if (mb_strlen($term) < 2) {
            return response()->json(['products' => [], 'categories' => []]);
        }

        $tenantId = tenancy()->tenant?->id ?? 'global';
        $cacheKey = "search_suggestions:{$tenantId}:".md5($term);

        $result = Cache::remember($cacheKey, now()->addMinutes(5), function () use ($term) {
            $products = Product::active()
                ->withoutTrashed()
                ->with(['productImages' => fn ($q) => $q->where('is_primary', true)->limit(1)])
                ->where(fn ($q) => $q
                    ->where('name', 'like', "%{$term}%")
                    ->orWhere('sku', 'like', "{$term}%")
                )
                ->orderBy('name')
                ->limit(5)
                ->get()
                ->map(fn (Product $p) => [
                    'id' => $p->id,
                    'name' => $p->name,
                    'slug' => $p->slug,
                    'price' => (float) $p->price,
                    'thumbnail_url' => $p->productImages->first()?->url,
                ]);

            $categories = Category::where('is_active', true)
                ->where('name', 'like', "%{$term}%")
                ->orderBy('name')
                ->limit(3)
                ->get(['id', 'name', 'slug']);

            return ['products' => $products, 'categories' => $categories];
        });

        return response()->json($result);
    }

    public function index(Request $request): JsonResponse
    {
        $products = Product::with('collection')
            ->when($request->search, fn ($q) => $q->where('name', 'like', "%{$request->search}%"))
            ->when($request->collection_id, fn ($q) => $q->where('collection_id', $request->collection_id))
            ->when($request->active_only, fn ($q) => $q->active())
            ->when($request->min_price, fn ($q) => $q->where('price', '>=', $request->min_price))
            ->when($request->max_price, fn ($q) => $q->where('price', '<=', $request->max_price))
            ->orderBy($request->sort_by ?? 'created_at', $request->sort_dir ?? 'desc')
            ->paginate($request->per_page ?? 20);

        return response()->json($products);
    }

    public function show(Product $product): JsonResponse
    {
        return response()->json(['data' => $product->load('collection', 'categories', 'productImages')]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'description' => 'nullable|string',
            'price' => 'required|numeric|min:0',
            'compare_price' => 'nullable|numeric|min:0',
            'stock' => 'integer|min:0',
            'sku' => 'nullable|string|unique:products,sku',
            'collection_id' => 'nullable|exists:collections,id',
            'images' => 'nullable|array',
            'images.*' => 'url',
            'is_active' => 'boolean',
            'weight' => 'nullable|numeric|min:0',
            'metadata' => 'nullable|array',
        ]);

        $validated['slug'] = Str::slug($validated['name']);

        $product = Product::create($validated);

        return response()->json(['data' => $product, 'message' => 'Product created successfully'], 201);
    }

    public function update(Request $request, Product $product): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'description' => 'sometimes|nullable|string',
            'price' => 'sometimes|numeric|min:0',
            'compare_price' => 'sometimes|nullable|numeric|min:0',
            'stock' => 'sometimes|integer|min:0',
            'sku' => "sometimes|nullable|string|unique:products,sku,{$product->id}",
            'collection_id' => 'sometimes|nullable|exists:collections,id',
            'images' => 'sometimes|nullable|array',
            'is_active' => 'sometimes|boolean',
            'weight' => 'sometimes|nullable|numeric|min:0',
            'metadata' => 'sometimes|nullable|array',
        ]);

        if (isset($validated['name'])) {
            $validated['slug'] = Str::slug($validated['name']);
        }

        $product->update($validated);

        return response()->json(['data' => $product, 'message' => 'Product updated successfully']);
    }

    public function destroy(Product $product): JsonResponse
    {
        $product->delete();

        return response()->json(['message' => 'Product deleted successfully']);
    }
}
