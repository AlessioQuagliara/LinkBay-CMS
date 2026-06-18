<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Jobs\ProvisionTenantDatabaseJob;
use App\Mail\StoreAdminWelcomeMail;
use App\Models\Central\Tenant;
use App\Services\TenantProvisioningService;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers the store admin welcome email sent after successful provisioning.
 *
 * All tests use a mocked TenantProvisioningService so no real tenant DB
 * is set up; we test the Job's email-sending logic in isolation.
 */
class StoreAdminWelcomeMailTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    /**
     * Insert a tenant row via raw SQL to bypass stancl's database-creation hooks.
     */
    private function makeTenant(?string $id = null, string $name = 'My Store'): Tenant
    {
        self::$seq++;
        $tenantId = $id ?? 'store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $tenantId,
            'name' => $name,
            'status' => 'active',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return Tenant::find($tenantId);
    }

    private function mockService(?string $returnToken = 'test-reset-token'): TenantProvisioningService
    {
        $mock = $this->createMock(TenantProvisioningService::class);
        $mock->method('initializeDatabase')->willReturn($returnToken);

        return $mock;
    }

    private function mockServiceThrows(): TenantProvisioningService
    {
        $mock = $this->createMock(TenantProvisioningService::class);
        $mock->method('initializeDatabase')->willThrowException(new \RuntimeException('DB error'));

        return $mock;
    }

    // ── Mail class tests ──────────────────────────────────────────────────────

    public function test_mailable_has_correct_subject(): void
    {
        $mail = new StoreAdminWelcomeMail(
            storeName: 'ACME Shop',
            storeUrl: 'https://acme.store.test/admin',
            resetUrl: 'https://acme.store.test/admin/password-reset/reset?token=abc&email=admin%40acme.com',
        );

        $this->assertEquals('Welcome to your new store — ACME Shop', $mail->envelope()->subject);
    }

    public function test_mailable_content_contains_reset_url(): void
    {
        Mail::fake();

        $mail = new StoreAdminWelcomeMail(
            storeName: 'ACME Shop',
            storeUrl: 'https://acme.store.test/admin',
            resetUrl: 'https://acme.store.test/admin/password-reset/reset?token=abc&email=admin%40acme.com',
        );

        $content = $mail->content();

        $this->assertEquals('emails.store-admin-welcome', $content->markdown);
        $this->assertStringContainsString(
            'https://acme.store.test/admin/password-reset/reset',
            $content->with['resetUrl'],
        );
    }

    public function test_mailable_content_contains_store_url(): void
    {
        $mail = new StoreAdminWelcomeMail(
            storeName: 'ACME Shop',
            storeUrl: 'https://acme.store.test/admin',
            resetUrl: 'https://acme.store.test/admin/password-reset/reset?token=abc&email=foo',
        );

        $this->assertStringContainsString('https://acme.store.test/admin', $mail->content()->with['storeUrl']);
    }

    // ── Job email-dispatch tests ───────────────────────────────────────────────

    public function test_welcome_email_sent_to_admin_after_successful_provisioning(): void
    {
        Mail::fake();

        $tenant = $this->makeTenant('acmestore', 'ACME Shop');
        $service = $this->mockService('sometoken');

        $job = new ProvisionTenantDatabaseJob($tenant->id, 'admin@acme.com');
        $job->handle($service);

        Mail::assertSent(StoreAdminWelcomeMail::class, function ($mail) {
            return $mail->hasTo('admin@acme.com');
        });
    }

    public function test_welcome_email_not_sent_when_admin_email_is_null(): void
    {
        Mail::fake();

        $tenant = $this->makeTenant();
        $service = $this->mockService(null);

        $job = new ProvisionTenantDatabaseJob($tenant->id, null);
        $job->handle($service);

        Mail::assertNotSent(StoreAdminWelcomeMail::class);
    }

    public function test_welcome_email_not_sent_when_provisioning_fails(): void
    {
        Mail::fake();

        $tenant = $this->makeTenant();
        $service = $this->mockServiceThrows();

        $this->expectException(\RuntimeException::class);

        $job = new ProvisionTenantDatabaseJob($tenant->id, 'admin@store.com');
        $job->handle($service);

        Mail::assertNotSent(StoreAdminWelcomeMail::class);
    }

    public function test_welcome_email_not_sent_when_tenant_not_found(): void
    {
        Mail::fake();

        $service = $this->mockService();

        $job = new ProvisionTenantDatabaseJob('nonexistent-tenant', 'admin@store.com');
        $job->handle($service);

        Mail::assertNotSent(StoreAdminWelcomeMail::class);
    }

    public function test_reset_url_contains_token_and_email(): void
    {
        Mail::fake();

        $tenant = $this->makeTenant('myshop', 'My Shop');
        $service = $this->mockService('reset-token-abc');

        $job = new ProvisionTenantDatabaseJob($tenant->id, 'owner@myshop.com');
        $job->handle($service);

        Mail::assertSent(StoreAdminWelcomeMail::class, function ($mail) {
            return str_contains($mail->resetUrl, 'reset-token-abc')
                && str_contains($mail->resetUrl, urlencode('owner@myshop.com'));
        });
    }

    public function test_reset_url_uses_tenant_subdomain(): void
    {
        Mail::fake();

        $tenant = $this->makeTenant('boutique', 'Boutique Store');
        $service = $this->mockService('mytoken');

        $job = new ProvisionTenantDatabaseJob($tenant->id, 'admin@boutique.com');
        $job->handle($service);

        $storeDomain = config('app.store_domain', 'yoursite-linkbay-cms.com');

        Mail::assertSent(StoreAdminWelcomeMail::class, function ($mail) use ($storeDomain) {
            return str_contains($mail->resetUrl, 'boutique.'.$storeDomain);
        });
    }
}
