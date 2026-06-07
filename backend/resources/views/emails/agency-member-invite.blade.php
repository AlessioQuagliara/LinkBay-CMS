<x-mail::message>
# Ciao!

Sei stato invitato a far parte del team di **{{ $agencyName }}** con il ruolo di **{{ $roleLabel }}**.

Clicca il pulsante qui sotto per accettare l'invito e impostare la tua password.

<x-mail::button :url="$inviteUrl">
Accetta invito
</x-mail::button>

Questo link è valido fino al **{{ $expiresAt }}**.

Se non ti aspettavi questo invito, ignora questa email.

Grazie,<br>
{{ config('app.name') }}
</x-mail::message>
