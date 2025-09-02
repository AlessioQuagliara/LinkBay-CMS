export interface User {
  id: number;
  tenant_id: number;
  email: string;
  password_hash: string;
  role: 'super_admin' | 'tenant_admin' | 'user' | 'agency';
  email_verified: boolean;
  created_at?: string;
  updated_at?: string;
}
