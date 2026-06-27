@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Benvenuto/a, {{ $customer->name }}!</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Siamo felici di averti con noi. Il tuo account su <strong>{{ $brand->store_name }}</strong> è pronto.
</p>

<p style="margin:0 0 24px 0;color:#555555;">
  Puoi già iniziare a sfogliare il catalogo, aggiungere prodotti al carrello e gestire i tuoi ordini in tutta comodità.
</p>

<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:24px;">
  <tr>
    <td align="center">
      <a href="{{ request()->getSchemeAndHttpHost() }}"
         style="display:inline-block;background-color:{{ $brand->primary_color ?? '#000000' }};color:#ffffff;text-decoration:none;padding:12px 28px;border-radius:6px;font-size:15px;font-weight:600;">
        Vai al negozio
      </a>
    </td>
  </tr>
</table>

<p style="margin:0;font-size:13px;color:#888888;">
  Se non hai creato tu questo account, ignora questa email.
</p>
@endsection
