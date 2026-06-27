<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\StorePaymentSettings;
use Filament\Actions\Action;
use Filament\Forms\Components\CheckboxList;
use Filament\Forms\Components\Section;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Form;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Support\Facades\Log;
use Stripe\Balance;
use Stripe\Stripe;

class PaymentSettingsPage extends Page
{
    use InteractsWithForms;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-credit-card';

    protected static string|\UnitEnum|null $navigationGroup = 'Impostazioni';

    protected static ?string $navigationLabel = 'Pagamenti';

    protected static ?string $slug = 'settings/payments';

    protected string $view = 'filament.tenant.pages.payment-settings';

    public array $data = [];

    public function mount(): void
    {
        $settings = StorePaymentSettings::current();

        $this->data = [
            'stripe_publishable_key' => $settings?->stripe_publishable_key ?? '',
            'stripe_secret_key' => '',
            // Never pre-fill the secret key for security; always require re-entry
            'payment_methods_enabled' => $settings?->payment_methods_enabled ?? ['card'],
            'currency' => $settings?->currency ?? 'eur',
            'capture_method' => $settings?->capture_method ?? 'automatic',
            'statement_descriptor' => $settings?->statement_descriptor ?? '',
            'stripe_account_id' => $settings?->stripe_account_id ?? '',
        ];

        $this->form->fill($this->data);
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Section::make('Stripe')
                    ->description('Configura le chiavi API Stripe per il tuo negozio.')
                    ->schema([
                        TextInput::make('stripe_publishable_key')
                            ->label('Chiave pubblica (pk_)')
                            ->placeholder('pk_live_...')
                            ->maxLength(255),
                        TextInput::make('stripe_secret_key')
                            ->label('Chiave segreta (sk_)')
                            ->placeholder('Lascia vuoto per non modificare')
                            ->password()
                            ->revealable()
                            ->maxLength(255),
                    ])->columns(2),

                Section::make('Metodi di pagamento abilitati')
                    ->schema([
                        CheckboxList::make('payment_methods_enabled')
                            ->label('')
                            ->options([
                                'card' => 'Carta di credito/debito',
                                'sepa_debit' => 'SEPA Direct Debit',
                                'paypal' => 'PayPal',
                                'klarna' => 'Klarna',
                            ])
                            ->columns(2),
                    ]),

                Section::make('Valuta e opzioni')
                    ->schema([
                        Select::make('currency')
                            ->label('Valuta')
                            ->options([
                                'eur' => 'EUR — Euro',
                                'usd' => 'USD — Dollaro',
                                'gbp' => 'GBP — Sterlina',
                            ])
                            ->required(),
                        Select::make('capture_method')
                            ->label('Metodo di cattura')
                            ->options([
                                'automatic' => 'Automatico (addebito immediato)',
                                'manual' => 'Manuale (autorizza e cattura separatamente)',
                            ])
                            ->required(),
                        TextInput::make('statement_descriptor')
                            ->label('Descrizione estratto conto')
                            ->maxLength(22)
                            ->helperText('Massimo 22 caratteri — appare sulla carta del cliente'),
                    ])->columns(3),

                Section::make('Stripe Connect')
                    ->description('Collega il tuo account Stripe per ricevere pagamenti direttamente.')
                    ->schema([
                        TextInput::make('stripe_account_id')
                            ->label('Account ID Stripe Connect')
                            ->placeholder('acct_...')
                            ->maxLength(255),
                    ]),
            ])
            ->statePath('data');
    }

    public function save(): void
    {
        $data = $this->form->getState();

        $updates = [
            'stripe_publishable_key' => $data['stripe_publishable_key'] ?? null,
            'payment_methods_enabled' => $data['payment_methods_enabled'] ?? ['card'],
            'currency' => $data['currency'] ?? 'eur',
            'capture_method' => $data['capture_method'] ?? 'automatic',
            'statement_descriptor' => $data['statement_descriptor'] ?? null,
            'stripe_account_id' => $data['stripe_account_id'] ?? null,
        ];

        // Only update secret key if provided
        if (! empty($data['stripe_secret_key'])) {
            $updates['stripe_secret_key'] = $data['stripe_secret_key'];
        }

        StorePaymentSettings::updateOrCreate([], $updates);

        Notification::make()->title('Impostazioni salvate')->success()->send();
    }

    protected function getHeaderActions(): array
    {
        return [
            Action::make('test_connection')
                ->label('Testa connessione Stripe')
                ->icon('heroicon-o-signal')
                ->color('info')
                ->action(function (): void {
                    $settings = StorePaymentSettings::current();

                    if (! $settings?->isStripeConfigured()) {
                        Notification::make()
                            ->title('Chiave segreta non configurata')
                            ->warning()
                            ->send();

                        return;
                    }

                    try {
                        Stripe::setApiKey($settings->stripe_secret_key);
                        Balance::retrieve();

                        Notification::make()
                            ->title('Connessione Stripe OK')
                            ->body('Le chiavi API sono valide.')
                            ->success()
                            ->send();
                    } catch (\Throwable $e) {
                        Log::error('PaymentSettingsPage: Stripe connection test failed', [
                            'error' => $e->getMessage(),
                        ]);

                        Notification::make()
                            ->title('Connessione fallita')
                            ->body($e->getMessage())
                            ->danger()
                            ->send();
                    }
                }),
        ];
    }
}
