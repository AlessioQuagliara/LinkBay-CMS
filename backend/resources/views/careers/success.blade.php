<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application submitted — LinkBay-CMS</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gray-50 flex flex-col">

<div class="bg-[#343a4D] text-white px-4 py-3 flex items-center justify-between">
    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}/work-with-us"
       class="text-sm text-gray-300 hover:text-white transition-colors">
        ← Back to open roles
    </a>
    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex items-center">
        @include('partials.logomark', ['variant' => 'white'])
    </a>
</div>

<div class="flex-1 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md text-center">

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
            <div class="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
                <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
            </div>

            <h1 class="text-2xl font-bold text-[#343a4D] mb-2">Application submitted</h1>
            <p class="text-gray-500 text-sm mb-1">
                You applied for <strong>{{ $job->title }}</strong>.
            </p>
            <p class="text-gray-500 text-sm mb-8">
                We review every application personally. If there is a good fit, we will be in touch within a few business days.
            </p>

            <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}/work-with-us"
               class="inline-block px-6 py-2.5 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
                See other open roles
            </a>
        </div>

    </div>
</div>

</body>
</html>
