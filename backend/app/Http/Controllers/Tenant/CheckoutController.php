<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Http\Requests\Tenant\ConfirmPaymentRequest;
use App\Http\Requests\Tenant\InitiateCheckoutRequest;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use App\Services\Tenant\CheckoutService;
use Illuminate\Http\JsonResponse;

class CheckoutController extends Controller
{
    public function __construct(private readonly CheckoutService $checkoutService) {}

    public function initiate(InitiateCheckoutRequest $request): JsonResponse
    {
        $cart = CartSession::where('session_id', $request->string('cart_session_id'))
            ->with('cartItems')
            ->firstOrFail();

        abort_if($cart->cartItems->isEmpty(), 422, 'Il carrello è vuoto.');

        $checkout = $this->checkoutService->initiate(
            $cart,
            $request->input('shipping_address'),
            $request->integer('shipping_method_id'),
        );

        return response()->json([
            'data' => $checkout->load(['shippingMethod', 'discountCode']),
            'meta' => $this->checkoutService->calculateTotals($checkout),
        ], 201);
    }

    public function show(CheckoutSession $checkout): JsonResponse
    {
        return response()->json([
            'data' => $checkout->load(['cartSession.cartItems.product', 'shippingMethod', 'discountCode']),
            'meta' => $this->checkoutService->calculateTotals($checkout),
        ]);
    }

    public function createPaymentIntent(CheckoutSession $checkout): JsonResponse
    {
        abort_if(
            $checkout->status === CheckoutSession::STATUS_COMPLETED,
            422,
            'Checkout già completato.'
        );

        $clientSecret = $this->checkoutService->createPaymentIntent($checkout);

        return response()->json([
            'data' => ['client_secret' => $clientSecret],
            'meta' => ['checkout_id' => $checkout->id],
        ]);
    }

    public function confirm(ConfirmPaymentRequest $request, CheckoutSession $checkout): JsonResponse
    {
        $checkout = $this->checkoutService->confirmPayment($request->string('payment_intent_id'));
        $order = $this->checkoutService->convertToOrder($checkout);

        return response()->json([
            'data' => $order->load('items'),
            'meta' => ['message' => 'Ordine creato con successo.'],
        ]);
    }
}
