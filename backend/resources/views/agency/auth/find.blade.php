<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to your dashboard — LinkBay-CMS</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; }
        @keyframes pulse-soft { 0%, 100% { opacity: 1; } 50% { opacity: .7; } }
    </style>
</head>
<body class="min-h-screen bg-gray-50 flex items-center justify-center p-4">

<div class="w-full max-w-md">

    {{-- Logo / Brand --}}
    <div class="text-center mb-8">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-4">
            @include('partials.logomark', ['variant' => 'dark'])
        </a>
        <h1 class="text-2xl font-bold text-[#343a4D]">Find your dashboard</h1>
        <p class="text-gray-500 mt-1 text-sm">Enter your agency subdomain to access your control panel.</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">

        <div id="error-msg" class="hidden mb-5 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm"></div>

        <form id="finder-form" class="space-y-5" onsubmit="handleFind(event)">

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Agency Subdomain</label>
                <div class="flex rounded-lg border border-gray-300 overflow-hidden focus-within:ring-2 focus-within:ring-[#ff5758] focus-within:border-transparent">
                    <input
                        type="text"
                        id="subdomain"
                        name="subdomain"
                        required
                        placeholder="my-agency"
                        autocomplete="off"
                        class="flex-1 px-3 py-2.5 text-sm focus:outline-none"
                    >
                    <span class="px-3 py-2.5 bg-gray-50 text-gray-500 text-sm border-l border-gray-300 whitespace-nowrap">
                        .{{ config('app.central_domain', 'linkbay-cms.com') }}
                    </span>
                </div>
                <p class="text-xs text-gray-400 mt-1">
                    You will be redirected to: <span id="preview-url" class="text-[#ff5758] font-medium">my-agency.{{ config('app.central_domain', 'linkbay-cms.com') }}/dashboard</span>
                </p>
            </div>

            <button type="submit"
                class="w-full py-2.5 px-4 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
                Go to dashboard →
            </button>
        </form>

        <div class="relative my-6">
            <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-200"></div></div>
            <div class="relative flex justify-center text-xs text-gray-400 uppercase"><span class="bg-white px-3">Or</span></div>
        </div>

        <p class="text-center text-sm text-gray-500">
            Don&apos;t have an account yet?
            <a href="{{ route('agency.register') }}" class="text-[#ff5758] hover:underline font-medium">Create your agency →</a>
        </p>

    </div>

    <p class="text-center text-xs text-gray-400 mt-6">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="hover:text-[#ff5758] transition-colors">← Back to site</a>
    </p>

</div>

<script>
    const subdomainInput = document.getElementById('subdomain');
    const previewUrl = document.getElementById('preview-url');
    const centralDomain = '{{ config('app.central_domain', 'linkbay-cms.com') }}';
    const scheme = location.protocol;

    subdomainInput?.addEventListener('input', function () {
        const val = this.value.toLowerCase().replace(/[^a-z0-9-]/g, '-');
        this.value = val;
        const clean = val.replace(/^-+|-+$/g, '').replace(/-+/g, '-') || 'my-agency';
        previewUrl.textContent = clean + '.' + centralDomain + '/dashboard';
    });

    function handleFind(e) {
        e.preventDefault();
        const raw = subdomainInput.value.trim().toLowerCase();
        const sub = raw
            .replace(/[^a-z0-9-]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-+|-+$/g, '');
        if (!sub) {
            showError('Please enter your agency subdomain.');
            return;
        }
        const url = scheme + '//' + sub + '.' + centralDomain + '/dashboard/login';
        window.location.href = url;
    }

    function showError(msg) {
        const el = document.getElementById('error-msg');
        el.textContent = msg;
        el.classList.remove('hidden');
    }
</script>
</body>
</html>
