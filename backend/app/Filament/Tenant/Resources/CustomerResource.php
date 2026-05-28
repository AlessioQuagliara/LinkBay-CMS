<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\CustomerResource\Pages;
use App\Models\Tenant\Customer;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Infolists;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class CustomerResource extends Resource
{
    protected static ?string $model = Customer::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-users';
    protected static string|\NITENUM|NULL $NAVIGATIONGROUP = 'Vendite';
    protected static ?string $modelLabel = 'Cliente';
    protected static ?string $pluralModelLabel = 'Clienti';
    protected static ?int $navigationSort = 2;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome')->required(),
            Forms\Components\TextInput::make('email')->label('Email')->email()->required()
                ->unique(Customer::class, 'email', ignoreRecord: true),
            Forms\Components\TextInput::make('phone')->label('Telefono'),

            Forms\Components\Section::make('Indirizzo')
                ->schema([
                    Forms\Components\TextInput::make('address.street')->label('Via / N. civico'),
                    Forms\Components\TextInput::make('address.city')->label('Città'),
                    Forms\Components\TextInput::make('address.zip')->label('CAP'),
                    Forms\Components\TextInput::make('address.province')->label('Provincia')->maxLength(2),
                    Forms\Components\TextInput::make('address.country')->label('Paese')->default('IT'),
                ])->columns(2),

            Forms\Components\Textarea::make('notes')->label('Note interne')->rows(3)->columnSpanFull(),
            Forms\Components\TagsInput::make('tags')->label('Tag'),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->searchable(),
                Tables\Columns\TextColumn::make('phone')
                    ->label('Telefono')
                    ->toggleable(),
                Tables\Columns\TextColumn::make('orders_count')
                    ->label('Ordini')
                    ->counts('orders')
                    ->badge()
                    ->color('info'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Registrato')
                    ->date('d/m/Y')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\Filter::make('search')
                    ->form([
                        Forms\Components\TextInput::make('search')->label('Cerca nome o email'),
                    ])
                    ->query(fn ($query, array $data) =>
                        $query->when($data['search'], fn ($q) => $q
                            ->where('name', 'like', "%{$data['search']}%")
                            ->orWhere('email', 'like', "%{$data['search']}%")
                        )
                    ),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\ViewAction::make(),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function infolist(Schema $schema): Schema
    {
        return $schema->schema([
            Infolists\Components\Section::make('Anagrafica')
                ->schema([
                    Infolists\Components\TextEntry::make('name')->label('Nome'),
                    Infolists\Components\TextEntry::make('email')->label('Email'),
                    Infolists\Components\TextEntry::make('phone')->label('Telefono'),
                    Infolists\Components\TextEntry::make('notes')->label('Note')->columnSpanFull(),
                ])->columns(3),
            Infolists\Components\Section::make('Indirizzo')
                ->schema([
                    Infolists\Components\TextEntry::make('address.street')->label('Via'),
                    Infolists\Components\TextEntry::make('address.city')->label('Città'),
                    Infolists\Components\TextEntry::make('address.zip')->label('CAP'),
                    Infolists\Components\TextEntry::make('address.country')->label('Paese'),
                ])->columns(4),
        ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListCustomers::route('/'),
            'create' => Pages\CreateCustomer::route('/create'),
            'edit' => Pages\EditCustomer::route('/{record}/edit'),
            'view' => Pages\ViewCustomer::route('/{record}'),
        ];
    }
}
