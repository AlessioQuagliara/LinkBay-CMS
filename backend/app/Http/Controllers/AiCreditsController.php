<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Services\AiCreditsService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Stripe\Stripe;

class AiCreditsController extends Controller
{
    public function __construct(private readonly AiCreditsService $credits) {}

    public function packages(): JsonResponse
    {
        return response()->json([
            'data' => AiCreditPackage::active()->get(),
        ]);
    }

    public function createCheckout(Request $request, AiCreditPackage $package): JsonResponse
    {
        $agency = $request->user()->agency
            ?? Agency::find($request->input('agency_id'));

        abort_unless($agency, 404, 'Agency not found');

        $session = $this->credits->createCheckoutSession($agency, $package);

        return response()->json(['checkout_url' => $session->url]);
    }

    public function success(Request $request): JsonResponse
    {
        Stripe::setApiKey(config('services.stripe.secret'));

        $sessionId = $request->query('session_id');
        $session = \Stripe\Checkout\Session::retrieve($sessionId);

        if ($session->payment_status !== 'paid') {
            return response()->json(['error' => 'Payment not completed'], 402);
        }

        $metadata = $session->metadata ?? (object) [];
        $agency = Agency::find($metadata->agency_id ?? null);
        $package = AiCreditPackage::find($metadata->package_id ?? null);

        if ($agency && $package) {
            $paymentIntentId = $session->payment_intent ?? $sessionId;

            // Idempotenza: il webhook checkout.session.completed potrebbe aver già creditato
            $alreadyCredited = AiCreditLedger::where('stripe_payment_intent_id', $paymentIntentId)->exists();
            if (!$alreadyCredited) {
                $this->credits->purchase($agency, $package, $paymentIntentId);
            }

            return response()->json([
                'message' => 'Credits added successfully',
                'balance' => $this->credits->getBalance($agency),
            ]);
        }

        return response()->json(['error' => 'Invalid session'], 422);
    }
}
