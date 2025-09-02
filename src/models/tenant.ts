export interface Tenant {
  id: number;
  name: string;
  subdomain: string;
  status: string;
  stripe_connect_id?: string | null;
  paypal_merchant_id?: string | null;
  created_at?: string;
  updated_at?: string;
}
