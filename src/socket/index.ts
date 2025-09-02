import { Server as IOServer, Socket } from 'socket.io';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import { knex } from '../db';
dotenv.config();

export let io: IOServer | null = null;

export function initSocket(server: any) {
  const IOServerClass = require('socket.io').Server;
  io = new IOServerClass(server, {
    cors: { origin: '*' }
  });

  // socket auth middleware using JWT from query or auth header
  if (!io) return;
  io.use(async (socket: Socket, next: any) => {
    try {
      const token = socket.handshake.auth && socket.handshake.auth.token || socket.handshake.query && socket.handshake.query.token;
      if (!token) return next(new Error('auth_required'));
      const payload: any = jwt.verify(token as string, process.env.SESSION_SECRET || 'secret');
      // attach user and tenant
      socket.data.user = { id: payload.sub, email: payload.email };
      socket.data.tenant_id = payload.tenant_id || null;
      // join user-specific room and tenant-room
      if (socket.data.tenant_id) socket.join(`tenant_${socket.data.tenant_id}`);
      if (socket.data.user && socket.data.user.id) socket.join(`user_${socket.data.user.id}`);
      return next();
    } catch (err:any) {
      return next(new Error('invalid_token'));
    }
  });

  if (io) {
    io.on('connection', (socket: Socket) => {
      console.log('socket connected', socket.id, socket.data.user && socket.data.user.id);
      socket.on('disconnect', () => console.log('socket disconnected', socket.id));
    });
  }

  return io;
}

export function notifyUser(userId: number | string, event: string, payload: any) {
  if (!io) return;
  io.to(`user_${userId}`).emit(event, payload);
}

export function notifyTenant(tenantId: number | string, event: string, payload: any) {
  if (!io) return;
  io.to(`tenant_${tenantId}`).emit(event, payload);
}
