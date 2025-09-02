export type PageViewEvent = {
  type: 'PageView';
  tenant_id?: number | null;
  path: string;
  hostname?: string;
  user_id?: number | null;
  timestamp: string;
};

export type ProductViewedEvent = {
  type: 'ProductViewed';
  tenant_id?: number | null;
  product_id: number;
  user_id?: number | null;
  timestamp: string;
};

export type AddToCartEvent = {
  type: 'AddToCart';
  tenant_id?: number | null;
  product_id: number;
  variant_id?: number | null;
  quantity: number;
  user_id?: number | null;
  session_id?: string | null;
  timestamp: string;
};

export type CheckoutStartedEvent = {
  type: 'CheckoutStarted';
  tenant_id?: number | null;
  items: any[];
  total_cents: number;
  user_id?: number | null;
  timestamp: string;
};

export type PurchaseCompletedEvent = {
  type: 'PurchaseCompleted';
  tenant_id?: number | null;
  order_id?: number | null;
  amount_cents?: number;
  user_id?: number | null;
  timestamp: string;
};

export type UserLoggedInEvent = {
  type: 'UserLoggedIn';
  user_id: number;
  tenant_id?: number | null;
  ip?: string;
  timestamp: string;
};

export type AnalyticsEvent = PageViewEvent | ProductViewedEvent | AddToCartEvent | CheckoutStartedEvent | PurchaseCompletedEvent | UserLoggedInEvent;
