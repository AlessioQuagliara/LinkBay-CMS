<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Mail\Tenant\CustomerWelcomeMail;
use App\Mail\Tenant\OrderConfirmedMail;
use App\Models\Tenant\BrandSetting;
use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use Illuminate\Support\Facades\Mail;
use Tests\TenantTestCase;

/**
 * Tests for tenant transactional mail classes.
 *
 * No factories exist for tenant models, so records are created via fill + save.
 * BrandSetting::current() works because brand_settings is included in tenant migrations
 * and the singleton uses firstOrCreate() with a fallback tenant_id.
 */
class TenantMailTest extends TenantTestCase
{
    private function makeCustomer(string $email = 'buyer@example.com', string $name = 'Test Buyer'): Customer
    {
        $customer = new Customer([
            'name' => $name,
            'email' => $email,
            'password' => bcrypt('secret'),
            'status' => 'active',
        ]);
        $customer->save();

        return $customer;
    }

    private function makeOrder(Customer $customer, float $total = 99.90): Order
    {
        $order = new Order([
            'customer_id' => $customer->id,
            'status' => Order::STATUS_CONFIRMED,
            'payment_status' => Order::PAYMENT_STATUS_PAID,
            'total' => $total,
            'subtotal' => $total,
            'discount_total' => 0,
            'shipping_total' => 0,
        ]);
        $order->save();

        return $order;
    }

    // ── OrderConfirmedMail ────────────────────────────────────────────────────

    public function test_order_confirmed_mail_has_correct_subject(): void
    {
        $customer = $this->makeCustomer();
        $order = $this->makeOrder($customer);

        $mail = new OrderConfirmedMail($order);
        $orderNumber = '#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT);

        $this->assertStringContainsString("Conferma ordine {$orderNumber}", $mail->envelope()->subject);
    }

    public function test_order_confirmed_mail_is_sent_to_customer_email(): void
    {
        $customer = $this->makeCustomer('shopper@test.com');
        $order = $this->makeOrder($customer);

        $mail = new OrderConfirmedMail($order);

        $this->assertStringContainsString('shopper@test.com', $mail->envelope()->to[0]->address);
    }

    public function test_order_confirmed_mail_uses_correct_view(): void
    {
        $customer = $this->makeCustomer();
        $order = $this->makeOrder($customer);

        $mail = new OrderConfirmedMail($order);

        $this->assertEquals('emails.tenant.order-confirmed', $mail->content()->view);
    }

    public function test_order_confirmed_mail_is_queued_on_emails_queue(): void
    {
        Mail::fake();

        $customer = $this->makeCustomer();
        $order = $this->makeOrder($customer);

        Mail::to($customer->email)->queue(new OrderConfirmedMail($order));

        Mail::assertQueued(OrderConfirmedMail::class, function (OrderConfirmedMail $mail): bool {
            return $mail->queue === 'emails';
        });
    }

    public function test_order_confirmed_mail_subject_includes_store_name(): void
    {
        BrandSetting::query()->updateOrCreate(
            ['tenant_id' => 'default'],
            ['store_name' => 'Boutique Glamour', 'primary_color' => '#ff0000'],
        );

        $customer = $this->makeCustomer();
        $order = $this->makeOrder($customer);

        $mail = new OrderConfirmedMail($order);

        $this->assertStringContainsString('Boutique Glamour', $mail->envelope()->subject);
    }

    public function test_order_confirmed_mail_order_number_is_padded(): void
    {
        $customer = $this->makeCustomer();
        $order = $this->makeOrder($customer);

        $mail = new OrderConfirmedMail($order);

        $this->assertEquals('#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT), $mail->orderNumber);
    }

    // ── CustomerWelcomeMail ───────────────────────────────────────────────────

    public function test_customer_welcome_mail_has_correct_subject(): void
    {
        BrandSetting::query()->updateOrCreate(
            ['tenant_id' => 'default'],
            ['store_name' => 'My Boutique', 'primary_color' => '#000000'],
        );

        $customer = $this->makeCustomer();
        $mail = new CustomerWelcomeMail($customer);

        $this->assertEquals('Benvenuto/a in My Boutique!', $mail->envelope()->subject);
    }

    public function test_customer_welcome_mail_is_sent_to_customer_email(): void
    {
        $customer = $this->makeCustomer('new@store.com');
        $mail = new CustomerWelcomeMail($customer);

        $this->assertEquals('new@store.com', $mail->envelope()->to[0]->address);
    }

    public function test_customer_welcome_mail_uses_correct_view(): void
    {
        $customer = $this->makeCustomer();
        $mail = new CustomerWelcomeMail($customer);

        $this->assertEquals('emails.tenant.customer-welcome', $mail->content()->view);
    }

    public function test_customer_welcome_mail_is_queued_on_emails_queue(): void
    {
        Mail::fake();

        $customer = $this->makeCustomer();

        Mail::to($customer->email)->queue(new CustomerWelcomeMail($customer));

        Mail::assertQueued(CustomerWelcomeMail::class, function (CustomerWelcomeMail $mail): bool {
            return $mail->queue === 'emails';
        });
    }

    public function test_customer_welcome_mail_subject_falls_back_to_app_name_when_store_name_empty(): void
    {
        BrandSetting::query()->updateOrCreate(
            ['tenant_id' => 'default'],
            ['store_name' => '', 'primary_color' => '#000000'],
        );

        $customer = $this->makeCustomer();
        $mail = new CustomerWelcomeMail($customer);

        $expectedName = config('app.name');
        $this->assertStringContainsString($expectedName, $mail->envelope()->subject);
    }

    public function test_customer_welcome_mail_brand_is_loaded(): void
    {
        $customer = $this->makeCustomer();
        $mail = new CustomerWelcomeMail($customer);

        $this->assertInstanceOf(BrandSetting::class, $mail->brand);
    }
}
