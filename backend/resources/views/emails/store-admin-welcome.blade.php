<x-mail::message>
# Welcome to {{ $storeName }}!

Your new store has been set up and is ready for you to explore.

Before you can log in, you need to set your password. Click the button below — this link is valid for **24 hours**.

<x-mail::button :url="$resetUrl">
Set Your Password
</x-mail::button>

Once your password is set, you can access your store dashboard at any time:

<x-mail::button :url="$storeUrl" color="success">
Go to Store Dashboard
</x-mail::button>

If you did not expect this email, you can safely ignore it.

Thanks,<br>
{{ config('app.name') }}
</x-mail::message>
