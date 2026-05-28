<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registra la tua Agency — LinkBay CMS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-violet-50 to-slate-100 flex items-center justify-center p-4">

<div class="w-full max-w-md">
    <div class="text-center mb-8">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-block mb-4">
            <span class="text-2xl font-bold text-violet-600">LinkBay CMS</span>
        </a>
        <h1 class="text-2xl font-bold text-slate-800">Crea il tuo spazio Agency</h1>
        <p class="text-slate-500 mt-1 text-sm">Gestisci i tuoi clienti e i loro negozi da un'unica dashboard.</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">

        @if(session('success'))
            <div class="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-800 text-sm">
                {{ session('success') }}
            </div>
        @endif

        @if($errors->any())
            <div class="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
                <ul class="list-disc list-inside space-y-1">
                    @foreach($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form method="POST" action="{{ route('agency.register.store') }}" class="space-y-5">
            @csrf

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Nome Agenzia</label>
                <input type="text" name="agency_name" value="{{ old('agency_name') }}" required
                    placeholder="Studio Rossi Marketing"
                    class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent @error('agency_name') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Sottodominio</label>
                <div class="flex rounded-lg border border-slate-300 overflow-hidden focus-within:ring-2 focus-within:ring-violet-500 @error('slug') border-red-400 @enderror">
                    <input type="text" id="slug" name="slug" value="{{ old('slug') }}" required
                        placeholder="mia-agenzia"
                        class="flex-1 px-3 py-2 text-sm focus:outline-none">
                    <span class="px-3 py-2 bg-slate-50 text-slate-500 text-sm border-l border-slate-300 whitespace-nowrap">
                        .{{ config('app.central_domain', 'linkbay-cms.com') }}
                    </span>
                </div>
                <p class="text-xs text-slate-400 mt-1">
                    Anteprima: <strong id="slug-preview" class="text-violet-600">{{ old('slug', 'mia-agenzia') }}</strong>.{{ config('app.central_domain', 'linkbay-cms.com') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input type="email" name="email" value="{{ old('email') }}" required
                    class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 @error('email') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Password</label>
                <input type="password" name="password" required minlength="8"
                    class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 @error('password') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Conferma Password</label>
                <input type="password" name="password_confirmation" required minlength="8"
                    class="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500">
            </div>

            <button type="submit"
                class="w-full py-2.5 px-4 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-lg text-sm transition-colors">
                Crea account Agency
            </button>
        </form>

        <p class="text-center text-sm text-slate-500 mt-6">
            Hai già un account?
            <a href="#" class="text-violet-600 hover:underline font-medium">Accedi alla tua dashboard</a>
        </p>

    </div>

    <p class="text-center text-xs text-slate-400 mt-6">
        Creando un account accetti i <a href="#" class="underline">Termini di Servizio</a>
        e la <a href="#" class="underline">Privacy Policy</a>.
    </p>
</div>

<script>
    const slugInput = document.getElementById('slug');
    const preview = document.getElementById('slug-preview');

    slugInput?.addEventListener('input', function () {
        const val = this.value.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/^-+|-+$/g, '');
        this.value = val;
        preview.textContent = val || 'mia-agenzia';
    });

    // Auto-genera slug dal nome agenzia
    document.querySelector('[name="agency_name"]')?.addEventListener('blur', function () {
        if (!slugInput.value) {
            const slug = this.value.toLowerCase()
                .normalize('NFD').replace(/[̀-ͯ]/g, '')
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-+|-+$/g, '')
                .substring(0, 63);
            slugInput.value = slug;
            preview.textContent = slug || 'mia-agenzia';
        }
    });
</script>
</body>
</html>
