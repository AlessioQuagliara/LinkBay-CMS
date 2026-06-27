@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Il tuo ordine è in arrivo!</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Il tuo ordine <strong>{{ $orderNumber }}</strong> è stato affidato al corriere <strong>{{ $carrierName }}</strong>.
</p>

{{-- Tracking box --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;margin-bottom:24px;">
  <tr>
    <td style="padding:20px 24px;">
      <p style="margin:0 0 4px 0;font-size:12px;font-weight:600;color:#0284c7;text-transform:uppercase;letter-spacing:0.5px;">Numero di tracking</p>
      <p style="margin:0 0 16px 0;font-size:20px;font-weight:700;color:#0c4a6e;letter-spacing:1px;">{{ $trackingNumber }}</p>
      <a href="{{ $trackingUrl }}"
         style="display:inline-block;background-color:{{ $brand->primary_color ?? '#000000' }};color:#ffffff;text-decoration:none;padding:10px 20px;border-radius:6px;font-size:14px;font-weight:600;">
        Traccia la spedizione
      </a>
    </td>
  </tr>
</table>

<p style="margin:0;font-size:14px;color:#555555;">
  In caso di problemi con la spedizione, contatta il corriere con il codice di tracking oppure scrivi a
  @if($brand->contact_email)
    <a href="mailto:{{ $brand->contact_email }}" style="color:{{ $brand->primary_color ?? '#000000' }};text-decoration:none;">{{ $brand->contact_email }}</a>.
  @else
    il nostro supporto.
  @endif
</p>
@endsection
