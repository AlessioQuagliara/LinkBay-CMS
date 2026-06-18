<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\LayoutTemplateResource\RelationManagers;

use App\Models\Central\LayoutAssignment;
use App\Models\Central\Tenant;
use Filament\Forms;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class AssignmentsRelationManager extends RelationManager
{
    protected static string $relationship = 'assignments';

    protected static ?string $title = 'Store assegnati';

    protected static ?string $recordTitleAttribute = 'tenant_id';

    public function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\Select::make('tenant_id')
                ->label('Store')
                ->options(function () {
                    $agencyId = $this->ownerRecord->agency_id;

                    return Tenant::where('agency_id', $agencyId)
                        ->where('status', 'active')
                        ->orderBy('name')
                        ->pluck('name', 'id');
                })
                ->searchable()
                ->required()
                ->helperText('Solo store attivi della tua agency.'),

            Forms\Components\Select::make('page_key')
                ->label('Pagina')
                ->options(array_combine(LayoutAssignment::PAGE_KEYS, array_map('ucfirst', LayoutAssignment::PAGE_KEYS)))
                ->default('home')
                ->required()
                ->helperText('Ogni store può avere un solo template per slot pagina.'),
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
                Tables\Columns\BadgeColumn::make('page_key')
                    ->label('Pagina')
                    ->formatStateUsing(fn (string $state) => ucfirst($state))
                    ->color('primary'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Assegnato il')
                    ->date('d/m/Y'),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make()
                    ->label('Assegna a store')
                    ->mutateFormDataUsing(function (array $data): array {
                        $data['agency_id'] = $this->ownerRecord->agency_id;

                        return $data;
                    })
                    ->before(function (array $data): void {
                        // Enforce cross-agency security: the selected tenant must belong
                        // to the same agency as this template.
                        $tenant = Tenant::find($data['tenant_id']);

                        if (! $tenant || (int) $tenant->agency_id !== (int) $this->ownerRecord->agency_id) {
                            $this->halt();
                        }
                    }),
            ])
            ->actions([
                Tables\Actions\DeleteAction::make()->label('Rimuovi'),
            ])
            ->emptyStateHeading('Nessuno store assegnato')
            ->emptyStateDescription('Assegna questo template a uno store per attivarlo.')
            ->emptyStateIcon('heroicon-o-shopping-bag');
    }
}
