@extends('emails.tenant.layout')

@section('content')
<h1 style="margin:0 0 8px 0;font-size:22px;color:#111111;">Rimborso in elaborazione</h1>
<p style="margin:0 0 20px 0;color:#555555;">
  Abbiamo elaborato un rimborso per il tuo ordine <strong>{{ $orderNumber }}</strong>.
</p>

{{-- Refund summary --}}
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f0fdf4;border:1px solid #86efac;border-radius:8px;margin-bottom:24px;">
  <tr>
    <td style="padding:20px 24px;">
      <p style="margin:0 0 4px 0;font-size:12px;font-weight:600;color:#166534;text-transform:uppercase;letter-spacing:0.5px;">Importo rimborsato</p>
      <p style="margin:0;font-size:28px;font-weight:700;color:#14532d;">€{{ number_format($refundAmount, 2, ',', '.') }}</p>
    </td>
  </tr>
</table>

<p style="margin:0 0 12px 0;font-size:14px;color:#555555;">
  Il rimborso verrà accreditato sul tuo metodo di pagamento originale entro <strong>5–7 giorni lavorativi</strong>,
  a seconda del tuo istituto bancario.
</p>
<p style="margin:0;font-size:14px;color:#555555;">
  Per qualsiasi domanda scrivi a
  @if($brand->contact_email)
    <a href="mailto:{{ $brand->contact_email }}" style="color:{{ $brand->primary_color ?? '#000000' }};text-decoration:none;">{{ $brand->contact_email }}</a>.
  @else
    il nostro supporto.
  @endif
</p>
@endsection
