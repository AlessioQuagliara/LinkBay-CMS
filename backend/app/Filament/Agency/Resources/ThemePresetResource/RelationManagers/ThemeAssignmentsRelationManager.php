<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\ThemePresetResource\RelationManagers;

use App\Models\Central\Tenant;
use App\Models\Central\ThemeAssignment;
use App\Models\Central\UsageEvent;
use App\Services\UsageEventService;
use Filament\Forms;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class ThemeAssignmentsRelationManager extends RelationManager
{
    protected static string $relationship = 'assignments';

    protected static ?string $title = 'Store con questo tema';

    protected static ?string $recordTitleAttribute = 'tenant_id';

    public function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\Select::make('tenant_id')
                ->label('Store')
                ->options(function () {
                    $agency = app()->has('current_agency') ? app('current_agency') : null;
                    if (! $agency) {
                        return [];
                    }

                    return Tenant::where('agency_id', $agency->id)
                        ->where('status', 'active')
                        ->orderBy('name')
                        ->pluck('name', 'id');
                })
                ->searchable()
                ->required()
                ->helperText('Solo store attivi della tua agency. Se lo store ha già un tema, verrà sostituito.'),
        ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('tenant.name')
                    ->label('Store')
                    ->searchable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('tenant_id')
                    ->label('Subdomain')
                    ->fontFamily('mono')
                    ->color('gray')
                    ->formatStateUsing(fn (string $state) => $state.'.'.config('app.store_domain', '...')),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Assegnato il')
                    ->date('d/m/Y'),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make()
                    ->label('Assegna a store')
                    ->using(function (array $data): ThemeAssignment {
                        $agency = app()->has('current_agency') ? app('current_agency') : null;

                        // Upsert: replace any existing theme assignment for this tenant.
                        $assignment = ThemeAssignment::updateOrCreate(
                            ['tenant_id' => $data['tenant_id']],
                            [
                                'agency_id' => $agency?->id,
                                'theme_preset_id' => $this->ownerRecord->id,
                            ],
                        );

                        app(UsageEventService::class)->track(
                            eventType: UsageEvent::EVENT_THEME_ASSIGNED,
                            agencyId: $agency?->id,
                            tenantId: $data['tenant_id'],
                            subjectType: 'theme_preset',
                            subjectId: $this->ownerRecord->id,
                            meta: ['theme_slug' => $this->ownerRecord->slug],
                        );

                        return $assignment;
                    })
                    ->before(function (array $data): void {
                        // Cross-agency security: tenant must belong to the current agency.
                        $agency = app()->has('current_agency') ? app('current_agency') : null;
                        $tenant = Tenant::find($data['tenant_id']);

                        if (! $agency || ! $tenant || (int) $tenant->agency_id !== (int) $agency->id) {
                            $this->halt();
                        }
                    }),
            ])
            ->actions([
                Tables\Actions\DeleteAction::make()->label('Rimuovi'),
            ])
            ->emptyStateHeading('Nessuno store assegnato')
            ->emptyStateDescription('Assegna questo tema a uno store per applicarlo.')
            ->emptyStateIcon('heroicon-o-shopping-bag');
    }
}
