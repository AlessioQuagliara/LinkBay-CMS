import dotenv from 'dotenv';
dotenv.config({ path: '.env.test' });

// increase default timeout for DB operations in CI
// @ts-ignore
(global as any).jest?.setTimeout?.(30_000);
