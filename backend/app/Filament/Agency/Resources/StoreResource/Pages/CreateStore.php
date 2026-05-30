<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\StoreResource\Pages;

use App\Filament\Agency\Resources\StoreResource;
use App\Models\Central\Agency;
use App\Services\TenantProvisioningService;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\CreateRecord;
use Illuminate\Support\Facades\Log;

class CreateStore extends CreateRecord
{
    protected static string $resource = StoreResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        // Try lazy singleton first, then direct query as fallback.
        // The singleton might be null if AgencyPanelProvider failed to resolve it
        // (e.g. on Livewire XHR requests where DB resolver isn't ready during register()).
        $agency = app('current_agency')
            ?? Agency::fromDomain(request()->getHost());

        if (! $agency) {
            Notification::make()
                ->title('Errore contesto agenzia')
                ->body('Impossibile identificare l\'agenzia corrente. Ricarica la pagina e riprova.')
                ->danger()
                ->send();
            $this->halt();
        }

        $data['agency_id'] = $agency->id;

        return $data;
    }

    protected function afterCreate(): void
    {
        // Only register the domain (fast INSERT, no tenancy context switch).
        // DB initialization is done via the "Provisioning" button in the table to avoid
        // tenancy()->initialize() corrupting the DB connection mid-Livewire-request.
        try {
            app(TenantProvisioningService::class)->registerDomain($this->record);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Registrazione dominio fallita')
                ->body('Store creato. Errore registrazione dominio: ' . $e->getMessage())
                ->warning()
                ->send();

            Log::warning('Store domain registration failed after create', [
                'tenant_id' => $this->record->id,
                'error'     => $e->getMessage(),
            ]);
        }
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index');
    }
}
