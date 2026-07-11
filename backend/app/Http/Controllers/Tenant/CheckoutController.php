<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Http\Requests\Tenant\ConfirmPaymentRequest;
use App\Http\Requests\Tenant\InitiateCheckoutRequest;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use App\Services\Tenant\CheckoutService;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Http\JsonResponse;
use RuntimeException;

class CheckoutController extends Controller
{
    public function __construct(private readonly CheckoutService $checkoutService) {}

    public function initiate(InitiateCheckoutRequest $request): JsonResponse
    {
        $cart = CartSession::where('session_id', $request->string('cart_session_id'))
            ->with('cartItems')
            ->first();

        abort_if($cart === null, 404, 'Sessione carrello non trovata o scaduta. Ricarica la pagina e riprova.');
        abort_if($cart->cartItems->isEmpty(), 422, 'Il carrello è vuoto.');

        try {
            $checkout = $this->checkoutService->initiate(
                $cart,
                $request->input('shipping_address'),
                $request->integer('shipping_method_id'),
            );
        } catch (ModelNotFoundException $e) {
            abort(422, $e->getMessage());
        }

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

        try {
            $clientSecret = $this->checkoutService->createPaymentIntent($checkout);
        } catch (RuntimeException $e) {
            abort(502, $e->getMessage());
        }

        return response()->json([
            'data' => ['client_secret' => $clientSecret],
            'meta' => ['checkout_id' => $checkout->id],
        ]);
    }

    public function confirm(ConfirmPaymentRequest $request, CheckoutSession $checkout): JsonResponse
    {
        try {
            $confirmed = $this->checkoutService->confirmPayment($request->string('payment_intent_id')->toString());
            $order = $this->checkoutService->convertToOrder($confirmed);
        } catch (ModelNotFoundException $e) {
            abort(404, $e->getMessage());
        } catch (RuntimeException $e) {
            abort(422, $e->getMessage());
        }

        return response()->json([
            'data' => $order->load('items'),
            'meta' => ['message' => 'Ordine creato con successo.'],
        ]);
    }

    /**
     * Public order lookup scoped by checkout session id, not customer auth —
     * the checkout/success page must work for guest checkouts too, so it
     * can't call the authenticated /api/account/orders/{id} route. Knowing
     * the checkout session id (only ever handed to the browser that completed
     * that specific checkout) is the access proof here.
     */
    public function order(CheckoutSession $checkout): JsonResponse
    {
        $order = $this->checkoutService->findOrderFor($checkout);

        abort_if($order === null, 404, 'Nessun ordine trovato per questo checkout.');

        return response()->json([
            'data' => $order->load('items'),
        ]);
    }
}
