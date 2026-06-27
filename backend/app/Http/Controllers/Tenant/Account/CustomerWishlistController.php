<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Account;

use App\Http\Controllers\Controller;
use App\Services\Tenant\CustomerProfileService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CustomerWishlistController extends Controller
{
    public function __construct(private readonly CustomerProfileService $profileService) {}

    public function index(Request $request): JsonResponse
    {
        $products = $this->profileService->getWishlist($request->user('customer'));

        return response()->json(['data' => $products]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'product_id' => ['required', 'integer', 'exists:products,id'],
        ]);

        $this->profileService->addToWishlist($request->user('customer'), $validated['product_id']);

        return response()->json(['message' => 'Product added to wishlist.'], 201);
    }

    public function destroy(Request $request, int $productId): JsonResponse
    {
        $this->profileService->removeFromWishlist($request->user('customer'), $productId);

        return response()->json(['message' => 'Product removed from wishlist.']);
    }
}
