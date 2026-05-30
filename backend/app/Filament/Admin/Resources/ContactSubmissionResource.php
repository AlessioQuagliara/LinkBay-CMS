<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\ContactSubmissionResource\Pages;
use App\Models\Central\ContactSubmission;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Forms;
use Filament\Tables;
use Filament\Tables\Table;

class ContactSubmissionResource extends Resource
{
    protected static ?string $model = ContactSubmission::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-envelope';
    protected static string|\UnitEnum|null $navigationGroup = 'Operations';
    protected static ?string $modelLabel = 'Contact Submission';
    protected static ?string $pluralModelLabel = 'Contact Submissions';
    protected static ?int $navigationSort = 10;

    public static function getNavigationBadge(): ?string
    {
        return (string) static::getModel()::where('status', 'new')->count() ?: null;
    }

    public static function getNavigationBadgeColor(): ?string
    {
        return 'danger';
    }

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Contact details')
                ->schema([
                    Forms\Components\TextInput::make('name')->label('Name')->disabled(),
                    Forms\Components\TextInput::make('company')->label('Company')->disabled(),
                    Forms\Components\TextInput::make('email')->label('Email')->disabled(),
                    Forms\Components\TextInput::make('store_count')->label('Store count')->disabled(),
                    Forms\Components\Select::make('status')
                        ->label('Status')
                        ->options([
                            'new'      => 'New',
                            'read'     => 'Read',
                            'archived' => 'Archived',
                        ])
                        ->required(),
                ])->columns(2),

            Section::make('Message')
                ->schema([
                    Forms\Components\Textarea::make('message')
                        ->label('Message')
                        ->disabled()
                        ->rows(8)
                        ->columnSpanFull(),
                ]),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->defaultSort('created_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Name')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('company')
                    ->label('Company')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->searchable()
                    ->copyable(),
                Tables\Columns\TextColumn::make('store_count')
                    ->label('Stores')
                    ->badge()
                    ->color('gray'),
                Tables\Columns\SelectColumn::make('status')
                    ->label('Status')
                    ->options([
                        'new'      => 'New',
                        'read'     => 'Read',
                        'archived' => 'Archived',
                    ])
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Received')
                    ->dateTime('d M Y, H:i')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'new'      => 'New',
                        'read'     => 'Read',
                        'archived' => 'Archived',
                    ]),
            ])
            ->actions([
                \Filament\Actions\EditAction::make()->label('View'),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListContactSubmissions::route('/'),
            'edit'  => Pages\ViewContactSubmission::route('/{record}/edit'),
        ];
    }
}
