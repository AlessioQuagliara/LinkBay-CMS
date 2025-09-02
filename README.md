# LinkBayCMS

Skeleton Node.js + TypeScript project for the LinkBay CMS migration.

Structure

- src/: application source
- views/: EJS views
- public/: static files
- migrations/, seeds/: knex

Run (dev)

1. cd linkbay_cms
2. npm install
3. npm run dev


Optional SAML integration
-------------------------

SAML support in LinkBayCMS is optional. The repository ships code to handle SAML authentication, but the runtime dependency `saml2-js` is optional and not required for the server to start.

To enable SAML support:

1. Install the SAML library:

	npm install saml2-js

2. Ensure the following environment variables are set (examples):

	- SAML_ENTITY_ID (optional) — entity id to expose in metadata
	- SAML_ASSERT_ENDPOINT (optional) — assertion consumer URL

3. Configure SAML providers for tenants using the `tenant_saml_providers` table. The migration that creates this table is included in `migrations/`.

Notes:

- The app now loads `saml2-js` lazily; if the package is not installed the SAML routes will return HTTP 503 (`saml_unavailable`).
- If you prefer to require SAML in all environments, add `saml2-js` to `dependencies` in `package.json`.

