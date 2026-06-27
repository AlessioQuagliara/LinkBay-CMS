<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Http\Requests\Tenant\ApplyDiscountRequest;
use App\Http\Requests\Tenant\StoreCartItemRequest;
use App\Http\Requests\Tenant\UpdateCartItemRequest;
use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Services\Tenant\CartService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class CartController extends Controller
{
    public function __construct(private readonly CartService $cartService) {}

    public function store(Request $request): JsonResponse
    {
        $sessionId = $request->input('session_id', (string) Str::uuid());
        $customerId = $request->input('customer_id');

        $cart = $this->cartService->getOrCreateCart($sessionId, $customerId);
        $cart->loadMissing('cartItems.product');

        return response()->json([
            'data' => $cart,
            'meta' => $this->cartService->getCartSummary($cart),
        ], 201);
    }

    public function show(string $sessionId): JsonResponse
    {
        $cart = CartSession::where('session_id', $sessionId)
            ->with(['cartItems.product'])
            ->firstOrFail();

        return response()->json([
            'data' => $cart,
            'meta' => $this->cartService->getCartSummary($cart),
        ]);
    }

    public function addItem(StoreCartItemRequest $request, string $sessionId): JsonResponse
    {
        $cart = CartSession::where('session_id', $sessionId)->firstOrFail();

        $item = $this->cartService->addItem(
            $cart,
            $request->integer('product_id'),
            $request->integer('quantity'),
            $request->input('variant_id'),
        );

        return response()->json([
            'data' => $item->load('product'),
            'meta' => $this->cartService->getCartSummary($cart->fresh()),
        ], 201);
    }

    public function updateItem(UpdateCartItemRequest $request, string $sessionId, CartItem $item): JsonResponse
    {
        $cart = CartSession::where('session_id', $sessionId)->firstOrFail();

        abort_unless((int) $item->cart_session_id === (int) $cart->id, 403);

        $item = $this->cartService->updateItemQuantity($item, $request->integer('quantity'));

        return response()->json([
            'data' => $item->load('product'),
            'meta' => $this->cartService->getCartSummary($cart->fresh()),
        ]);
    }

    public function removeItem(string $sessionId, CartItem $item): JsonResponse
    {
        $cart = CartSession::where('session_id', $sessionId)->firstOrFail();

        abort_unless((int) $item->cart_session_id === (int) $cart->id, 403);

        $this->cartService->removeItem($item);

        return response()->json([
            'data' => null,
            'meta' => $this->cartService->getCartSummary($cart->fresh()),
        ]);
    }

    public function applyDiscount(ApplyDiscountRequest $request, string $sessionId): JsonResponse
    {
        $cart = CartSession::where('session_id', $sessionId)->firstOrFail();

        $result = $this->cartService->applyDiscount($cart, $request->string('code'));

        $status = $result['success'] ? 200 : 422;

        return response()->json([
            'data' => $result['discount'],
            'meta' => [
                'success' => $result['success'],
                'message' => $result['message'],
            ],
        ], $status);
    }
}
