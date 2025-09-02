import eventBus from './eventBus';
import fetch from 'node-fetch';
import crypto from 'crypto';
import { knex } from '../db';

function sleep(ms:number){ return new Promise(res=>setTimeout(res, ms)); }

export class WebhookConsumer {
  private registered = false;
  private handler = this.handleEvent.bind(this);

  start(){
    if (this.registered) return;
    // subscribe to all events; we'll filter per-tenant webhooks
    eventBus.on('*', this.handler);
    this.registered = true;
  }

  stop(){
    if (!this.registered) return;
    eventBus.off('*', this.handler);
    this.registered = false;
  }

  private async handleEvent(evt:any): Promise<void> {
    try {
      const tenantId = evt.tenant_id || null;
      if (!tenantId) return; // only tenant-scoped events
      // find active webhooks for tenant
      const hooks = await knex('tenant_webhooks').where({ tenant_id: tenantId, is_active: true }).select('*');
      for (const h of hooks){
        const types = h.event_types ? (Array.isArray(h.event_types) ? h.event_types : JSON.parse(h.event_types)) : null;
        if (types && types.length && !types.includes(evt.type)) continue;
        // send webhook asynchronously (don't block the bus)
  this.sendWithRetry(h, evt).catch((err: any) => { console.error('webhook send failed', err && err.message); });
      }
    } catch (err:any){ console.error('webhook handler error', err && err.message); }
  }

  private async sendWithRetry(hook:any, evt:any, attempt=0): Promise<void> {
    const maxAttempts = 5;
    try {
      await this.sendOnce(hook, evt, attempt);
      // log success
      await knex('webhook_logs').insert({ tenant_id: hook.tenant_id, webhook_id: hook.id, event_type: evt.type, event_payload: JSON.stringify(evt), success: true, attempts: attempt+1, response_status: 'ok' });
    } catch (err:any){
      const nextAttempt = attempt+1;
      await knex('webhook_logs').insert({ tenant_id: hook.tenant_id, webhook_id: hook.id, event_type: evt.type, event_payload: JSON.stringify(evt), success: false, attempts: nextAttempt, error: String(err && err.message || err) });
      if (nextAttempt < maxAttempts){
        const backoff = Math.min(30000, 200 * Math.pow(2, attempt));
        await sleep(backoff);
        return this.sendWithRetry(hook, evt, nextAttempt);
      }
    }
  }

  private async sendOnce(hook:any, evt:any, attempt:number): Promise<void> {
    const payload = { event: evt.type, data: evt, attempt };
    const body = JSON.stringify(payload);
    const headers:any = { 'Content-Type': 'application/json' };
    if (hook.secret){
      const sig = crypto.createHmac('sha256', String(hook.secret)).update(body).digest('hex');
      headers['X-LinkBay-Signature'] = sig;
    }
    const res = await fetch(hook.url, { method: 'POST', body, headers, timeout: 10000 });
    if (!res.ok) throw new Error('webhook_response_'+res.status);
  }
}

const defaultConsumer = new WebhookConsumer();
if (process.env.NODE_ENV !== 'test') { try { defaultConsumer.start(); } catch(e){} }

// graceful teardown
process.on('exit', ()=>{ try { defaultConsumer.stop(); } catch(e){} });

export default defaultConsumer;
