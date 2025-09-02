import { Router } from 'express';
import Stripe from 'stripe';
import dotenv from 'dotenv';
import { knex } from '../db';
import { getTenantDB } from '../dbMultiTenant';
import { logAuditEvent } from '../middleware/audit';
import { notifyUser, notifyTenant } from '../socket';
import eventBus from '../lib/eventBus';
dotenv.config();

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2022-11-15' });
const router = Router();

// Onboard URL creation for Stripe Express
router.post('/connect-onboard', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  // Create account if doesn't exist
  let accountId = tenant.stripe_connect_id;
  if (!accountId) {
    const acc = await stripe.accounts.create({ type: 'express' });
    accountId = acc.id;
    await knex('tenants').where({ id: tenant.id }).update({ stripe_connect_id: accountId });
  }
  const origin = req.headers.origin || `http://localhost:${process.env.PORT || 3000}`;
  const accountLink = await stripe.accountLinks.create({ account: accountId, refresh_url: `${origin}/onboard/refresh`, return_url: `${origin}/onboard/return`, type: 'account_onboarding' });
  res.json({ url: accountLink.url });
});

// Checkout - create session with application_fee and transfer_data.destination
router.post('/checkout', logAuditEvent('payment.checkout_initiated', (req)=>({ tenant: req && (req as any).tenant && (req as any).tenant.id, items: req.body.items })), async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { items, success_url, cancel_url } = req.body;
  const accountId = tenant.stripe_connect_id;
  if (!accountId) return res.status(400).json({ error: 'seller_not_connected' });
  // compute amount and application fee
  const total = items.reduce((s:number, it:any) => s + (it.price_cents || 0) * (it.quantity || 1), 0);
  const feePercent = Number(process.env.PLATFORM_FEE_PERCENT || '5');
  const appFee = Math.round(total * feePercent / 100);

  // create an order in the tenant schema with status 'pending'
  let orderId: number | null = null;
  try {
    const tenantDb = getTenantDB(tenant.id);
    const inserted: any = await tenantDb('orders').insert({
      customer_id: req.body.customer_id || null,
      items: JSON.stringify(items),
      total_cents: total,
      status: 'pending'
    }).returning('*');
    const first = Array.isArray(inserted) ? inserted[0] : inserted;
    orderId = first && (first.id || first);
  } catch (err:any) {
    console.error('failed to create tenant order', err && err.message);
    // continue: we'll still create the session but webhook will have no order metadata
  }

  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    mode: 'payment',
    line_items: items.map((it:any)=>({ price_data: { currency: 'usd', product_data: { name: it.name }, unit_amount: it.price_cents }, quantity: it.quantity })),
    payment_intent_data: {
      application_fee_amount: appFee,
      transfer_data: { destination: accountId }
    },
    metadata: {
      order_id: orderId ? String(orderId) : '',
      tenant_id: String(tenant.id)
    },
    success_url: success_url || `${req.headers.origin}/success`,
    cancel_url: cancel_url || `${req.headers.origin}/cancel`
  }, { stripeAccount: accountId });

  res.json({ url: session.url, id: session.id });
  // emit checkout started event
  try { eventBus.emit({ type: 'CheckoutStarted', tenant_id: tenant.id, items, total_cents: total, user_id: req.body.customer_id || null, timestamp: new Date().toISOString() }); } catch(e){}
});

// Create a Checkout Session for a recurring subscription (SaaS platform fee)
router.post('/subscribe', logAuditEvent('subscription.checkout_initiated', (req)=>({ tenant: req && (req as any).tenant && (req as any).tenant.id })), async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { priceId, success_url, cancel_url } = req.body;
  if (!priceId) return res.status(400).json({ error: 'price_required' });

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      metadata: { tenant_id: String(tenant.id) },
      success_url: success_url || `${req.headers.origin}/subscription/success`,
      cancel_url: cancel_url || `${req.headers.origin}/subscription/cancel`
    });
    res.json({ url: session.url, id: session.id });
  } catch (err:any) {
    console.error('failed to create subscription session', err && err.message);
    res.status(500).json({ error: 'subscription_session_failed' });
  }
});

