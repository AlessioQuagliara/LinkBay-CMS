{{--
  Inline HTML wordmark — renders correctly with Electrolize loaded via Google Fonts.
  Usage: @include('partials.logomark', ['variant' => 'dark'])
  variant: 'dark' (default) | 'white'
--}}
@php $textColor = ($variant ?? 'dark') === 'white' ? '#ffffff' : '#343a4D'; @endphp
<span style="display:inline-flex;align-items:center;gap:0.28em;font-family:'Electrolize',monospace;text-decoration:none;" aria-label="LinkBay-CMS">
    <span style="color:{{ $textColor }};font-size:1.5em;line-height:1;letter-spacing:-0.01em;font-weight:400;">LinkBay</span>
    <span style="background:#ff5758;color:#ffffff;font-size:0.62em;padding:0.3em 0.55em;border-radius:0.25em;letter-spacing:0.06em;line-height:1;font-weight:400;">CMS</span>
</span>
