# Staging Deploy — Proposal

There is currently no staging environment and no deploy automation beyond CI
(tests + build, no `deploy` job). This is a minimal proposal deliberately
scoped for a beta, not a scalable-infra rewrite — one small VPS, the same
`compose.yaml` already used for local/production, no Kubernetes/Terraform/CD
platform.

## Why this shape

`compose.yaml` was already written domain-agnostic (no `.test`/`localhost`
baked in — see its own header comment) specifically so the same file works
for both production and staging; only `compose.override.local.yml` is
dev-only. That means staging needs **no new container topology**, just:

1. A second small VPS (or a second Docker context on the same box, if you
   want to cut cost further — see caveat below).
2. A staging domain (e.g. `staging.linkbay-cms.com`, wildcard
   `*.staging.linkbay-cms.com` for tenant/agency subdomains) with DNS pointed
   at that VPS.
3. A `.env` on that VPS with `CENTRAL_DOMAIN=staging.linkbay-cms.com`,
   `APP_STRIPE_*` set to **test mode** keys (never live keys on staging),
   and its own Postgres volume — completely isolated from production data.

## Setup (one-time)

```bash
# On the staging VPS
git clone <repo-url> linkbay-staging
cd linkbay-staging
cp .env.example .env               # fill in staging values, see below
cp backend/.env.example backend/.env
# edit both — staging domain, test-mode Stripe keys, real SMTP sandbox creds,
# LOG_SLACK_WEBHOOK_URL if you want failure alerts from staging too
docker compose -f compose.yaml build
docker compose -f compose.yaml up -d
docker compose -f compose.yaml exec php php artisan migrate --force
docker compose -f compose.yaml exec php php artisan db:seed --class=PlanSeeder
```

Key staging-specific env values (root `.env`):

```
APP_ENV=production          # yes, even on staging — this flag governs Laravel
                             # optimizations, not "is this the real prod DB"
CENTRAL_DOMAIN=staging.linkbay-cms.com
SESSION_DOMAIN=.staging.linkbay-cms.com
APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
APP_STRIPE_SECRET_KEY=sk_test_...
APP_STRIPE_WEBHOOK_SECRET=whsec_...          # from `stripe listen` or a
                                              # dashboard-configured test webhook
NEXT_PUBLIC_API_BASE_URL=https://app.staging.linkbay-cms.com
```

## Redeploying (every push you want to promote)

```bash
./scripts/deploy-staging.sh          # defaults to origin/main
./scripts/deploy-staging.sh v1.4.0   # or deploy a specific tag/ref
```

The script (`scripts/deploy-staging.sh`) fetches, checks out the ref,
rebuilds images, runs migrations, re-caches config/routes, and checks `/up`
before declaring success. Run it by hand over SSH, or wire a "Deploy to
staging" **manual** GitHub Actions `workflow_dispatch` job that SSHs in and
runs it — deliberately not on every push to `main`, so a broken commit on
`main` doesn't immediately wreck the one demo environment you have. Example:

```yaml
# .github/workflows/deploy-staging.yml (not yet created — add when the VPS exists)
name: Deploy to Staging
on:
  workflow_dispatch:
    inputs:
      ref:
        description: "Git ref to deploy"
        default: "main"
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.STAGING_SSH_KEY }}
      - run: ssh -o StrictHostKeyChecking=no deploy@staging.linkbay-cms.com
          "cd linkbay-staging && ./scripts/deploy-staging.sh ${{ inputs.ref }}"
```

Not created yet because it needs `STAGING_SSH_KEY` and an actual host to
target — add it once the VPS exists rather than have a workflow that always
fails.

## Rollback

```bash
./scripts/deploy-staging.sh <previous-tag-or-commit>
```

Same script, older ref — rebuilds and re-migrates against the older code.
Migrations are additive-only in this codebase (no destructive rollback
tooling observed), so rolling back code while leaving the DB schema ahead is
normally safe; if a migration was destructive, restore the staging DB volume
snapshot instead (take one before risky migrations — `docker compose exec db
pg_dump ...`).

## Deliberately not doing (would be overengineering for a beta)

- No blue/green or zero-downtime deploy — a beta staging box can have a
  few seconds of downtime during `docker compose up -d`.
- No auto-deploy on every push — reduces "why is staging broken" noise
  while the team is still stabilizing CI (see pre-demo-checklist.md).
- No separate staging Kubernetes/ECS/Nomad cluster — same Compose file as
  local/prod is the whole point.
- No infra-as-code (Terraform/Pulumi) for a single VPS — provision it by
  hand once, document the steps here, revisit if a second environment is
  ever needed.

## Residual gap

This proposal assumes a VPS with Docker already exists or will be
provisioned by hand (out of scope here — no cloud credentials or account
access available to do it directly). Everything above is ready to run the
moment that VPS exists.
