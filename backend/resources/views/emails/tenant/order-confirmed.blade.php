@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Grazie per il tuo ordine!</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Abbiamo ricevuto il tuo ordine <strong>{{ $orderNumber }}</strong> e lo stiamo elaborando.
</p>

{{-- Order items table --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border:1px solid #e5e5e5;border-radius:6px;overflow:hidden;margin-bottom:20px;">
  <tr style="background-color:#f9f9f9;">
    <th align="left" style="padding:10px 12px;font-size:12px;color:#888888;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Prodotto</th>
    <th align="center" style="padding:10px 12px;font-size:12px;color:#888888;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Qtà</th>
    <th align="right" style="padding:10px 12px;font-size:12px;color:#888888;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Prezzo</th>
  </tr>
  @foreach($order->items as $item)
  <tr style="border-top:1px solid #e5e5e5;">
    <td style="padding:10px 12px;font-size:14px;color:#333333;">{{ $item->name }}</td>
    <td align="center" style="padding:10px 12px;font-size:14px;color:#333333;">{{ $item->quantity }}</td>
    <td align="right" style="padding:10px 12px;font-size:14px;color:#333333;">€{{ number_format((float)$item->total, 2, ',', '.') }}</td>
  </tr>
  @endforeach
</table>

{{-- Totals --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:24px;">
  @if((float)$order->discount_total > 0)
  <tr>
    <td style="padding:3px 0;font-size:14px;color:#555555;">Sconto</td>
    <td align="right" style="padding:3px 0;font-size:14px;color:#22c55e;">−€{{ number_format((float)$order->discount_total, 2, ',', '.') }}</td>
  </tr>
  @endif
  <tr>
    <td style="padding:3px 0;font-size:14px;color:#555555;">Spedizione ({{ $order->shippingMethod?->name ?? '—' }})</td>
    <td align="right" style="padding:3px 0;font-size:14px;color:#555555;">€{{ number_format((float)$order->shipping_total, 2, ',', '.') }}</td>
  </tr>
  <tr>
    <td style="padding:8px 0 0 0;font-size:16px;font-weight:700;color:#111111;border-top:1px solid #e5e5e5;">Totale</td>
    <td align="right" style="padding:8px 0 0 0;font-size:16px;font-weight:700;color:#111111;border-top:1px solid #e5e5e5;">€{{ number_format((float)$order->total, 2, ',', '.') }}</td>
  </tr>
</table>

{{-- Shipping address --}}
@if($order->shipping_address)
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:20px;">
  <tr>
    <td style="width:50%;vertical-align:top;padding-right:12px;">
      <p style="margin:0 0 6px 0;font-size:12px;font-weight:600;color:#888888;text-transform:uppercase;letter-spacing:0.5px;">Indirizzo di spedizione</p>
      <p style="margin:0;font-size:14px;color:#333333;line-height:1.5;">
        {{ $order->shipping_address['name'] ?? $order->customer?->name }}<br>
        {{ $order->shipping_address['address_line1'] ?? '' }}<br>
        @if(!empty($order->shipping_address['address_line2'])){{ $order->shipping_address['address_line2'] }}<br>@endif
        {{ $order->shipping_address['city'] ?? '' }}, {{ $order->shipping_address['postal_code'] ?? '' }}<br>
        {{ $order->shipping_address['country'] ?? '' }}
      </p>
    </td>
    <td style="width:50%;vertical-align:top;padding-left:12px;">
      <p style="margin:0 0 6px 0;font-size:12px;font-weight:600;color:#888888;text-transform:uppercase;letter-spacing:0.5px;">Metodo di pagamento</p>
      <p style="margin:0;font-size:14px;color:#333333;">{{ ucfirst($order->payment_method ?? 'carta') }}</p>
    </td>
  </tr>
</table>
@endif

<p style="margin:0;font-size:14px;color:#555555;">
  Riceverai una notifica non appena il tuo ordine sarà spedito.
</p>
@endsection
