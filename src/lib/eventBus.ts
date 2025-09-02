import { AnalyticsEvent } from '../types/events';

export interface EventBus {
  on(eventType: string, handler: (evt: AnalyticsEvent)=>void): void;
  off(eventType: string, handler: (evt: AnalyticsEvent)=>void): void;
  emit(evt: AnalyticsEvent): void;
}

type HandlersMap = { [key: string]: Array<(evt: AnalyticsEvent)=>void> };

export class BasicEventBus implements EventBus {
  private handlers: HandlersMap = {};

  on(eventType: string, handler: (evt: AnalyticsEvent)=>void) {
    this.handlers[eventType] = this.handlers[eventType] || [];
    this.handlers[eventType].push(handler);
  }

  off(eventType: string, handler: (evt: AnalyticsEvent)=>void) {
    const list = this.handlers[eventType] || [];
    this.handlers[eventType] = list.filter(h => h !== handler);
  }

  emit(evt: AnalyticsEvent) {
    // call specific handlers
    const list = this.handlers[evt.type] || [];
    for (const h of list) {
      try { h(evt); } catch (e) { /* swallow */ }
    }
    // call wildcard handlers
    const wild = this.handlers['*'] || [];
    for (const h of wild) {
      try { h(evt); } catch (e) { /* swallow */ }
    }
  }
}

// singleton instance for app
const eventBus = new BasicEventBus();
export default eventBus;
