<x-filament-panels::page>
    <x-filament::section heading="Piano attuale">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                <p class="text-xs text-gray-500">Piano</p>
                <p class="text-xl font-bold">{{ $this->planName() }}</p>
            </div>
            <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                <p class="text-xs text-gray-500">Prezzo</p>
                <p class="text-xl font-bold">{{ $this->planPrice() }}</p>
            </div>
            <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                <p class="text-xs text-gray-500">Max Negozi</p>
                <p class="text-xl font-bold">{{ $this->maxStores() }}</p>
            </div>
            <div class="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
                <p class="text-xs text-gray-500">Fee transazione</p>
                <p class="text-xl font-bold">{{ $this->transactionFee() }}</p>
            </div>
        </div>
    </x-filament::section>

    <x-filament::section heading="Feature incluse" class="mt-6">
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
            @foreach($this->features() as $key => $value)
                <div class="flex items-center gap-2">
                    @if(is_bool($value))
                        <x-dynamic-component :component="$value ? 'heroicon-o-check-circle' : 'heroicon-o-x-circle'"
                            class="w-5 h-5 {{ $value ? 'text-green-500' : 'text-red-400' }}" />
                    @else
                        <x-heroicon-o-information-circle class="w-5 h-5 text-blue-500" />
                    @endif
                    <span class="text-sm capitalize">{{ str_replace('_', ' ', $key) }}:
                        @if(!is_bool($value)) <strong>{{ $value ?? 'Illimitato' }}</strong> @endif
                    </span>
                </div>
            @endforeach
        </div>
    </x-filament::section>

    <x-filament::section heading="Cambia piano" class="mt-6">
        <p class="text-sm text-gray-500">Contatta il supporto per cambiare piano o per informazioni sulla fatturazione.</p>
        <a href="mailto:{{ config('mail.from.address') }}">
            <x-filament::button class="mt-3">Contatta supporto</x-filament::button>
        </a>
    </x-filament::section>
</x-filament-panels::page>
