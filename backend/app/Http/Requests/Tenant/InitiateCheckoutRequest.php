<?php

declare(strict_types=1);

namespace App\Http\Requests\Tenant;

use Illuminate\Foundation\Http\FormRequest;

class InitiateCheckoutRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'cart_session_id' => ['required', 'string'],
            'shipping_method_id' => ['required', 'integer', 'exists:shipping_methods,id'],
            'shipping_address' => ['required', 'array'],
            'shipping_address.first_name' => ['required', 'string', 'max:128'],
            'shipping_address.last_name' => ['required', 'string', 'max:128'],
            'shipping_address.address_line_1' => ['required', 'string', 'max:255'],
            'shipping_address.address_line_2' => ['nullable', 'string', 'max:255'],
            'shipping_address.city' => ['required', 'string', 'max:128'],
            'shipping_address.postal_code' => ['required', 'string', 'max:16'],
            'shipping_address.country' => ['required', 'string', 'size:2'],
            'shipping_address.phone' => ['nullable', 'string', 'max:32'],
        ];
    }
}
