<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apply — {{ $job->title }} — LinkBay-CMS</title>
    <link rel="icon" type="image/svg+xml" href="/image/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gray-50">

{{-- Header bar --}}
<div class="bg-[#343a4D] text-white px-4 py-3 flex items-center justify-between">
    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}/work-with-us"
       class="text-sm text-gray-300 hover:text-white transition-colors">
        ← Back to open roles
    </a>
    <a href="{{ config('app.frontend_url', 'http://localhost:3000') }}" class="inline-flex items-center">
        @include('partials.logomark', ['variant' => 'white'])
    </a>
</div>

<div class="max-w-2xl mx-auto px-4 py-12">

    {{-- Role context --}}
    <div class="mb-8">
        <div class="flex flex-wrap gap-2 mb-3">
            <span class="bg-blue-100 text-blue-800 px-2.5 py-1 rounded text-xs font-medium">
                {{ str_replace('_', '-', $job->employment_type) }}
            </span>
            <span class="bg-green-100 text-green-800 px-2.5 py-1 rounded text-xs font-medium">
                {{ $job->location }}
            </span>
            <span class="bg-purple-100 text-purple-800 px-2.5 py-1 rounded text-xs font-medium">
                {{ $job->department }}
            </span>
            @if($job->work_mode === 'remote')
                <span class="bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-xs font-medium">Remote</span>
            @elseif($job->work_mode === 'hybrid')
                <span class="bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-xs font-medium">Hybrid</span>
            @else
                <span class="bg-gray-100 text-gray-700 px-2.5 py-1 rounded text-xs font-medium">On-site</span>
            @endif
        </div>

        <h1 class="text-2xl font-bold text-[#343a4D] mb-2">{{ $job->title }}</h1>
        <p class="text-gray-600">{{ $job->summary }}</p>
    </div>

    {{-- Application form --}}
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <h2 class="text-lg font-semibold text-[#343a4D] mb-6">Your application</h2>

        @if($errors->any())
            <div class="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
                <ul class="list-disc list-inside space-y-1">
                    @foreach($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form method="POST" action="{{ route('careers.submit', $job->slug) }}"
              enctype="multipart/form-data" class="space-y-5">
            @csrf

            <div class="grid sm:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Full name <span class="text-[#ff5758]">*</span>
                    </label>
                    <input type="text" name="full_name" value="{{ old('full_name') }}"
                        required maxlength="150" placeholder="Jane Smith"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('full_name') border-red-400 @enderror">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Email <span class="text-[#ff5758]">*</span>
                    </label>
                    <input type="email" name="email" value="{{ old('email') }}"
                        required maxlength="255" placeholder="jane@example.com"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('email') border-red-400 @enderror">
                </div>
            </div>

            <div class="grid sm:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input type="tel" name="phone" value="{{ old('phone') }}"
                        maxlength="50" placeholder="+39 333 000 0000"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758]">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <input type="text" name="location" value="{{ old('location') }}"
                        maxlength="150" placeholder="City, Country"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758]">
                </div>
            </div>

            <div class="grid sm:grid-cols-2 gap-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">LinkedIn URL</label>
                    <input type="url" name="linkedin_url" value="{{ old('linkedin_url') }}"
                        maxlength="500" placeholder="https://linkedin.com/in/..."
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('linkedin_url') border-red-400 @enderror">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Portfolio / GitHub URL</label>
                    <input type="url" name="portfolio_url" value="{{ old('portfolio_url') }}"
                        maxlength="500" placeholder="https://github.com/..."
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('portfolio_url') border-red-400 @enderror">
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Why are you applying for this role? <span class="text-[#ff5758]">*</span>
                </label>
                <textarea name="motivation" required rows="4" maxlength="5000"
                    placeholder="What draws you to this specific role and what you can contribute..."
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('motivation') border-red-400 @enderror">{{ old('motivation') }}</textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Relevant experience <span class="text-[#ff5758]">*</span>
                </label>
                <textarea name="experience_summary" required rows="4" maxlength="5000"
                    placeholder="Describe your most relevant past work, projects, or experience..."
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#ff5758] @error('experience_summary') border-red-400 @enderror">{{ old('experience_summary') }}</textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    CV / Resume <span class="text-[#ff5758]">*</span>
                </label>
                <div class="border-2 border-dashed border-gray-300 rounded-lg px-4 py-5 text-center hover:border-[#ff5758] transition-colors @error('cv') border-red-400 @enderror">
                    <input type="file" name="cv" id="cv" accept=".pdf,.doc,.docx"
                        required class="hidden" onchange="updateFileLabel(this)">
                    <label for="cv" class="cursor-pointer">
                        <div class="text-sm text-gray-600 mb-1">
                            <span class="font-medium text-[#ff5758]">Click to upload</span> or drag and drop
                        </div>
                        <div id="file-label" class="text-xs text-gray-400">PDF, DOC or DOCX — max 10 MB</div>
                    </label>
                </div>
            </div>

            <button type="submit"
                class="w-full py-2.5 px-4 bg-[#ff5758] hover:bg-[#e04e4f] text-white font-semibold rounded-lg text-sm transition-colors">
                Submit application
            </button>

            <p class="text-center text-xs text-gray-400">
                Your information will be used only to evaluate your application.
            </p>
        </form>
    </div>

    {{-- Full description (below form) --}}
    @if($job->description || $job->requirements || $job->responsibilities)
        <div class="mt-8 bg-white rounded-2xl shadow-sm border border-gray-200 p-8 space-y-6">
            <h2 class="text-lg font-semibold text-[#343a4D]">Role details</h2>

            @if($job->description)
                <div class="text-gray-700 text-sm leading-relaxed whitespace-pre-line">{{ $job->description }}</div>
            @endif

            @if($job->responsibilities && count($job->responsibilities))
                <div>
                    <h3 class="text-sm font-semibold text-[#343a4D] uppercase tracking-wide mb-3">Responsibilities</h3>
                    <ul class="space-y-1.5">
                        @foreach($job->responsibilities as $item)
                            <li class="flex items-start gap-2 text-sm text-gray-700">
                                <span class="text-[#ff5758] mt-1 shrink-0">•</span>{{ $item }}
                            </li>
                        @endforeach
                    </ul>
                </div>
            @endif

            @if($job->requirements && count($job->requirements))
                <div>
                    <h3 class="text-sm font-semibold text-[#343a4D] uppercase tracking-wide mb-3">What we look for</h3>
                    <ul class="space-y-1.5">
                        @foreach($job->requirements as $item)
                            <li class="flex items-start gap-2 text-sm text-gray-700">
                                <span class="text-[#ff5758] mt-1 shrink-0">•</span>{{ $item }}
                            </li>
                        @endforeach
                    </ul>
                </div>
            @endif

            @if($job->nice_to_have && count($job->nice_to_have))
                <div>
                    <h3 class="text-sm font-semibold text-[#343a4D] uppercase tracking-wide mb-3">Nice to have</h3>
                    <ul class="space-y-1.5">
                        @foreach($job->nice_to_have as $item)
                            <li class="flex items-start gap-2 text-sm text-gray-700">
                                <span class="text-gray-400 mt-1 shrink-0">◦</span>{{ $item }}
                            </li>
                        @endforeach
                    </ul>
                </div>
            @endif
        </div>
    @endif
</div>

<script>
function updateFileLabel(input) {
    const label = document.getElementById('file-label');
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const size = (file.size / (1024 * 1024)).toFixed(1);
        label.textContent = file.name + ' (' + size + ' MB)';
        label.classList.add('text-[#ff5758]', 'font-medium');
    }
}
</script>

</body>
</html>