// Webhook handler for account.updated and others
router.post('/webhook', expressRawMiddleware(), async (req, res) => {
  const sig = req.headers['stripe-signature'] as string | undefined;
  const rawBody = (req as any).rawBody as Buffer;
  try {
    const event = stripe.webhooks.constructEvent(rawBody, sig || '', process.env.STRIPE_WEBHOOK_SECRET || '');
    if (event.type === 'account.updated') {
      const acc = event.data.object as Stripe.Account;
      // find tenant by account id and update
      await knex('tenants').where({ stripe_connect_id: acc.id }).update({ stripe_connect_id: acc.id });
    }

    // invoice.paid - create invoice record and mark tenant subscription active
    if (event.type === 'invoice.paid') {
      const invoice = event.data.object as Stripe.Invoice & { metadata?: any };
      const tenantId = invoice.metadata && invoice.metadata.tenant_id ? Number(invoice.metadata.tenant_id) : null;
      if (tenantId) {
        try {
          await knex('invoices').insert({
            tenant_id: tenantId,
            stripe_invoice_id: invoice.id,
            amount_cents: invoice.amount_paid || invoice.amount_due || 0,
            currency: invoice.currency || 'usd',
            status: 'paid',
            period_start: invoice.period_start ? new Date((invoice.period_start as any) * 1000) : null,
            period_end: invoice.period_end ? new Date((invoice.period_end as any) * 1000) : null,
            paid_at: invoice.status === 'paid' ? new Date() : null,
            metadata: invoice.metadata || {}
          });
          // update tenant subscription status
          await knex('tenants').where({ id: tenantId }).update({ subscription_status: 'active', subscription_expires_at: invoice.period_end ? new Date((invoice.period_end as any) * 1000) : null });
        } catch (err:any) {
          console.error('failed to persist invoice', err && err.message);
        }
      }
    }

    // customer.subscription.deleted - mark tenant subscription as cancelled
    if (event.type === 'customer.subscription.deleted') {
      const subscription = event.data.object as Stripe.Subscription & { metadata?: any };
      const tenantId = subscription.metadata && subscription.metadata.tenant_id ? Number(subscription.metadata.tenant_id) : null;
      if (tenantId) {
        try {
          await knex('tenants').where({ id: tenantId }).update({ subscription_status: 'cancelled', subscription_expires_at: new Date(subscription.current_period_end ? (subscription.current_period_end as any) * 1000 : Date.now()) });
        } catch (err:any) {
          console.error('failed to mark tenant subscription cancelled', err && err.message);
        }
      }
    }

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session & { metadata?: any };
      const metadata = session.metadata || {};
      const orderId = metadata.order_id;
      const tenantId = metadata.tenant_id ? Number(metadata.tenant_id) : null;
      if (orderId && tenantId) {
        const tenantDb = getTenantDB(Number(tenantId));
        try {
          // mark order as paid
          await tenantDb('orders').where({ id: Number(orderId) }).update({ status: 'paid', updated_at: new Date() });
          console.log(`Order ${orderId} marked as paid for tenant ${tenantId}`);

          // try to decrement stock for variants if items include variant_id
          try {
            const order = await tenantDb('orders').where({ id: Number(orderId) }).first();
            const items = order && order.items ? JSON.parse(order.items) : [];
            for (const it of items) {
              if (it.variant_id) {
                // decrement stock atomically
                await tenantDb.transaction(async (trx) => {
                  const v = await trx('product_variants').where({ id: it.variant_id }).first();
                  if (v) {
                    const newStock = Math.max(0, (v.stock || 0) - (it.quantity || 1));
                    await trx('product_variants').where({ id: it.variant_id }).update({ stock: newStock, updated_at: new Date() });
                  }
                });
              }
            }
          } catch (err2:any) {
            console.error('failed to decrement variant stock', err2 && err2.message);
          }

          // notify customer and tenant about payment processed
          try {
            const orderRow = await tenantDb('orders').where({ id: Number(orderId) }).first();
            if (orderRow && orderRow.customer_id) notifyUser(orderRow.customer_id, 'order.paid', { order_id: orderId, tenant_id: tenantId });
            notifyTenant(tenantId, 'order.paid', { order_id: orderId });
          } catch (errn:any) {
            console.error('failed to send socket notifications for order paid', errn && errn.message);
          }
          // emit purchase completed (use orderRow total if available, otherwise session amount_total)
          try {
            const orderRow = await tenantDb('orders').where({ id: Number(orderId) }).first();
            const amount = orderRow && orderRow.total_cents ? Number(orderRow.total_cents) : (session.amount_total ? Number(session.amount_total) : undefined);
            eventBus.emit({ type: 'PurchaseCompleted', tenant_id: tenantId, order_id: Number(orderId), amount_cents: amount, user_id: orderRow && orderRow.customer_id ? orderRow.customer_id : null, timestamp: new Date().toISOString() });
          } catch(e){}

        } catch (err:any) {
          console.error('failed to mark order paid', err && err.message);
        }
      } else {
        console.warn('checkout.session.completed received without order metadata', { metadata });
      }
    }
    res.json({ received: true });
  } catch (err:any) {
    console.error('stripe webhook error', err && err.message);
    res.status(400).send(`Webhook Error: ${err.message}`);
  }
});

function expressRawMiddleware() {
  // capture raw body for webhook signature verification
  return (req:any, res:any, next:any) => {
    let data: any = [];
    req.setEncoding('utf8');
    req.on('data', (chunk:any) => { data.push(chunk); });
    req.on('end', () => { req.rawBody = Buffer.from(data.join('')) ; next(); });
  };
}

export default router;
