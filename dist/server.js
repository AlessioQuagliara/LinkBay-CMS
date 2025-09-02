"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const app_1 = __importDefault(require("./app"));
const graphql_1 = require("./graphql");
const dotenv_1 = __importDefault(require("dotenv"));
const http_1 = __importDefault(require("http"));
const socket_1 = require("./socket");
const loader_1 = __importDefault(require("./plugins/loader"));
dotenv_1.default.config();
const port = process.env.PORT || 3000;
async function start() {
    const server = http_1.default.createServer(app_1.default);
    (0, socket_1.initSocket)(server);
    const gql = await (0, graphql_1.createGraphQLServer)();
    gql.applyMiddleware({ app: app_1.default, path: '/graphql' });
    server.listen(port, async () => {
        console.log(`LinkBayCMS listening on http://localhost:${port}`);
        try {
            await loader_1.default.loadAndRegisterPlugins();
        }
        catch (e) {
            console.error('plugin loader failed', e);
        }
    });
}
start().catch(err => { console.error('server start error', err); process.exit(1); });
