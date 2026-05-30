<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;

use Filament\Forms;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class ContactsRelationManager extends RelationManager
{
    protected static string $relationship = 'contacts';
    protected static ?string $title = 'Contatti';

    public function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')
                ->label('Nome')
                ->required()
                ->maxLength(255),
            Forms\Components\TextInput::make('email')
                ->label('Email')
                ->email()
                ->required()
                ->maxLength(255),
            Forms\Components\TextInput::make('role')
                ->label('Ruolo')
                ->maxLength(100)
                ->placeholder('Es: CEO, Marketing, Tecnico'),
            Forms\Components\Toggle::make('can_access_tenant')
                ->label('Può accedere agli store')
                ->default(false)
                ->helperText('Struttura pronta — accesso reale configurabile in fase successiva'),
        ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->searchable(),
                Tables\Columns\TextColumn::make('role')
                    ->label('Ruolo')
                    ->placeholder('—'),
                Tables\Columns\IconColumn::make('can_access_tenant')
                    ->label('Accesso store')
                    ->boolean(),
            ])
            ->headerActions([
                \Filament\Actions\CreateAction::make()->label('Aggiungi contatto'),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                ]),
            ])
            ->emptyStateHeading('Nessun contatto')
            ->emptyStateDescription('Aggiungi i referenti di questo cliente.')
            ->emptyStateIcon('heroicon-o-user-plus');
    }
}
