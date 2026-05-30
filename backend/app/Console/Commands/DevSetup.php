<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Models\Central\Agency;
use App\Models\Central\User;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Hash;

/**
 * Creates super-admin and a test agency+owner pair for local development.
 * Safe to run multiple times — uses firstOrCreate for idempotency.
 */
class DevSetup extends Command
{
    protected $signature = 'dev:setup
        {--admin-email=admin@linkbay-cms.test : Email super admin}
        {--admin-password=password : Password super admin}
        {--agency-slug=test-agency : Slug agenzia di test}
        {--agency-email=owner@test-agency.test : Email titolare agenzia}
        {--agency-password=password : Password titolare agenzia}';

    protected $description = 'Crea super admin e agenzia test per sviluppo locale (idempotente)';

    public function handle(): int
    {
        if (app()->isProduction()) {
            $this->error('Questo comando non può girare in produzione.');
            return self::FAILURE;
        }

        $this->info('── Super Admin ─────────────────────────────────────────');

        $adminEmail    = $this->option('admin-email');
        $adminPassword = $this->option('admin-password');

        $admin = User::firstOrCreate(
            ['email' => $adminEmail],
            [
                'name'           => 'LinkBayCMS Admin',
                'email'          => $adminEmail,
                'password'       => Hash::make($adminPassword),
                'is_super_admin' => true,
            ]
        );

        if ($admin->wasRecentlyCreated) {
            $this->info("  Creato: {$adminEmail}");
        } else {
            // Update password in case it changed
            $admin->update(['password' => Hash::make($adminPassword), 'is_super_admin' => true]);
            $this->line("  Già esistente, password aggiornata: {$adminEmail}");
        }

        $this->info("  Password: {$adminPassword}");
        $this->info("  URL:      " . config('app.url') . '/linkbay-admin/login');

        $this->info('');
        $this->info('── Agenzia Test ────────────────────────────────────────');

        $agencySlug    = $this->option('agency-slug');
        $agencyEmail   = $this->option('agency-email');
        $agencyPassword = $this->option('agency-password');
        $centralDomain = config('app.central_domain', 'linkbay-cms.com');

        $agency = Agency::firstOrCreate(
            ['slug' => $agencySlug],
            [
                'name'         => 'Test Agency',
                'brand_name'   => 'Test Agency',
                'slug'         => $agencySlug,
                'status'       => 'active',
                'billing_type' => 'monthly',
            ]
        );

        if ($agency->wasRecentlyCreated) {
            $this->info("  Agenzia creata: {$agencySlug}");
        } else {
            $this->line("  Agenzia già esistente: {$agencySlug}");
        }

        $owner = User::firstOrCreate(
            ['email' => $agencyEmail],
            [
                'name'           => 'Agency Owner',
                'email'          => $agencyEmail,
                'password'       => Hash::make($agencyPassword),
                'is_super_admin' => false,
            ]
        );

        if ($owner->wasRecentlyCreated) {
            $this->info("  Utente creato: {$agencyEmail}");
        } else {
            $owner->update(['password' => Hash::make($agencyPassword)]);
            $this->line("  Utente già esistente, password aggiornata: {$agencyEmail}");
        }

        // Link owner to agency if not already linked
        if (!$agency->owner_user_id) {
            $agency->update(['owner_user_id' => $owner->id]);
            $this->info("  Owner collegato all'agenzia");
        } elseif ((int) $agency->owner_user_id !== (int) $owner->id) {
            $this->warn("  L'agenzia ha già un owner diverso (ID: {$agency->owner_user_id}). Non aggiornato.");
        }

        $this->info("  Password: {$agencyPassword}");
        $this->info("  URL:      http://{$agencySlug}.{$centralDomain}/dashboard/login");

        $this->info('');
        $this->info('✅  Setup completato. Pronto per il test.');
        $this->table(
            ['Ruolo', 'Email', 'Password', 'URL Login'],
            [
                ['Super Admin', $adminEmail, $adminPassword, config('app.url') . '/linkbay-admin/login'],
                ['Agency Owner', $agencyEmail, $agencyPassword, "http://{$agencySlug}.{$centralDomain}/dashboard/login"],
            ]
        );

        return self::SUCCESS;
    }
}
