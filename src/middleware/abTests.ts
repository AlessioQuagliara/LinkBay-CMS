import { RequestHandler } from 'express';
import { knex } from '../db';
import { analyticsKnex } from '../lib/analyticsConsumer';

function pickVariant(variants:any[]) {
  // variants: [{id,name,traffic_percentage}]
  const total = variants.reduce((s:any,v:any)=>s+Number(v.traffic_percentage||0),0) || 100;
  let r = Math.random() * total;
  for (const v of variants) {
    r -= Number(v.traffic_percentage||0);
    if (r <= 0) return v;
  }
  return variants[0];
}

export const assignAbTestVariant: RequestHandler = async (req:any, res, next) => {
  const tenant = req.tenant;
  if (!tenant) return next();
  // load active tests for tenant
  const tests = await knex('ab_tests').where({ tenant_id: tenant.id, status: 'running' }).select('*');
  if (!tests || tests.length === 0) return next();

  const sessionId = req.cookies && req.cookies.session_id ? req.cookies.session_id : (req.query.session_id || null);
  // for each test, ensure we have an assignment
  req.abTests = req.abTests || {};
  for (const t of tests) {
    // check cookie-stored variant
    const cookieKey = `ab_test_${t.id}`;
    let variantId = req.cookies && req.cookies[cookieKey] ? Number(req.cookies[cookieKey]) : null;
    if (!variantId) {
      // check existing assignment in analytics
  const row = sessionId ? await analyticsKnex('analytics.ab_assignments').where({ test_id: t.id, session_id: sessionId }).first() : null;
      if (row) variantId = row.variant_id;
    }
    if (!variantId) {
      const variants = await knex('ab_test_variants').where({ test_id: t.id }).select('*');
      if (variants && variants.length) {
        const chosen = pickVariant(variants);
        variantId = chosen.id;
        // persist assignment
        try {
          await analyticsKnex('analytics.ab_assignments').insert({ tenant_id: tenant.id, test_id: t.id, variant_id: variantId, session_id: sessionId || null, user_id: req.user ? req.user.id : null });
        } catch (e) { /* ignore dupes */ }
      }
    }
    if (variantId) {
      req.abTests[t.name] = variantId;
      // set cookie for persistence
      try { res.cookie(cookieKey, String(variantId), { maxAge: 1000*60*60*24*30, httpOnly: false }); } catch(e){}
    }
  }
  next();
};
