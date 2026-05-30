<x-filament-panels::page>
    <div class="max-w-2xl mx-auto">
        <x-filament::section>
            <div class="text-center mb-6">
                <x-heroicon-o-document-check class="w-8 h-8 text-primary-500 mx-auto mb-3" />
                <h2 class="text-2xl font-bold">Termini e Condizioni d'uso</h2>
                <p class="text-sm text-gray-500 mt-1">Versione {{ $this->termsVersion() }}</p>
            </div>

            <div class="prose dark:prose-invert prose-sm max-w-none text-gray-700 dark:text-gray-300 space-y-4 max-h-96 overflow-y-auto border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                <h3>1. Utilizzo della piattaforma</h3>
                <p>Utilizzando LinkBay-CMS accetti le presenti condizioni d'uso. La piattaforma è destinata ad agenzie digitali, software house e operatori white-label.</p>

                <h3>2. Platform Share</h3>
                <p>LinkBayCMS trattiene una percentuale (Platform Share) su ogni pagamento processato dai tuoi clienti finali tramite il tuo account Stripe Connect. La percentuale dipende dal piano attivo al momento della transazione:</p>
                <ul>
                    <li>Piano Starter: 30%</li>
                    <li>Piano Pro: 20%</li>
                    <li>Piano Business: 10%</li>
                    <li>Piano AppSumo LTD: 38% fisso a vita</li>
                </ul>
                <p><strong>La Platform Share si applica alle transazioni future. Modifiche al piano alterano la fee solo sulle transazioni successive al cambio piano.</strong></p>

                <h3>3. Crediti AI</h3>
                <p>I crediti AI sono consumabili separati dal piano. Non sono rimborsabili. Il saldo mostrato in dashboard è autoritativo. I crediti AI non sono inclusi nel piano LTD AppSumo.</p>

                <h3>4. Responsabilità contenuti</h3>
                <p>L'agenzia è responsabile in solido dei contenuti pubblicati dai propri store sulla piattaforma. LinkBayCMS si riserva il diritto di sospendere store o agenzie in violazione dei presenti termini.</p>

                <h3>5. Sospensione per morosità</h3>
                <p>In caso di mancato pagamento del piano ricorrente, l'agenzia riceve un periodo di grazia di 7 giorni. Trascorso tale periodo senza regolarizzazione, l'account viene sospeso. I dati vengono conservati per 30 giorni prima dell'eliminazione definitiva.</p>

                <h3>6. Export dati e offboarding</h3>
                <p>I dati dei negozi (ordini, prodotti, clienti) sono di proprietà dell'agenzia/cliente. LinkBayCMS fornisce export su richiesta entro 30 giorni dalla cancellazione dell'account.</p>

                <h3>7. Divieto di rivendita</h3>
                <p>L'agenzia non può rivendere l'accesso alla piattaforma come proprio prodotto senza accordo white-label esplicito firmato con LinkBay.</p>

                <h3>8. Risoluzione dispute</h3>
                <p>In caso di discrepanza nei calcoli delle commissioni, fa fede il report Stripe riconciliato con i CommissionRecord di LinkBay. L'agenzia può richiedere verifica entro 30 giorni dalla data della transazione.</p>

                <h3>9. Modifiche ai termini</h3>
                <p>LinkBayCMS può modificare i presenti termini con 30 giorni di preavviso per i piani ricorrenti. Il piano LTD AppSumo mantiene le condizioni economiche (Platform Share 38%) per tutta la vita del piano.</p>
            </div>

            <div class="mt-6 p-4 border border-amber-300 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                <p class="text-sm font-medium text-amber-800 dark:text-amber-300">
                    Prima di accedere alla piattaforma devi leggere e accettare i Termini e Condizioni d'uso (versione {{ $this->termsVersion() }}).
                </p>
                <p class="text-xs text-amber-700 dark:text-amber-400 mt-1">
                    Cliccando su "Accetto i Termini" dichiari di aver letto, compreso e accettato le condizioni sopra riportate, incluse le percentuali di Platform Share applicabili al tuo piano.
                </p>
            </div>

            <div class="mt-4 flex flex-col sm:flex-row gap-3 justify-end">
                <a href="{{ route('filament.agency.auth.logout') }}"
                   onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                    <x-filament::button color="gray">Non accetto — Esci</x-filament::button>
                </a>
                <form id="logout-form" action="{{ route('filament.agency.auth.logout') }}" method="POST" class="hidden">
                    @csrf
                </form>

                <x-filament::button wire:click="accept" color="primary">
                    Accetto i Termini
                </x-filament::button>
            </div>
        </x-filament::section>
    </div>
</x-filament-panels::page>
