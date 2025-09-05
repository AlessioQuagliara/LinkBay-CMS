// Lightweight launcher: if server/app.ts exists and ts-node is available, require it.
try {
  // prefer runtime TypeScript execution during migration
  require('ts-node/register');
  require('./app.ts');
} catch (e) {
  // fallback: require the JS express app implementation
  try {
    require('./app.server');
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Failed to start app. Ensure server/app.ts or server/app.server.js exists.', err);
    process.exit(1);
  }
}
