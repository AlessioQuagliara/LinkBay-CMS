@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Nuovo ordine ricevuto</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  È arrivato un nuovo ordine <strong>{{ $orderNumber }}</strong>
  @if($order->customer)da <strong>{{ $order->customer->name }}</strong> ({{ $order->customer->email }})@endif.
</p>

{{-- Summary box --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;margin-bottom:20px;">
  <tr>
    <td style="padding:16px 20px;">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
        <tr>
          <td style="font-size:13px;color:#6b7280;padding-bottom:4px;">Totale ordine</td>
          <td align="right" style="font-size:18px;font-weight:700;color:#111111;">€{{ number_format((float)$order->total, 2, ',', '.') }}</td>
        </tr>
        <tr>
          <td style="font-size:13px;color:#6b7280;">Stato</td>
          <td align="right" style="font-size:13px;font-weight:600;color:#16a34a;">{{ ucfirst($order->status) }}</td>
        </tr>
        <tr>
          <td style="font-size:13px;color:#6b7280;">Pagamento</td>
          <td align="right" style="font-size:13px;color:#333333;">{{ ucfirst($order->payment_method ?? '—') }} · {{ ucfirst($order->payment_status ?? '—') }}</td>
        </tr>
      </table>
    </td>
  </tr>
</table>

{{-- Items --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border:1px solid #e5e5e5;border-radius:6px;overflow:hidden;margin-bottom:20px;">
  <tr style="background-color:#f9f9f9;">
    <th align="left" style="padding:8px 12px;font-size:11px;color:#888888;font-weight:600;text-transform:uppercase;">Prodotto</th>
    <th align="center" style="padding:8px 12px;font-size:11px;color:#888888;font-weight:600;text-transform:uppercase;">Qtà</th>
    <th align="right" style="padding:8px 12px;font-size:11px;color:#888888;font-weight:600;text-transform:uppercase;">Totale</th>
  </tr>
  @foreach($order->items as $item)
  <tr style="border-top:1px solid #e5e5e5;">
    <td style="padding:8px 12px;font-size:13px;color:#333333;">{{ $item->name }}</td>
    <td align="center" style="padding:8px 12px;font-size:13px;color:#333333;">{{ $item->quantity }}</td>
    <td align="right" style="padding:8px 12px;font-size:13px;color:#333333;">€{{ number_format((float)$item->total, 2, ',', '.') }}</td>
  </tr>
  @endforeach
</table>

<table role="presentation" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td align="center">
      <a href="{{ url('/admin/orders') }}"
         style="display:inline-block;background-color:{{ $brand->primary_color ?? '#000000' }};color:#ffffff;text-decoration:none;padding:10px 22px;border-radius:6px;font-size:14px;font-weight:600;">
        Gestisci ordine nel pannello
      </a>
    </td>
  </tr>
</table>
@endsection
