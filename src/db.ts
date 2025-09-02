import knexInit from 'knex';
import dotenv from 'dotenv';
dotenv.config();

export const knex = knexInit({ client: 'pg', connection: process.env.DATABASE_URL });

// Instrument queries to log slow queries in development
if (process.env.NODE_ENV !== 'production') {
	knex.on('query', (query:any) => {
		(query as any)._start = Date.now();
	});
	knex.on('query-response', async (response:any, query:any) => {
		try {
			const duration = Date.now() - (query as any)._start;
			if (duration > 100) {
				const text = (query && query.sql) ? query.sql : JSON.stringify(query);
				console.warn(`SLOW QUERY ${duration}ms: ${text}`);
				// insert into audit_logs for later inspection if table exists
				try {
					await (knex as any)('audit_logs').insert({ action: 'db.slow_query', metadata: JSON.stringify({ sql: text, duration }), created_at: new Date() });
				} catch (err) {
					// ignore
				}
			}
		} catch (err) {
			// ignore
		}
	});
}
