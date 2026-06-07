<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accetta invito — {{ $storeName }}</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Inter', system-ui, sans-serif; }</style>
</head>
<body class="min-h-screen bg-gray-50 flex items-center justify-center p-4">

<div class="w-full max-w-md">
    <div class="text-center mb-8">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-4">
            @include('partials.logomark', ['variant' => 'dark'])
        </a>
        <h1 class="text-2xl font-bold text-[#343a4D]">Accedi al tuo store</h1>
        <p class="text-gray-500 mt-1 text-sm">
            Sei stato invitato a gestire <span class="font-semibold text-[#343a4D]">{{ $storeName }}</span>.
            Scegli una password per attivare il tuo accesso.
        </p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">

        @if($errors->any())
            <div class="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
                <ul class="list-disc list-inside space-y-1">
                    @foreach($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form method="POST" action="{{ route('client-invite.accept', ['token' => $token]) }}" class="space-y-5">
            @csrf

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="text"
                    value="{{ $contact->email }}"
                    disabled
                    class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-gray-500 text-sm cursor-not-allowed">
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                    Password <span class="text-red-500">*</span>
                </label>
                <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    minlength="8"
                    autocomplete="new-password"
                    class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:border-[#ff5758] focus:ring-2 focus:ring-[#ff5758]/20 text-sm outline-none transition @error('password') border-red-400 @enderror"
                    placeholder="Almeno 8 caratteri">
            </div>

            <div>
                <label for="password_confirmation" class="block text-sm font-medium text-gray-700 mb-1">
                    Conferma password <span class="text-red-500">*</span>
                </label>
                <input
                    id="password_confirmation"
                    name="password_confirmation"
                    type="password"
                    required
                    autocomplete="new-password"
                    class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:border-[#ff5758] focus:ring-2 focus:ring-[#ff5758]/20 text-sm outline-none transition"
                    placeholder="Ripeti la password">
            </div>

            <button type="submit"
                class="w-full py-3 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-xl text-sm transition-colors mt-2">
                Attiva accesso
            </button>
        </form>
    </div>

    <p class="text-center text-xs text-gray-400 mt-6">
        Questo link scade automaticamente dopo 72 ore.
        Se non ti aspettavi questo invito, ignora questa pagina.
    </p>
</div>

</body>
</html>
