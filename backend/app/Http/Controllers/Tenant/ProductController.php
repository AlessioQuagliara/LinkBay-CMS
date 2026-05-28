<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Product;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class ProductController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $products = Product::with('collection')
            ->when($request->search, fn($q) => $q->where('name', 'like', "%{$request->search}%"))
            ->when($request->collection_id, fn($q) => $q->where('collection_id', $request->collection_id))
            ->when($request->active_only, fn($q) => $q->active())
            ->when($request->min_price, fn($q) => $q->where('price', '>=', $request->min_price))
            ->when($request->max_price, fn($q) => $q->where('price', '<=', $request->max_price))
            ->orderBy($request->sort_by ?? 'created_at', $request->sort_dir ?? 'desc')
            ->paginate($request->per_page ?? 20);

        return response()->json($products);
    }

    public function show(Product $product): JsonResponse
    {
        return response()->json(['data' => $product->load('collection')]);
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
