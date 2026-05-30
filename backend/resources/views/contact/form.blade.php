<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact us — LinkBay-CMS</title>
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

<div class="w-full max-w-lg">

    <div class="text-center mb-8">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-4">
            @include('partials.logomark', ['variant' => 'dark'])
        </a>
        <h1 class="text-2xl font-bold text-[#343a4D]">Send us a message</h1>
        <p class="text-gray-500 mt-1 text-sm">
            Tell us about your agency and how you run client stores today.
            We respond within one business day.
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

        <form method="POST" action="{{ route('contact.store') }}" class="space-y-5">
            @csrf

            <div class="grid sm:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Your name <span class="text-[#ff5758]">*</span>
                    </label>
                    <input type="text" name="name" value="{{ old('name') }}" required maxlength="150"
                        placeholder="Jane Smith"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent @error('name') border-red-400 @enderror">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Agency / company <span class="text-[#ff5758]">*</span>
                    </label>
                    <input type="text" name="company" value="{{ old('company') }}" required maxlength="150"
                        placeholder="Acme Agency"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent @error('company') border-red-400 @enderror">
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Work email <span class="text-[#ff5758]">*</span>
                </label>
                <input type="email" name="email" value="{{ old('email') }}" required maxlength="255"
                    placeholder="jane@youragency.com"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent @error('email') border-red-400 @enderror">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    How many client stores do you manage today?
                </label>
                <select name="store_count"
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent">
                    <option value="">Select a range</option>
                    <option value="1-3" @selected(old('store_count') === '1-3')>1–3 stores</option>
                    <option value="4-10" @selected(old('store_count') === '4-10')>4–10 stores</option>
                    <option value="11-30" @selected(old('store_count') === '11-30')>11–30 stores</option>
                    <option value="31+" @selected(old('store_count') === '31+')>More than 30</option>
                    <option value="evaluating" @selected(old('store_count') === 'evaluating')>None yet — evaluating</option>
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    What would you like to discuss? <span class="text-[#ff5758]">*</span>
                </label>
                <textarea name="message" required rows="5" maxlength="5000"
                    placeholder="Tell us about your agency setup, what you're trying to solve, or any specific questions."
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#ff5758] focus:border-transparent @error('message') border-red-400 @enderror">{{ old('message') }}</textarea>
            </div>

            <button type="submit"
                class="w-full py-2.5 px-4 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
                Send message
            </button>
        </form>

        <p class="text-center text-xs text-gray-400 mt-5">
            We don&rsquo;t share your information with third parties.
        </p>

    </div>

    <p class="text-center text-xs text-gray-400 mt-6">
        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="hover:text-[#ff5758] transition-colors">← Back to site</a>
    </p>

</div>

</body>
</html>
