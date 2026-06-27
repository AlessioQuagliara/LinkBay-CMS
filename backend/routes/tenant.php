<?php

declare(strict_types=1);

use App\Http\Controllers\Tenant\Account\CustomerAddressController;
use App\Http\Controllers\Tenant\Account\CustomerAuthController;
use App\Http\Controllers\Tenant\Account\CustomerOrderController;
use App\Http\Controllers\Tenant\Account\CustomerProfileController;
use App\Http\Controllers\Tenant\Account\CustomerWishlistController;
use App\Http\Controllers\Tenant\AnalyticsController;
use App\Http\Controllers\Tenant\CartController;
use App\Http\Controllers\Tenant\CategoryController;
use App\Http\Controllers\Tenant\CheckoutController;
use App\Http\Controllers\Tenant\CustomerController;
use App\Http\Controllers\Tenant\DiscountCodeController;
use App\Http\Controllers\Tenant\OrderController;
use App\Http\Controllers\Tenant\ProductController;
use App\Http\Controllers\Tenant\Storefront\BrandSettingController;
use App\Http\Controllers\Tenant\Storefront\LanguageController;
use App\Http\Controllers\Tenant\Storefront\MediaController;
use App\Http\Controllers\Tenant\Storefront\StorePageController;
use App\Http\Controllers\Tenant\TenantImpersonateController;
use App\Http\Controllers\Tenant\TenantStripeWebhookController;
use App\Http\Middleware\AuthenticateCustomer;
use App\Http\Middleware\RedirectIfCustomerAuthenticated;
use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken;
use Illuminate\Support\Facades\Route;
use Stancl\Tenancy\Middleware\InitializeTenancyByDomain;
use Stancl\Tenancy\Middleware\PreventAccessFromCentralDomains;

Route::middleware([
    'api',
    InitializeTenancyByDomain::class,
    PreventAccessFromCentralDomains::class,
])->prefix('api/v1')->group(function () {

    Route::middleware('auth:sanctum')->group(function () {

        // Products
        Route::get('/products', [ProductController::class, 'index']);
        Route::post('/products', [ProductController::class, 'store']);
        Route::get('/products/{product}', [ProductController::class, 'show']);
        Route::put('/products/{product}', [ProductController::class, 'update']);
        Route::delete('/products/{product}', [ProductController::class, 'destroy']);

        // Orders
        Route::get('/orders', [OrderController::class, 'index']);
        Route::get('/orders/{order}', [OrderController::class, 'show']);
        Route::patch('/orders/{order}/status', [OrderController::class, 'updateStatus']);

        // Customers
        Route::get('/customers', [CustomerController::class, 'index']);
        Route::post('/customers', [CustomerController::class, 'store']);
        Route::get('/customers/{customer}', [CustomerController::class, 'show']);
        Route::put('/customers/{customer}', [CustomerController::class, 'update']);
        Route::delete('/customers/{customer}', [CustomerController::class, 'destroy']);

        // Discount Codes
        Route::get('/discount-codes', [DiscountCodeController::class, 'index']);
        Route::post('/discount-codes', [DiscountCodeController::class, 'store']);
        Route::put('/discount-codes/{discountCode}', [DiscountCodeController::class, 'update']);
        Route::delete('/discount-codes/{discountCode}', [DiscountCodeController::class, 'destroy']);

        // Analytics
        Route::get('/analytics/summary', [AnalyticsController::class, 'summary']);
    });
});

