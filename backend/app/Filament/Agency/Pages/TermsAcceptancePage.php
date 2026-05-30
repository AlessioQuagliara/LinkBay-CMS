<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\TermsAcceptance;
use Filament\Notifications\Notification;
use Filament\Pages\Page;

class TermsAcceptancePage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-document-check';
    protected static ?string $navigationLabel = 'Termini & Condizioni';
    protected static ?string $slug = 'terms-acceptance';
    protected string $view = 'filament.agency.pages.terms-acceptance';

    // Mai in sidebar: è solo un gate, non una destinazione di navigazione
    public static function shouldRegisterNavigation(): bool
    {
        return false;
    }

    public function mount(): void
    {
        $agency = $this->agency();

        // Se i T&C sono già accettati, redirige alla dashboard
        if ($agency && TermsAcceptance::hasAccepted($agency->id)) {
            $this->redirect(route('filament.agency.pages.dashboard'));
        }
    }

    public function accept(): void
    {
        $agency = $this->agency();
        $user   = auth()->user();

        if (!$agency || !$user) {
            Notification::make()->title('Errore: sessione non valida')->danger()->send();
            return;
        }

        try {
            TermsAcceptance::record(
                agency: $agency,
                userId: $user->id,
                ip:     request()->ip() ?? '0.0.0.0',
                ua:     request()->userAgent(),
            );
        } catch (\Illuminate\Database\UniqueConstraintViolationException) {
            // Double-click o doppio submit: i T&C erano già stati accettati, procedi comunque
        }

        // Aggiorna il campo in-memory per far funzionare il fast-path nel middleware
        $agency->update(['terms_accepted_version' => TermsAcceptance::currentVersion()]);

        Notification::make()
            ->title('Termini accettati — benvenuto in LinkBay!')
            ->success()
            ->send();

        $this->redirect(route('filament.agency.pages.dashboard'));
    }

    public function termsVersion(): string
    {
        return TermsAcceptance::currentVersion();
    }

}
