@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Verifica il tuo indirizzo email</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Ciao <strong>{{ $customer->name }}</strong>! Per completare la registrazione su <strong>{{ $brand->store_name }}</strong>
  devi verificare il tuo indirizzo email.
</p>

<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:24px;">
  <tr>
    <td align="center">
      <a href="{{ $verificationUrl }}"
         style="display:inline-block;background-color:{{ $brand->primary_color ?? '#000000' }};color:#ffffff;text-decoration:none;padding:12px 28px;border-radius:6px;font-size:15px;font-weight:600;">
        Verifica email
      </a>
    </td>
  </tr>
</table>

<p style="margin:0 0 8px 0;font-size:13px;color:#888888;">
  Se il bottone non funziona, copia e incolla questo link nel browser:
</p>
<p style="margin:0;font-size:12px;color:#aaaaaa;word-break:break-all;">
  {{ $verificationUrl }}
</p>
@endsection
