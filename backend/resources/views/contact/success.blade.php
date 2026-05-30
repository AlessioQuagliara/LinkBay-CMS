<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message sent — LinkBay-CMS</title>
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

<div class="w-full max-w-md text-center">

    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-8">
        @include('partials.logomark', ['variant' => 'dark'])
    </a>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
        <div class="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
        </div>

        <h1 class="text-2xl font-bold text-[#343a4D] mb-2">Message sent</h1>
        <p class="text-gray-500 text-sm mb-8">
            Thanks for reaching out. We'll get back to you within one business day.
        </p>

        <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}"
            class="inline-block px-6 py-2.5 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
            ← Back to site
        </a>
    </div>

</div>

</body>
</html>
