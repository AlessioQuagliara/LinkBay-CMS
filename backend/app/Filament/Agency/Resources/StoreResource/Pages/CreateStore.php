<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\StoreResource\Pages;

use App\Filament\Agency\Resources\StoreResource;
use App\Jobs\ProvisionTenantDatabaseJob;
use App\Models\Central\AgencyClient;
use App\Models\Central\AuditEvent;
use App\Models\Central\Tenant;
use App\Services\AuditEventService;
use App\Services\TenantProvisioningService;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\CreateRecord;
use Filament\Resources\Pages\CreateRecord\Concerns\HasWizard;
use Filament\Schemas\Components\Wizard\Step;
use Illuminate\Support\Facades\Log;

class CreateStore extends CreateRecord
{
    use HasWizard;

    protected static string $resource = StoreResource::class;

    public function getSteps(): array
    {
        $agency = app()->bound('current_agency') ? app('current_agency') : null;
        $storeDomain = config('app.store_domain', 'linkbay-cms.com');

        return [

            // ── Step 1: Cliente ───────────────────────────────────────────────
            Step::make('Cliente')
                ->description('Associa questo store a un cliente della tua agency.')
                ->icon('heroicon-o-users')
                ->schema([
                    Forms\Components\Select::make('agency_client_id')
                        ->label('Cliente')
                        ->options(
                            $agency
                                ? AgencyClient::where('agency_id', $agency->id)
                                    ->where('status', 'active')
                                    ->orderBy('name')
                                    ->pluck('name', 'id')
                                : []
                        )
                        ->searchable()
                        ->nullable()
                        ->placeholder('Nessun cliente — potrai associarlo dopo')
                        ->createOptionForm([
                            Forms\Components\TextInput::make('name')
                                ->label('Nome cliente / azienda')
                                ->required()
                                ->maxLength(255),
                            Forms\Components\TextInput::make('billing_email')
                                ->label('Email fatturazione')
                                ->email()
                                ->required()
                                ->maxLength(255),
                        ])
                        ->createOptionUsing(function (array $data) use ($agency): int|string {
                            if (! $agency) {
                                return 0;
                            }

                            $client = AgencyClient::create([
                                'agency_id' => $agency->id,
                                'name' => $data['name'],
                                'billing_email' => $data['billing_email'],
                                'status' => 'active',
                            ]);

                            return $client->id;
                        })
                        ->columnSpanFull(),
                ]),

            // ── Step 2: Negozio ───────────────────────────────────────────────
            Step::make('Negozio')
                ->description('Nome, subdomain e contatto admin del negozio.')
                ->icon('heroicon-o-shopping-bag')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome negozio')
                        ->required()
                        ->maxLength(255),

                    Forms\Components\TextInput::make('id')
                        ->label('Subdomain')
                        ->required()
                        ->unique(Tenant::class, 'id', ignoreRecord: true)
                        ->regex('/^[a-z0-9][a-z0-9-]*$/')
                        ->maxLength(63)
                        ->suffix('.'.$storeDomain)
                        ->helperText('Solo lettere minuscole, numeri e trattini.')
                        ->live(onBlur: true),

                    Forms\Components\TextInput::make('admin_email')
                        ->label('Email admin store')
                        ->email()
                        ->required()
                        ->maxLength(255)
                        ->helperText('Usata per impostare l\'utente admin iniziale del pannello negozio.')
                        ->columnSpanFull(),
                ])->columns(2),

            // ── Step 3: Riepilogo ─────────────────────────────────────────────
            Step::make('Riepilogo')
                ->description('Verifica i dati prima di creare il negozio.')
                ->icon('heroicon-o-check-circle')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome negozio')
                        ->readOnly(),

                    Forms\Components\TextInput::make('id')
                        ->label('Dominio completo')
                        ->readOnly()
                        ->suffix('.'.$storeDomain),

                    Forms\Components\TextInput::make('admin_email')
                        ->label('Email admin store')
                        ->readOnly(),

                    Forms\Components\Select::make('agency_client_id')
                        ->label('Cliente')
                        ->options(
                            $agency
                                ? AgencyClient::where('agency_id', $agency->id)
                                    ->pluck('name', 'id')
                                : []
                        )
                        ->disabled()
                        ->placeholder('Nessuno'),
                ])->columns(2),
        ];
    }

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $agency = app()->bound('current_agency') ? app('current_agency') : null;

        if (! $agency) {
            Notification::make()
                ->title('Errore contesto agenzia')
                ->body('Impossibile identificare l\'agenzia corrente. Ricarica la pagina e riprova.')
                ->danger()
                ->send();

            $this->halt();
        }

        $data['agency_id'] = $agency->id;
        $data['status'] = 'active';

        return $data;
    }

    protected function afterCreate(): void
    {
        $tenant = $this->record;
        $adminEmail = $tenant->admin_email;

        // Domain registration: fast DB insert, safe from Livewire context.
        try {
            app(TenantProvisioningService::class)->registerDomain($tenant);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Avviso: registrazione dominio')
                ->body($e->getMessage())
                ->warning()
                ->send();

            Log::warning('StoreWizard: domain registration failed', [
                'tenant_id' => $tenant->id,
                'error' => $e->getMessage(),
            ]);
        }

        // DB initialization must run outside Livewire — dispatched to the queue.
        ProvisionTenantDatabaseJob::dispatch($tenant->id, $adminEmail);

        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_STORE_CREATED,
            subjectType: 'store',
            subjectId: $tenant->id,
            newValues: [
                'name' => $tenant->name,
                'id' => $tenant->id,
                'status' => $tenant->status,
            ],
            metadata: [
                'admin_email' => $adminEmail,
                'agency_client_id' => $tenant->agency_client_id,
                'provisioning_queued' => true,
            ],
        );
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('edit', ['record' => $this->getRecord()]);
    }

    protected function getCreatedNotification(): ?Notification
    {
        $record = $this->getRecord();
        $storeDomain = config('app.store_domain', 'linkbay-cms.com');

        return Notification::make()
            ->title('Negozio "'.$record->name.'" creato!')
            ->body('Database in inizializzazione. Usa il pulsante "Login" per accedere al pannello store.')
            ->success()
            ->persistent();
    }
}
