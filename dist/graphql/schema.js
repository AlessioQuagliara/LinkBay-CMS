"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.typeDefs = void 0;
const apollo_server_express_1 = require("apollo-server-express");
exports.typeDefs = (0, apollo_server_express_1.gql) `
  type Product { id: ID!, name: String!, description: String, price_cents: Int! }
  type Order { id: ID!, status: String!, total_cents: Int! }
  type Page { id: ID!, path: String!, title: String }

  type Query {
    getProducts(limit: Int): [Product]
    getOrders(limit: Int): [Order]
  }

  input CreateProductInput { name: String!, description: String, price_cents: Int! }

  type Mutation {
    createProduct(input: CreateProductInput!): Product
  }
`;
