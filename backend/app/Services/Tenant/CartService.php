<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Product;
use Illuminate\Support\Facades\DB;

class CartService
{
    public function getOrCreateCart(string $sessionId, ?int $customerId = null): CartSession
    {
        return CartSession::firstOrCreate(
            ['session_id' => $sessionId],
            [
                'customer_id' => $customerId,
                'expires_at' => now()->addDays(30),
            ]
        );
    }

    public function addItem(CartSession $cart, int $productId, int $quantity, ?int $variantId = null): CartItem
    {
        $product = Product::findOrFail($productId);

        $existingItem = $cart->cartItems()
            ->where('product_id', $productId)
            ->where('variant_id', $variantId)
            ->first();

        if ($existingItem) {
            $existingItem->increment('quantity', $quantity);

            return $existingItem->fresh();
        }

        return $cart->cartItems()->create([
            'product_id' => $productId,
            'variant_id' => $variantId,
            'quantity' => $quantity,
            'unit_price' => $product->price,
        ]);
    }

    public function updateItemQuantity(CartItem $item, int $quantity): CartItem
    {
        $item->update(['quantity' => $quantity]);

        return $item->fresh();
    }

    public function removeItem(CartItem $item): void
    {
        $item->delete();
    }

    /**
     * @return array{success: bool, discount: DiscountCode|null, message: string}
     */
    public function applyDiscount(CartSession $cart, string $code): array
    {
        $discount = DiscountCode::where('code', strtoupper($code))->first();

        if (! $discount) {
            return ['success' => false, 'discount' => null, 'message' => 'Codice sconto non valido.'];
        }

        if (! $discount->isValid()) {
            return ['success' => false, 'discount' => null, 'message' => 'Codice sconto scaduto o non più disponibile.'];
        }

        $summary = $this->getCartSummary($cart);

        if ($discount->minimum_amount && $summary['subtotal'] < (float) $discount->minimum_amount) {
            return [
                'success' => false,
                'discount' => null,
                'message' => "Importo minimo richiesto: €{$discount->minimum_amount}",
            ];
        }

        return ['success' => true, 'discount' => $discount, 'message' => 'Sconto applicato.'];
    }

    /**
     * @return array{subtotal: float, discount: float, shipping: float, tax: float, total: float}
     */
    public function getCartSummary(CartSession $cart): array
    {
        $cart->loadMissing('cartItems.product');

        $subtotal = $cart->cartItems->sum(fn (CartItem $item) => (float) $item->unit_price * $item->quantity);

        return [
            'subtotal' => round($subtotal, 2),
            'discount' => 0.0,
            'shipping' => 0.0,
            'tax' => 0.0,
            'total' => round($subtotal, 2),
        ];
    }

    public function mergeGuestCart(string $guestSessionId, int $customerId): void
    {
        $guestCart = CartSession::where('session_id', $guestSessionId)->first();

        if (! $guestCart) {
            return;
        }

        $customerCart = CartSession::where('customer_id', $customerId)->latest()->first();

        if (! $customerCart) {
            $guestCart->update(['customer_id' => $customerId]);

            return;
        }

        DB::transaction(function () use ($guestCart, $customerCart) {
            foreach ($guestCart->cartItems as $guestItem) {
                $existing = $customerCart->cartItems()
                    ->where('product_id', $guestItem->product_id)
                    ->where('variant_id', $guestItem->variant_id)
                    ->first();

                if ($existing) {
                    $existing->increment('quantity', $guestItem->quantity);
                } else {
                    $customerCart->cartItems()->create($guestItem->only([
                        'product_id', 'variant_id', 'quantity', 'unit_price', 'metadata',
                    ]));
                }
            }

            $guestCart->delete();
        });
    }
}
