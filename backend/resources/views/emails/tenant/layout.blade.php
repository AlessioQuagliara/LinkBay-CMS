<!DOCTYPE html>
<html lang="it" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{{ $brand->store_name }}</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">

<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f4f4f4;">
  <tr>
    <td align="center" style="padding:24px 16px;">

      {{-- Email container --}}
      <table role="presentation" cellpadding="0" cellspacing="0" width="600" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

        {{-- Header --}}
        <tr>
          <td style="background-color:{{ $brand->primary_color ?? '#000000' }};padding:28px 32px;text-align:center;">
            @if($brand->logo_url)
              <img src="{{ $brand->logo_url }}" alt="{{ $brand->store_name }}" style="max-height:48px;max-width:200px;height:auto;display:inline-block;" />
            @else
              <span style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:0.5px;">{{ $brand->store_name }}</span>
            @endif
          </td>
        </tr>

        {{-- Body --}}
        <tr>
          <td style="padding:32px 32px 24px 32px;color:#333333;font-size:15px;line-height:1.6;">
            @yield('content')
          </td>
        </tr>

        {{-- Divider --}}
        <tr>
          <td style="padding:0 32px;">
            <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
              <tr><td style="border-top:1px solid #e5e5e5;font-size:0;line-height:0;">&nbsp;</td></tr>
            </table>
          </td>
        </tr>

        {{-- Footer --}}
        <tr>
          <td style="padding:20px 32px 28px 32px;text-align:center;color:#888888;font-size:12px;line-height:1.5;">
            <p style="margin:0 0 4px 0;font-weight:600;color:#555555;">{{ $brand->store_name }}</p>
            @if($brand->contact_email)
              <p style="margin:0 0 8px 0;">
                <a href="mailto:{{ $brand->contact_email }}" style="color:#888888;text-decoration:none;">{{ $brand->contact_email }}</a>
              </p>
            @endif
            <p style="margin:0;font-size:11px;color:#aaaaaa;">
              Hai ricevuto questa email perché sei cliente di {{ $brand->store_name }}.
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>

</body>
</html>
