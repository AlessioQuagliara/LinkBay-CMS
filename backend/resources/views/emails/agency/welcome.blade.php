<x-mail::message>
# Benvenuto su LinkBay CMS, {{ $ownerName }}!

Il tuo account **{{ $agencyName }}** è stato creato con successo.

@if ($isPending)
> La tua agenzia è in attesa di approvazione. Riceverai una email non appena il tuo account sarà attivato.
@else
Il tuo account è già **attivo**. Puoi effettuare il login alla tua dashboard:

<x-mail::button :url="$loginUrl">
Accedi alla Dashboard
</x-mail::button>
@endif

Se hai bisogno di aiuto, rispondi a questa email o visita la nostra documentazione.

Grazie,
{{ config('app.name') }}
</x-mail::message>
