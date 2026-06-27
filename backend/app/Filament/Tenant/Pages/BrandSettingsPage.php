<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\BrandSetting;
use App\Services\Tenant\BrandService;
use Filament\Forms;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Form;
use Filament\Notifications\Notification;
use Filament\Pages\Page;

class BrandSettingsPage extends Page
{
    use InteractsWithForms;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-paint-brush';

    protected static string|\UnitEnum|null $navigationGroup = 'Impostazioni';

    protected static ?string $navigationLabel = 'Brand';

    protected static ?int $navigationSort = 20;

    protected string $view = 'filament.tenant.pages.brand-settings';

    public array $data = [];

    public function mount(): void
    {
        $brand = BrandSetting::current();
        $this->data = $brand->toArray();
        $this->form->fill($this->data);
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Logo & Favicon')
                    ->schema([
                        Forms\Components\FileUpload::make('logo_upload')
                            ->label('Logo')
                            ->image()
                            ->disk('public')
                            ->directory('brand/logo')
                            ->maxSize(2048)
                            ->helperText('PNG o SVG consigliati, max 2 MB'),
                        Forms\Components\FileUpload::make('favicon_upload')
                            ->label('Favicon')
                            ->image()
                            ->disk('public')
                            ->directory('brand/favicon')
                            ->maxSize(512)
                            ->helperText('PNG 32×32 o ICO, max 512 KB'),
                    ])->columns(2),

                Forms\Components\Section::make('Colori')
                    ->schema([
                        Forms\Components\ColorPicker::make('primary_color')
                            ->label('Colore primario')
                            ->default('#000000'),
                        Forms\Components\ColorPicker::make('secondary_color')
                            ->label('Colore secondario'),
                        Forms\Components\ColorPicker::make('accent_color')
                            ->label('Colore accento'),
                    ])->columns(3),

                Forms\Components\Section::make('Tipografia')
                    ->schema([
                        Forms\Components\Select::make('font_heading')
                            ->label('Font titoli')
                            ->searchable()
                            ->options($this->googleFonts()),
                        Forms\Components\Select::make('font_body')
                            ->label('Font corpo')
                            ->searchable()
                            ->options($this->googleFonts()),
                    ])->columns(2),

                Forms\Components\Section::make('Informazioni negozio')
                    ->schema([
                        Forms\Components\TextInput::make('store_name')
                            ->label('Nome negozio')
                            ->required()
                            ->maxLength(255),
                        Forms\Components\Textarea::make('store_description')
                            ->label('Descrizione')
                            ->rows(3),
                        Forms\Components\TextInput::make('contact_email')
                            ->label('Email di contatto')
                            ->email()
                            ->maxLength(255),
                        Forms\Components\TextInput::make('contact_phone')
                            ->label('Telefono di contatto')
                            ->tel()
                            ->maxLength(50),
                    ])->columns(2),

                Forms\Components\Section::make('Social Links')
                    ->schema([
                        Forms\Components\KeyValue::make('social_links')
                            ->label('')
                            ->keyLabel('Piattaforma (es. instagram)')
                            ->valueLabel('URL')
                            ->addActionLabel('Aggiungi social'),
                    ]),

                Forms\Components\Section::make('Tracking')
                    ->schema([
                        Forms\Components\TextInput::make('meta_pixel_id')
                            ->label('Meta Pixel ID')
                            ->placeholder('1234567890'),
                        Forms\Components\TextInput::make('google_analytics_id')
                            ->label('Google Analytics ID')
                            ->placeholder('G-XXXXXXXXXX'),
                        Forms\Components\Toggle::make('cookie_banner_enabled')
                            ->label('Mostra banner cookie')
                            ->default(true),
                    ])->columns(2),

                Forms\Components\Section::make('CSS / JS personalizzato')
                    ->description('Attenzione: il codice viene iniettato direttamente nel frontend.')
                    ->collapsible()
                    ->collapsed()
                    ->schema([
                        Forms\Components\Textarea::make('custom_css')
                            ->label('CSS personalizzato')
                            ->rows(8)
                            ->fontFamily('mono'),
                        Forms\Components\Textarea::make('custom_js')
                            ->label('JS personalizzato')
                            ->rows(8)
                            ->fontFamily('mono'),
                    ]),
            ])
            ->statePath('data');
    }

    public function save(): void
    {
        $data = $this->form->getState();
        $service = app(BrandService::class);

        // Handle file uploads separately
        $logoUpload = $data['logo_upload'] ?? null;
        $faviconUpload = $data['favicon_upload'] ?? null;
        unset($data['logo_upload'], $data['favicon_upload']);

        $service->update(array_filter($data, fn ($v) => $v !== null));

        Notification::make()
            ->title('Brand aggiornato')
            ->success()
            ->send();
    }

    public function previewCss(): void
    {
        $brand = BrandSetting::current();
        $css = app(BrandService::class)->generateCssVariables($brand);

        $this->dispatch('open-css-preview', css: $css);
    }

    private function googleFonts(): array
    {
        return [
            'Inter' => 'Inter',
            'Roboto' => 'Roboto',
            'Open Sans' => 'Open Sans',
            'Lato' => 'Lato',
            'Montserrat' => 'Montserrat',
            'Poppins' => 'Poppins',
            'Raleway' => 'Raleway',
            'Oswald' => 'Oswald',
            'Merriweather' => 'Merriweather',
            'Playfair Display' => 'Playfair Display',
            'Source Sans 3' => 'Source Sans 3',
            'Nunito' => 'Nunito',
            'Ubuntu' => 'Ubuntu',
            'PT Sans' => 'PT Sans',
            'Noto Sans' => 'Noto Sans',
        ];
    }
}
