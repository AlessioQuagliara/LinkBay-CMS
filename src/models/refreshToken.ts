export interface RefreshToken {
  id: number;
  user_id: number;
  token: string;
  expires_at: string;
  created_at?: string;
}
