<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Account;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Customer;
use App\Services\Tenant\CustomerAuthService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rules\Password;

class CustomerAuthController extends Controller
{
    public function __construct(private readonly CustomerAuthService $authService) {}

    public function register(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'email', 'max:255'],
            'password' => ['required', 'confirmed', Password::min(8)],
            'phone' => ['nullable', 'string', 'max:30'],
            'accepts_marketing' => ['boolean'],
        ]);

        $customer = $this->authService->register($validated);

        return response()->json([
            'data' => $customer->only(['id', 'name', 'email', 'phone']),
            'message' => 'Registration successful. Please verify your email.',
        ], 201);
    }

    public function login(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        $customer = $this->authService->login($validated['email'], $validated['password']);

        if (! $customer) {
            return response()->json(['message' => 'Invalid credentials.'], 401);
        }

        return response()->json([
            'data' => $customer->only(['id', 'name', 'email']),
            'message' => 'Login successful.',
        ]);
    }

    public function logout(): JsonResponse
    {
        $this->authService->logout();

        return response()->json(['message' => 'Logged out successfully.']);
    }

    public function forgotPassword(Request $request): JsonResponse
    {
        $request->validate(['email' => ['required', 'email']]);

        $this->authService->sendPasswordResetLink($request->string('email')->value());

        return response()->json(['message' => 'If that email exists, a reset link has been sent.']);
    }

    public function resetPassword(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'token' => ['required', 'string'],
            'email' => ['required', 'email'],
            'password' => ['required', 'confirmed', Password::min(8)],
        ]);

        $success = $this->authService->resetPassword(
            $validated['token'],
            $validated['email'],
            $validated['password'],
        );

        if (! $success) {
            return response()->json(['message' => 'Invalid or expired reset token.'], 422);
        }

        return response()->json(['message' => 'Password reset successfully.']);
    }

    public function verifyEmail(Request $request, int $id, string $hash): JsonResponse
    {
        $customer = Customer::findOrFail($id);

        $verified = $this->authService->verifyEmail($customer, $hash);

        if (! $verified) {
            return response()->json(['message' => 'Invalid verification link.'], 422);
        }

        return response()->json(['message' => 'Email verified successfully.']);
    }
}
