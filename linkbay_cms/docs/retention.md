# Retention cleanup

We provide a cleanup script to enforce retention policies defined in the `retention_policies` table.

To run once:

```bash
node -r ts-node/register scripts/retention_cleanup.ts
```

To schedule daily (linux/mac): add a cron entry that runs the command above once per day.

Configuration
- Global defaults are seeded into `retention_policies` (audit_logs_retention_days: 365, user_activity_logs_retention_days: 90).
- You can override per-tenant by inserting a row with `tenant_id` and the same `key`.

Notes
- Orders and other fiscal records may be anonymized instead of deleted. The script demonstrates anonymization for `orders` when `orders_retention_days` is set.
- The real data transfer/migration for region residency and legal requirements must be coordinated with your Ops/infra team.
