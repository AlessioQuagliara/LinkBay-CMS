"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolvers = void 0;
const db_1 = require("../db");
exports.resolvers = {
    Query: {
        getProducts: async (_, args, ctx) => {
            const tenantId = ctx.tenant && ctx.tenant.id;
            if (!tenantId)
                throw new Error('tenant_required');
            const limit = args.limit || 50;
            return (0, db_1.knex)('products').where('tenant_id', tenantId).limit(limit);
        },
        getOrders: async (_, args, ctx) => {
            const tenantId = ctx.tenant && ctx.tenant.id;
            if (!tenantId)
                throw new Error('tenant_required');
            const limit = args.limit || 50;
            return (0, db_1.knex)('orders').where('tenant_id', tenantId).limit(limit);
        }
    },
    Mutation: {
        createProduct: async (_, { input }, ctx) => {
            const tenantId = ctx.tenant && ctx.tenant.id;
            if (!tenantId)
                throw new Error('tenant_required');
            const [id] = await (0, db_1.knex)('products').insert({ tenant_id: tenantId, name: input.name, description: input.description, price_cents: input.price_cents, created_at: new Date() }).returning('id');
            return { id, name: input.name, description: input.description, price_cents: input.price_cents };
        }
    }
};
