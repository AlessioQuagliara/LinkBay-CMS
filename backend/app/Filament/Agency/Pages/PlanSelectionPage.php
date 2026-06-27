<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\Plan;
use App\Services\AgencyBillingService;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Support\Collection;

class PlanSelectionPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-squares-2x2';

    protected static ?string $navigationLabel = 'Piani';

    protected static ?string $slug = 'billing/plans';

    protected string $view = 'filament.agency.pages.plan-selection';

    protected static bool $shouldRegisterNavigation = false;

    public string $interval = 'monthly';

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwner() ?? false;
    }

    // ── Data ──────────────────────────────────────────────────────────────────

    public function plans(): Collection
    {
        return Plan::where('is_active', true)
            ->orderBy('sort_order')
            ->orderBy('price')
            ->get();
    }

    public function currentPlanId(): ?int
    {
        return $this->agency()?->plan_id;
    }

    public function toggleInterval(string $interval): void
    {
        $this->interval = in_array($interval, ['monthly', 'yearly']) ? $interval : 'monthly';
    }

    /**
     * Displays the price for the given plan and the current interval.
     */
    public function displayPrice(Plan $plan): string
    {
        $price = $plan->priceForInterval($this->interval);
        $suffix = $this->interval === 'yearly' ? '/anno' : '/mese';

        return '€'.number_format($price, 2, ',', '.').$suffix;
    }

    public function yearlySaving(Plan $plan): ?string
    {
        if ($this->interval !== 'yearly' || (float) $plan->price <= 0) {
            return null;
        }

        $monthly = (float) $plan->price * 12;
        $yearly = $plan->priceForInterval('yearly');
        $saving = $monthly - $yearly;

        return $saving > 0 ? '€'.number_format($saving, 0, ',', '.').' risparmio' : null;
    }

    // ── Actions ───────────────────────────────────────────────────────────────

    public function selectPlan(int $planId): void
    {
        $agency = $this->agency();
        $plan = Plan::find($planId);

        if (! $agency || ! $plan) {
            return;
        }

        if ($agency->stripe_subscription_id) {
            try {
                app(AgencyBillingService::class)->changeSubscriptionPlan($agency, $plan);

                Notification::make()
                    ->title("Piano cambiato a {$plan->name}")
                    ->success()
                    ->send();

                $this->redirect(route('filament.agency.pages.agency-billing'));
            } catch (\Throwable $e) {
                Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
            }

            return;
        }

        // No active subscription — redirect to billing page to checkout
        $this->redirect(route('filament.agency.pages.agency-billing'));
    }
}
