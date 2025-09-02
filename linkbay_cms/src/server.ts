import app from './app';
import { createGraphQLServer } from './graphql';
import dotenv from 'dotenv';
import http from 'http';
import { initSocket } from './socket';
import pluginLoader from './plugins/loader';
dotenv.config();

const port = process.env.PORT || 3000;
async function start(){
	const server = http.createServer(app);
	initSocket(server);
	const gql = await createGraphQLServer();
	gql.applyMiddleware({ app, path: '/graphql' });
	server.listen(port, async () => {
		console.log(`LinkBayCMS listening on http://localhost:${port}`);
		try { await pluginLoader.loadAndRegisterPlugins(); } catch(e) { console.error('plugin loader failed', e); }
	});
}

start().catch(err=>{ console.error('server start error', err); process.exit(1); });
