<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register your Agency — LinkBay-CMS</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; }
    </style>
</head>
<body class="min-h-screen bg-gray-50 flex items-center justify-center p-4">

<div class="w-full max-w-md">
    <div class="text-center mb-8">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-4">
            @include('partials.logomark', ['variant' => 'dark'])
        </a>
        <h1 class="text-2xl font-bold text-[#343a4D]">Create your Agency account</h1>
        <p class="text-gray-500 mt-1 text-sm">Manage your clients and their stores from one central dashboard.</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">

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
                <label class="block text-sm font-medium text-gray-700 mb-1">Agency Name</label>
                <input type="text" name="agency_name" value="{{ old('agency_name') }}" required
                    placeholder="Rossi Marketing Studio"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent @error('agency_name') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Subdomain</label>
                <div class="flex rounded-lg border border-gray-300 overflow-hidden focus-within:ring-2 focus-within:ring-violet-500 @error('slug') border-red-400 @enderror">
                    <input type="text" id="slug" name="slug" value="{{ old('slug') }}" required
                        placeholder="my-agency"
                        class="flex-1 px-3 py-2 text-sm focus:outline-none">
                    <span class="px-3 py-2 bg-slate-50 text-gray-500 text-sm border-l border-gray-300 whitespace-nowrap">
                        .{{ config('app.central_domain', 'linkbay-cms.com') }}
                    </span>
                </div>
                <p class="text-xs text-gray-400 mt-1">
                    Preview: <strong id="slug-preview" class="text-[#ff5758]">{{ old('slug', 'my-agency') }}</strong>.{{ config('app.central_domain', 'linkbay-cms.com') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" name="email" value="{{ old('email') }}" required
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('email') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input type="password" name="password" required minlength="8"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('password') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                <input type="password" name="password_confirmation" required minlength="8"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758]">
            </div>

            <button type="submit"
                class="w-full py-2.5 px-4 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
                Create Agency account
            </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-6">
            Already have an account?
            <a href="{{ route('agency.find') }}" class="text-[#ff5758] hover:underline font-medium">Log in to your dashboard →</a>
        </p>

    </div>

    <p class="text-center text-xs text-gray-400 mt-6">
        By creating an account you agree to our <a href="#" class="underline">Terms of Service</a>
        and <a href="#" class="underline">Privacy Policy</a>.
    </p>
</div>

<script>
    const slugInput = document.getElementById('slug');
    const preview = document.getElementById('slug-preview');

    slugInput?.addEventListener('input', function () {
        const val = this.value.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/^-+|-+$/g, '');
        this.value = val;
        preview.textContent = val || 'my-agency';
    });

    // Auto-generate slug from agency name on blur
    document.querySelector('[name="agency_name"]')?.addEventListener('blur', function () {
        if (!slugInput.value) {
            const slug = this.value.toLowerCase()
                .normalize('NFD').replace(/[̀-ͯ]/g, '')
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-+|-+$/g, '')
                .substring(0, 63);
            slugInput.value = slug;
            preview.textContent = slug || 'my-agency';
        }
    });
</script>
</body>
</html>
