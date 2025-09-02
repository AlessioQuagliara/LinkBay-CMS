import { gql } from 'apollo-server-express';

export const typeDefs = gql`
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
