# GraphQL API

The project exposes a GraphQL endpoint at `/graphql`. It supports authentication via `X-API-Key` (preferred for programmatic tenant access) or via a JWT `Authorization: Bearer <token>`.

Example query (curl):

```
curl -X POST http://localhost:3001/graphql \
 -H "Content-Type: application/json" \
 -H "X-API-Key: <YOUR_RAW_KEY>" \
 -d '{"query":"{ getProducts { id name price_cents } }"}'
```

In development, GraphQL Playground/Sandbox may be available depending on server configuration.
