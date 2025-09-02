"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const dbMultiTenant_1 = require("../dbMultiTenant");
const socket_1 = require("../socket");
const router = (0, express_1.Router)();
// List conversations for tenant
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    const tenantDb = (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const convos = await tenantDb('conversations').select('*').orderBy('updated_at', 'desc');
    res.json({ success: true, conversations: convos });
});
// Create conversation
router.post('/', async (req, res) => {
    const tenant = req.tenant;
    const user = req.user;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    const { subject, participants } = req.body;
    const tenantDb = (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const inserted = await tenantDb('conversations').insert({ subject, status: 'open' }).returning('*');
    const convo = Array.isArray(inserted) ? inserted[0] : inserted;
    // add participants
    const parts = participants && Array.isArray(participants) ? participants : [user && user.id];
    for (const p of parts) {
        await tenantDb('conversation_participants').insert({ conversation_id: convo.id, user_id: p });
    }
    // notify participants about new conversation
    for (const p of parts) {
        if (p)
            (0, socket_1.notifyUser)(p, 'conversation.created', { conversation: convo, tenant_id: tenant.id });
    }
    res.json({ success: true, conversation: convo });
});
// List messages for a conversation
router.get('/:id/messages', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    const tenantDb = (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const convId = Number(req.params.id);
    const msgs = await tenantDb('messages').where({ conversation_id: convId }).orderBy('created_at', 'asc');
    res.json({ success: true, messages: msgs });
});
// Post a message to a conversation
router.post('/:id/messages', async (req, res) => {
    const tenant = req.tenant;
    const user = req.user;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    if (!user)
        return res.status(401).json({ error: 'authentication_required' });
    const tenantDb = (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const convId = Number(req.params.id);
    const { body } = req.body;
    const inserted = await tenantDb('messages').insert({ conversation_id: convId, user_id: user.id, body }).returning('*');
    const msg = Array.isArray(inserted) ? inserted[0] : inserted;
    // update conversation updated_at
    await tenantDb('conversations').where({ id: convId }).update({ updated_at: new Date() });
    // notify participants in conversation about new message
    const participants = await tenantDb('conversation_participants').where({ conversation_id: convId }).select('user_id');
    participants.forEach((p) => { if (p && p.user_id)
        (0, socket_1.notifyUser)(p.user_id, 'conversation.message', { message: msg, tenant_id: tenant.id }); });
    res.json({ success: true, message: msg });
});
exports.default = router;
