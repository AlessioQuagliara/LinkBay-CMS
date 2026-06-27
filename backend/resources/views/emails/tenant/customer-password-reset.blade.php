@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Reimposta la tua password</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Abbiamo ricevuto una richiesta di reimpostazione password per l'account associato a <strong>{{ $customer->email }}</strong>.
</p>

<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:20px;">
  <tr>
    <td align="center">
      <a href="{{ $resetUrl }}"
         style="display:inline-block;background-color:{{ $brand->primary_color ?? '#000000' }};color:#ffffff;text-decoration:none;padding:12px 28px;border-radius:6px;font-size:15px;font-weight:600;">
        Reimposta password
      </a>
    </td>
  </tr>
</table>

<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#fffbeb;border:1px solid #fcd34d;border-radius:6px;margin-bottom:20px;">
  <tr>
    <td style="padding:12px 16px;font-size:13px;color:#92400e;">
      ⏱ Questo link scade tra <strong>60 minuti</strong>. Dopo la scadenza, richiedi un nuovo link.
    </td>
  </tr>
</table>

<p style="margin:0;font-size:13px;color:#888888;">
  Se non hai richiesto il reset della password, ignora questa email. Il tuo account è al sicuro.
</p>
@endsection
