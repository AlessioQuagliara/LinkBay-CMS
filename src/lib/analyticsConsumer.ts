import knexInit from 'knex';
import eventBus from './eventBus';
import { AnalyticsEvent } from '../types/events';
import dotenv from 'dotenv';
dotenv.config();

const ANALYTICS_DB_URL = process.env.ANALYTICS_DATABASE_URL || process.env.DATABASE_URL;

// separate knex instance / pool for analytics
export const analyticsKnex = knexInit({ client: 'pg', connection: ANALYTICS_DB_URL, pool: { min: 0, max: 5 } });

function sleep(ms:number){ return new Promise(res=>setTimeout(res, ms)); }

export class DatabaseAnalyticsConsumer {
  private registered = false;
  private handler = this.handleEvent.bind(this);

  start() {
    if (this.registered) return;
    // subscribe to all analytic events
    eventBus.on('*', this.handler);
    // also subscribe to specific types for efficiency
    ['PageView','ProductViewed','AddToCart','CheckoutStarted','PurchaseCompleted','UserLoggedIn'].forEach(t=>eventBus.on(t, this.handler));
    this.registered = true;
  }

  stop() {
    if (!this.registered) return;
    eventBus.off('*', this.handler);
    ['PageView','ProductViewed','AddToCart','CheckoutStarted','PurchaseCompleted','UserLoggedIn'].forEach(t=>eventBus.off(t, this.handler));
    this.registered = false;
  }

  private async handleEvent(evt: AnalyticsEvent) {
    try {
      await this.saveEventWithRetry(evt);
    } catch (err) {
      // last-resort: log but don't crash the app
      try { console.error('analytics save failed', (err as any).message || err); } catch(e){}
    }
  }

  private async saveEventWithRetry(evt: AnalyticsEvent, attempts = 0): Promise<void> {
    const maxAttempts = 5;
    try {
      await this.saveEvent(evt);
    } catch (err:any) {
      const retriable = (err && err.code && ['57P01','57P03','53300','ECONNRESET','ETIMEDOUT'].includes(err.code)) || attempts < 3;
      if (retriable && attempts < maxAttempts) {
        const backoff = Math.min(2000, 100 * Math.pow(2, attempts));
        await sleep(backoff);
        return this.saveEventWithRetry(evt, attempts+1);
      }
      throw err;
    }
  }

  private async saveEvent(evt: AnalyticsEvent) {
    // Map our events to analytics.events columns
    const common: any = {
      tenant_id: (evt as any).tenant_id || null,
      event_type: (evt as any).type ? String((evt as any).type).toLowerCase() : 'unknown',
      event_data: {},
      user_id: (evt as any).user_id || null,
      session_id: (evt as any).session_id || null,
      url_path: (evt as any).path || (evt as any).url_path || null,
      timestamp: evt && (evt as any).timestamp ? new Date((evt as any).timestamp) : new Date()
    };

    // populate event_data with the whole event payload minus duplicated fields
    const payload: any = { ...evt } as any;
    delete payload.type; delete payload.tenant_id; delete payload.user_id; delete payload.session_id; delete payload.path; delete payload.url_path; delete payload.timestamp;
    common.event_data = payload;

  await analyticsKnex('analytics.events').insert({
      tenant_id: common.tenant_id,
      event_type: common.event_type,
      event_data: JSON.stringify(common.event_data),
      user_id: common.user_id,
      session_id: common.session_id,
      url_path: common.url_path,
      timestamp: common.timestamp
    });
  }
}

// default instance and auto-start in development
const defaultConsumer = new DatabaseAnalyticsConsumer();
if (process.env.NODE_ENV !== 'test') {
  try { defaultConsumer.start(); } catch(e) { /* ignore startup errors */ }
}

// graceful shutdown: destroy analytics pool on process exit
process.on('exit', () => { try { analyticsKnex.destroy(); } catch(e){} });
process.on('SIGINT', () => { try { analyticsKnex.destroy(); } catch(e){} process.exit(0); });

export default defaultConsumer;
