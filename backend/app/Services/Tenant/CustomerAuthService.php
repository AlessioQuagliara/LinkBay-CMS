<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Events\Tenant\CustomerRegistered;
use App\Models\Tenant\Customer;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Auth\Events\Registered;
use Illuminate\Auth\Events\Verified;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Laravel\Sanctum\NewAccessToken;

class CustomerAuthService
{
    /**
     * Register a new customer and issue an access token (auto-login).
     * Fires Registered event (triggers email verification).
     *
     * @param  array{name: string, email: string, password: string, phone?: string, accepts_marketing?: bool}  $data
     *
     * @throws ValidationException if email already exists in this tenant
     */
    public function register(array $data): NewAccessToken
    {
        if (Customer::where('email', $data['email'])->exists()) {
            throw ValidationException::withMessages([
                'email' => ['This email is already registered.'],
            ]);
        }

        $customer = Customer::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
            'phone' => $data['phone'] ?? null,
            'accepts_marketing' => $data['accepts_marketing'] ?? false,
            'status' => 'active',
        ]);

        event(new Registered($customer));
        event(new CustomerRegistered($customer));

        $customer->update(['last_login_at' => now()]);

        return $customer->createToken('storefront');
    }

    /**
     * Attempt login and issue a Sanctum access token for the storefront.
     */
    public function login(string $email, string $password): NewAccessToken|false
    {
        $customer = Customer::where('email', $email)->where('status', 'active')->first();

        if (! $customer || ! Hash::check($password, $customer->password)) {
            return false;
        }

        $customer->update(['last_login_at' => now()]);

        return $customer->createToken('storefront');
    }

    /**
     * Revoke the access token used to authenticate the current request.
     */
    public function logout(Customer $customer): void
    {
        $customer->currentAccessToken()?->delete();
    }

    /**
     * Send a password reset link to the customer's email address.
     */
    public function sendPasswordResetLink(string $email): bool
    {
        $status = Password::broker('customers')->sendResetLink(['email' => $email]);

        return $status === Password::RESET_LINK_SENT;
    }

    /**
     * Reset the customer password using a valid token.
     *
     * @throws ValidationException on invalid token or email
     */
    public function resetPassword(string $token, string $email, string $password): bool
    {
        $status = Password::broker('customers')->reset(
            ['email' => $email, 'password' => $password, 'token' => $token],
            function (Customer $customer, string $newPassword): void {
                $customer->forceFill([
                    'password' => Hash::make($newPassword),
                    'remember_token' => Str::random(60),
                ])->save();

                event(new PasswordReset($customer));
            }
        );

        return $status === Password::PASSWORD_RESET;
    }

    /**
     * Dispatch the email verification notification for the given customer.
     */
    public function sendEmailVerification(Customer $customer): void
    {
        $customer->sendEmailVerificationNotification();
    }

    /**
     * Mark a customer's email as verified after validating the signed hash.
     */
    public function verifyEmail(Customer $customer, string $hash): bool
    {
        if (! hash_equals(sha1($customer->getEmailForVerification()), $hash)) {
            return false;
        }

        if ($customer->hasVerifiedEmail()) {
            return true;
        }

        $customer->markEmailAsVerified();
        event(new Verified($customer));

        return true;
    }
}
