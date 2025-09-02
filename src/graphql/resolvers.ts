import { knex } from '../db';

export const resolvers = {
  Query: {
    getProducts: async (_: any, args: any, ctx: any) => {
      const tenantId = ctx.tenant && ctx.tenant.id;
      if (!tenantId) throw new Error('tenant_required');
      const limit = args.limit || 50;
      return knex('products').where('tenant_id', tenantId).limit(limit);
    },
    getOrders: async (_: any, args: any, ctx: any) => {
      const tenantId = ctx.tenant && ctx.tenant.id;
      if (!tenantId) throw new Error('tenant_required');
      const limit = args.limit || 50;
      return knex('orders').where('tenant_id', tenantId).limit(limit);
    }
  },
  Mutation: {
    createProduct: async (_: any, { input }: any, ctx: any) => {
      const tenantId = ctx.tenant && ctx.tenant.id;
      if (!tenantId) throw new Error('tenant_required');
      const [id] = await knex('products').insert({ tenant_id: tenantId, name: input.name, description: input.description, price_cents: input.price_cents, created_at: new Date() }).returning('id');
      return { id, name: input.name, description: input.description, price_cents: input.price_cents };
    }
  }
};
