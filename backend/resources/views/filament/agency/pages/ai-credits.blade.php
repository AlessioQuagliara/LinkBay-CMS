<x-filament-panels::page>
    <x-filament::section>
        <div class="flex items-center gap-4">
            <x-heroicon-o-sparkles class="w-10 h-10 text-amber-500"/>
            <div>
                <p class="text-sm text-gray-500">Saldo crediti AI</p>
                <p class="text-4xl font-bold">{{ number_format($this->balance()) }}</p>
            </div>
        </div>
    </x-filament::section>

    <x-filament::section heading="Acquista crediti" class="mt-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            @foreach($this->packages() as $package)
                <div class="border rounded-xl p-5 text-center hover:shadow-md transition">
                    <p class="font-bold text-lg">{{ $package->name }}</p>
                    <p class="text-3xl font-black text-amber-500 my-2">{{ number_format($package->credits) }}</p>
                    <p class="text-xs text-gray-500">crediti</p>
                    <p class="text-xl font-bold mt-3">{{ $package->priceFormatted() }}</p>
                    @php $url = $this->checkoutUrl($package->id); @endphp
                    @if($url)
                        <a href="{{ $url }}" class="block mt-4">
                            <x-filament::button class="w-full">Acquista</x-filament::button>
                        </a>
                    @else
                        <p class="text-xs text-red-500 mt-2">Stripe non configurato</p>
                    @endif
                </div>
            @endforeach
        </div>
    </x-filament::section>

    <x-filament::section heading="Storico (ultimi 20)" class="mt-6">
        <table class="w-full text-sm">
            <thead>
                <tr class="text-left border-b">
                    <th class="pb-2">Data</th>
                    <th class="pb-2">Tipo</th>
                    <th class="pb-2">Descrizione</th>
                    <th class="pb-2 text-right">Crediti</th>
                    <th class="pb-2 text-right">Saldo dopo</th>
                </tr>
            </thead>
            <tbody>
                @foreach($this->ledger() as $entry)
                <tr class="border-b last:border-0">
                    <td class="py-2">{{ $entry->created_at->format('d/m/Y H:i') }}</td>
                    <td class="py-2">
                        <span class="px-2 py-0.5 rounded text-xs font-medium
                            {{ $entry->type === 'purchase' ? 'bg-green-100 text-green-700' :
                               ($entry->type === 'bonus' ? 'bg-blue-100 text-blue-700' :
                               ($entry->type === 'refund' ? 'bg-yellow-100 text-yellow-700' :
                               'bg-red-100 text-red-700')) }}">
                            {{ ucfirst($entry->type) }}
                        </span>
                    </td>
                    <td class="py-2">{{ $entry->description }}</td>
                    <td class="py-2 text-right font-mono {{ $entry->amount > 0 ? 'text-green-600' : 'text-red-600' }}">
                        {{ $entry->amount > 0 ? '+' : '' }}{{ number_format($entry->amount) }}
                    </td>
                    <td class="py-2 text-right font-mono">{{ number_format($entry->balance_after) }}</td>
                </tr>
                @endforeach
            </tbody>
        </table>
    </x-filament::section>
</x-filament-panels::page>