// ─── Customer account area — /api/account ────────────────────────────────────
Route::middleware([
    'api',
    InitializeTenancyByDomain::class,
    PreventAccessFromCentralDomains::class,
])->prefix('api/account')->group(function () {

    // Guest-only routes (redirect if already authenticated)
    Route::middleware(RedirectIfCustomerAuthenticated::class)->group(function () {
        Route::post('/register', [CustomerAuthController::class, 'register']);
        Route::post('/login', [CustomerAuthController::class, 'login']);
        Route::post('/password/forgot', [CustomerAuthController::class, 'forgotPassword']);
        Route::post('/password/reset', [CustomerAuthController::class, 'resetPassword']);
    });

    // Email verification (no auth required — link is signed)
    Route::get('/email/verify/{id}/{hash}', [CustomerAuthController::class, 'verifyEmail'])
        ->name('customer.verification.verify');

    // Authenticated routes
    Route::middleware(AuthenticateCustomer::class)->group(function () {
        Route::post('/logout', [CustomerAuthController::class, 'logout']);

        Route::get('/profile', [CustomerProfileController::class, 'show']);
        Route::put('/profile', [CustomerProfileController::class, 'update']);

        Route::get('/addresses', [CustomerAddressController::class, 'index']);
        Route::post('/addresses', [CustomerAddressController::class, 'store']);
        Route::put('/addresses/{id}', [CustomerAddressController::class, 'update']);
        Route::delete('/addresses/{id}', [CustomerAddressController::class, 'destroy']);
        Route::post('/addresses/{id}/set-default', [CustomerAddressController::class, 'setDefault']);

        Route::get('/orders', [CustomerOrderController::class, 'index']);
        Route::get('/orders/{id}', [CustomerOrderController::class, 'show']);

        Route::get('/wishlist', [CustomerWishlistController::class, 'index']);
        Route::post('/wishlist', [CustomerWishlistController::class, 'store']);
        Route::delete('/wishlist/{productId}', [CustomerWishlistController::class, 'destroy']);
    });
});

// ─── Public Storefront — /api/store ─────────────────────────────────────────
Route::middleware([
    'api',
    InitializeTenancyByDomain::class,
    PreventAccessFromCentralDomains::class,
])->prefix('api/store')->group(function () {

    // Catalog
    Route::get('/products', [ProductController::class, 'storefront']);
    Route::get('/products/{product:slug}', [ProductController::class, 'show']);
    Route::get('/categories', [CategoryController::class, 'index']);
    Route::get('/categories/{slug}/products', [CategoryController::class, 'products']);

    // Cart
    Route::post('/cart', [CartController::class, 'store']);
    Route::get('/cart/{sessionId}', [CartController::class, 'show']);
    Route::post('/cart/{sessionId}/items', [CartController::class, 'addItem']);
    Route::patch('/cart/{sessionId}/items/{item}', [CartController::class, 'updateItem']);
    Route::delete('/cart/{sessionId}/items/{item}', [CartController::class, 'removeItem']);
    Route::post('/cart/{sessionId}/discount', [CartController::class, 'applyDiscount']);

    // Checkout
    Route::post('/checkout', [CheckoutController::class, 'initiate']);
    Route::get('/checkout/{checkout}', [CheckoutController::class, 'show']);
    Route::post('/checkout/{checkout}/payment-intent', [CheckoutController::class, 'createPaymentIntent']);
    Route::post('/checkout/{checkout}/confirm', [CheckoutController::class, 'confirm']);

    // Brand & appearance
    Route::get('/brand', [BrandSettingController::class, 'show']);
    Route::get('/brand/css', [BrandSettingController::class, 'css']);

    // Languages
    Route::get('/languages', [LanguageController::class, 'index']);

    // Pages (builder)
    Route::get('/pages/{slug}', [StorePageController::class, 'show']);

    // Media
    Route::get('/media/{id}', [MediaController::class, 'show']);
});

Route::middleware([
    'web',
    InitializeTenancyByDomain::class,
    PreventAccessFromCentralDomains::class,
])->group(function () {
    Route::get('/_impersonate/{token}', [TenantImpersonateController::class, 'handle'])
        ->name('tenant.impersonate');
});

// ─── Stripe webhooks — tenant-scoped (no CSRF, verify via Stripe signature) ──
Route::middleware([
    InitializeTenancyByDomain::class,
    PreventAccessFromCentralDomains::class,
])->post('/webhooks/stripe', [TenantStripeWebhookController::class, 'handle'])
    ->name('tenant.webhooks.stripe')
    ->withoutMiddleware([VerifyCsrfToken::class]);
