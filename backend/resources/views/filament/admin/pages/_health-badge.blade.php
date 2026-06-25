@php
    $classes = match ($color) {
        'success' => 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
        'warning' => 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
        'info'    => 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
        'danger'  => 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
        default   => 'bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-300',
    };
@endphp
<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {{ $classes }}">
    {{ $label }}
</span>
