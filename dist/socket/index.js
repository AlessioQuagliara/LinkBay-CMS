"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.io = void 0;
exports.initSocket = initSocket;
exports.notifyUser = notifyUser;
exports.notifyTenant = notifyTenant;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
exports.io = null;
function initSocket(server) {
    const IOServerClass = require('socket.io').Server;
    exports.io = new IOServerClass(server, {
        cors: { origin: '*' }
    });
    // socket auth middleware using JWT from query or auth header
    if (!exports.io)
        return;
    exports.io.use(async (socket, next) => {
        try {
            const token = socket.handshake.auth && socket.handshake.auth.token || socket.handshake.query && socket.handshake.query.token;
            if (!token)
                return next(new Error('auth_required'));
            const payload = jsonwebtoken_1.default.verify(token, process.env.SESSION_SECRET || 'secret');
            // attach user and tenant
            socket.data.user = { id: payload.sub, email: payload.email };
            socket.data.tenant_id = payload.tenant_id || null;
            // join user-specific room and tenant-room
            if (socket.data.tenant_id)
                socket.join(`tenant_${socket.data.tenant_id}`);
            if (socket.data.user && socket.data.user.id)
                socket.join(`user_${socket.data.user.id}`);
            return next();
        }
        catch (err) {
            return next(new Error('invalid_token'));
        }
    });
    if (exports.io) {
        exports.io.on('connection', (socket) => {
            console.log('socket connected', socket.id, socket.data.user && socket.data.user.id);
            socket.on('disconnect', () => console.log('socket disconnected', socket.id));
        });
    }
    return exports.io;
}
function notifyUser(userId, event, payload) {
    if (!exports.io)
        return;
    exports.io.to(`user_${userId}`).emit(event, payload);
}
function notifyTenant(tenantId, event, payload) {
    if (!exports.io)
        return;
    exports.io.to(`tenant_${tenantId}`).emit(event, payload);
}
