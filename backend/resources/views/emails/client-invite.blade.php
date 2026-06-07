<x-mail::message>
# Ciao {{ $contactName }},

Sei stato invitato ad accedere al pannello di gestione per il negozio **{{ $storeName }}**.

Clicca il pulsante qui sotto per impostare la tua password e attivare l'accesso.

<x-mail::button :url="$inviteUrl">
Accetta invito
</x-mail::button>

Questo link è valido fino al **{{ $expiresAt }}**.

Se non ti aspettavi questo invito, ignora questa email.

Grazie,<br>
{{ config('app.name') }}
</x-mail::message>
