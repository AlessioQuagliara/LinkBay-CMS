<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invito non valido — {{ config('app.name') }}</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { font-family: 'Inter', system-ui, sans-serif; }</style>
</head>
<body class="min-h-screen bg-gray-50 flex items-center justify-center p-4">

<div class="w-full max-w-md text-center">

    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex justify-center mb-8">
        @include('partials.logomark', ['variant' => 'dark'])
    </a>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
        <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </div>

        @if($reason === 'expired')
            <h1 class="text-2xl font-bold text-[#343a4D] mb-2">Link scaduto</h1>
            <p class="text-gray-500 text-sm mb-8">
                Questo invito è scaduto. Chiedi all'agenzia di inviarti un nuovo link.
            </p>
        @else
            <h1 class="text-2xl font-bold text-[#343a4D] mb-2">Link non valido</h1>
            <p class="text-gray-500 text-sm mb-8">
                Questo link di invito non è valido o è già stato utilizzato.
                Se pensi ci sia un errore, contatta l'agenzia.
            </p>
        @endif
    </div>

</div>

</body>
</html>
