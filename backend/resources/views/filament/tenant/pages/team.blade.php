<x-filament-panels::page>
    <div class="space-y-6">

        {{-- Invite form --}}
        <x-filament::section>
            <x-slot name="heading">
                <div class="flex items-center gap-2">
                    <x-heroicon-o-paper-airplane class="w-5 h-5 shrink-0 text-primary-500"/>
                    <span>Invita un membro</span>
                </div>
            </x-slot>

            <form wire:submit="inviteUser" class="flex flex-col sm:flex-row gap-4 items-end">
                <div class="flex-1 space-y-1">
                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Email</label>
                    <x-filament::input type="email" wire:model="inviteData.email" placeholder="nome@esempio.com" required />
                    @error('inviteData.email') <p class="text-xs text-red-500">{{ $message }}</p> @enderror
                </div>
                <div class="w-40 space-y-1">
                    <label class="text-sm font-medium text-gray-700 dark:text-gray-200">Ruolo</label>
                    <select wire:model="inviteData.role" class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white">
                        <option value="editor">Editor</option>
                        <option value="viewer">Viewer</option>
                    </select>
                    @error('inviteData.role') <p class="text-xs text-red-500">{{ $message }}</p> @enderror
                </div>
                <x-filament::button type="submit" icon="heroicon-o-paper-airplane">
                    Invia invito
                </x-filament::button>
            </form>
        </x-filament::section>

        {{-- Members table --}}
        <x-filament::section>
            <x-slot name="heading">
                <div class="flex items-center gap-2">
                    <x-heroicon-o-user-group class="w-5 h-5 shrink-0 text-primary-500"/>
                    <span>Membri del team</span>
                </div>
            </x-slot>

            @php $members = $this->getMembers(); @endphp

            @if($members->isEmpty())
                <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                    <x-heroicon-o-users class="mx-auto w-10 h-10 mb-2 text-gray-300 dark:text-gray-600"/>
                    <p>Nessun membro ancora. Invita qualcuno!</p>
                </div>
            @else
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="text-xs text-gray-500 dark:text-gray-400 uppercase border-b border-gray-200 dark:border-gray-700">
                            <tr>
                                <th class="py-2 pr-4">Nome</th>
                                <th class="py-2 pr-4">Email</th>
                                <th class="py-2 pr-4">Ruolo</th>
                                <th class="py-2 pr-4">Aggiunto il</th>
                                <th class="py-2"></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                            @foreach($members as $member)
                                <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                    <td class="py-2 pr-4 font-medium text-gray-900 dark:text-white">{{ $member->name }}</td>
                                    <td class="py-2 pr-4 text-gray-600 dark:text-gray-400">{{ $member->email }}</td>
                                    <td class="py-2 pr-4">
                                        <x-filament::badge :color="$this->roleColorFor($member->role)">
                                            {{ $this->roleLabelFor($member->role) }}
                                        </x-filament::badge>
                                    </td>
                                    <td class="py-2 pr-4 text-gray-500 dark:text-gray-400">
                                        {{ $member->created_at->format('d/m/Y') }}
                                    </td>
                                    <td class="py-2 text-right">
                                        @if($member->role !== 'owner' && $member->id !== auth()->id())
                                            <button wire:click="removeUser({{ $member->id }})"
                                                    wire:confirm="Rimuovere {{ $member->name }} dal team?"
                                                    class="text-xs text-red-500 hover:text-red-700 hover:underline">
                                                Rimuovi
                                            </button>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </x-filament::section>
    </div>
</x-filament-panels::page>
