type CacheEntry<T> = {
  value: T;
  expiresAt: number;
};

class SimpleCache {
  private store: Map<string, CacheEntry<any>> = new Map();

  get<T>(key: string): T | null {
    const e = this.store.get(key);
    if (!e) return null;
    if (Date.now() > e.expiresAt) {
      this.store.delete(key);
      return null;
    }
    return e.value as T;
  }

  set<T>(key: string, value: T, ttlSeconds = 30) {
    const expiresAt = Date.now() + ttlSeconds * 1000;
    this.store.set(key, { value, expiresAt });
  }

  del(key: string) {
    this.store.delete(key);
  }
}

export default new SimpleCache();
