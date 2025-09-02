"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.assignAbTestVariant = void 0;
const db_1 = require("../db");
const analyticsConsumer_1 = require("../lib/analyticsConsumer");
function pickVariant(variants) {
    // variants: [{id,name,traffic_percentage}]
    const total = variants.reduce((s, v) => s + Number(v.traffic_percentage || 0), 0) || 100;
    let r = Math.random() * total;
    for (const v of variants) {
        r -= Number(v.traffic_percentage || 0);
        if (r <= 0)
            return v;
    }
    return variants[0];
}
const assignAbTestVariant = async (req, res, next) => {
    const tenant = req.tenant;
    if (!tenant)
        return next();
    // load active tests for tenant
    const tests = await (0, db_1.knex)('ab_tests').where({ tenant_id: tenant.id, status: 'running' }).select('*');
    if (!tests || tests.length === 0)
        return next();
    const sessionId = req.cookies && req.cookies.session_id ? req.cookies.session_id : (req.query.session_id || null);
    // for each test, ensure we have an assignment
    req.abTests = req.abTests || {};
    for (const t of tests) {
        // check cookie-stored variant
        const cookieKey = `ab_test_${t.id}`;
        let variantId = req.cookies && req.cookies[cookieKey] ? Number(req.cookies[cookieKey]) : null;
        if (!variantId) {
            // check existing assignment in analytics
            const row = sessionId ? await (0, analyticsConsumer_1.analyticsKnex)('analytics.ab_assignments').where({ test_id: t.id, session_id: sessionId }).first() : null;
            if (row)
                variantId = row.variant_id;
        }
        if (!variantId) {
            const variants = await (0, db_1.knex)('ab_test_variants').where({ test_id: t.id }).select('*');
            if (variants && variants.length) {
                const chosen = pickVariant(variants);
                variantId = chosen.id;
                // persist assignment
                try {
                    await (0, analyticsConsumer_1.analyticsKnex)('analytics.ab_assignments').insert({ tenant_id: tenant.id, test_id: t.id, variant_id: variantId, session_id: sessionId || null, user_id: req.user ? req.user.id : null });
                }
                catch (e) { /* ignore dupes */ }
            }
        }
        if (variantId) {
            req.abTests[t.name] = variantId;
            // set cookie for persistence
            try {
                res.cookie(cookieKey, String(variantId), { maxAge: 1000 * 60 * 60 * 24 * 30, httpOnly: false });
            }
            catch (e) { }
        }
    }
    next();
};
exports.assignAbTestVariant = assignAbTestVariant;
