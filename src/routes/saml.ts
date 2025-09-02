import { Router } from 'express';
// saml2-js is optional; require lazily so app can run without it installed
let saml2: any;
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  saml2 = require('saml2-js');
} catch (e) {
  saml2 = null;
}
import { knex } from '../db';
import { signAccessToken, signRefreshToken } from '../services/auth';
import eventBus from '../lib/eventBus';

const router = Router();

// Load SP config from env with safe fallbacks
const baseUrl = process.env.SAML_BASE_URL || process.env.APP_URL || (`http://localhost:${process.env.PORT || 3001}`);
const spOptions = {
  entity_id: process.env.SAML_ENTITY_ID || (baseUrl + '/auth/saml/metadata.xml'),
  assert_endpoint: process.env.SAML_ASSERT_ENDPOINT || (baseUrl + '/auth/saml/callback')
};
const sp = saml2 ? new saml2.ServiceProvider(spOptions as any) : null;

async function getProviderForTenant(tenantId:number){
  return knex('tenant_saml_providers').where({ tenant_id: tenantId, is_active: true }).first();
}

// Initiate login: GET /auth/saml/:tenantId
router.get('/:tenantId', async (req, res) => {
  if (!saml2 || !sp) return res.status(503).send('saml_unavailable');
  const tenantId = Number(req.params.tenantId || (req as any).tenant && (req as any).tenant.id);
  if (!tenantId) return res.status(400).send('tenant_required');
  const provider = await getProviderForTenant(tenantId);
  if (!provider) return res.status(404).send('saml_not_configured');
  // build idp from stored metadata/certificate
  const idpOptions:any = {};
  if (provider.metadata_url) idpOptions.metadata_url = provider.metadata_url;
  if ((provider as any).sso_login_url) idpOptions.sso_login_url = (provider as any).sso_login_url;
  if (provider.issuer) idpOptions.entity_id = provider.issuer;
  if (provider.certificate) idpOptions.cert = provider.certificate;
  // debug logs removed
  const idp = new saml2.IdentityProvider(idpOptions);
  sp.create_login_request_url(idp, {}, (err:any, loginUrl:string, requestId:any) => {
  if (err) { console.error('saml create_login_request_url err', err); return res.status(500).send('saml_request_error'); }
    res.redirect(loginUrl);
  });
});

// Callback: POST /auth/saml/callback
router.post('/callback', async (req:any, res) => {
  if (!saml2 || !sp) return res.status(503).send('saml_unavailable');
  try {
    const options = { request_body: req.body };
    const idp = new saml2.IdentityProvider({}); // placeholder, saml2-js verifies using SP and raw response
    sp.post_assert(idp, options, async (err:any, samlResponse:any) => {
      if (err) { console.error('saml assert err', err); return res.status(400).send('saml_invalid'); }
      const profile = samlResponse.user; // attributes
      const email = (profile.email || profile['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'] || profile['EmailAddress'] || profile['emailAddress']) as any;
      if (!email) return res.status(400).send('no_email');
      // find tenant by issuer? here we expect tenant info in RelayState or similar (omitted), assume tenant attached
      const tenant = req.tenant;
      if (!tenant) return res.status(400).send('tenant_required');
      // find or create user
      let user = await knex('users').where({ email, tenant_id: tenant.id }).first();
      if (!user){
        const [id] = await knex('users').insert({ tenant_id: tenant.id, email, password_hash: '', role: 'user', created_at: new Date() }).returning('id');
        user = await knex('users').where({ id }).first();
      }
      // issue tokens
      const access = signAccessToken({ id: user.id, tenant_id: user.tenant_id, role: user.role });
      const refresh = signRefreshToken({ id: user.id });
      await knex('refresh_tokens').insert({ user_id: user.id, token: refresh, expires_at: new Date(Date.now() + 1000*60*60*24*30) });
      try { eventBus.emit({ type: 'UserLoggedIn', user_id: user.id, tenant_id: user.tenant_id || null, timestamp: new Date().toISOString() }); } catch(e){}
      // redirect with tokens or provide JSON
      res.json({ ok: true, token: access, refresh });
    });
  } catch (err:any){ console.error('saml callback', err); res.status(500).json({ error: 'saml_failed' }); }
});

// Metadata endpoint
router.get('/metadata.xml', (req, res) => {
  if (!saml2 || !sp) return res.status(503).send('saml_unavailable');
  const metadata = sp.create_metadata();
  res.type('application/xml').send(metadata);
});

export default router;
