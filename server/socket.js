const http = require('http');
const { Server } = require('socket.io');

function startSocketServer(app, initDatabase) {
  async function run() {
    try {
      await initDatabase();
      const PORT = process.env.PORT || 3000;
      const httpServer = http.createServer(app);
      const io = new Server(httpServer, {
        cors: {
          origin: '*',
          methods: ['GET', 'POST']
        }
      });

      // === SOCKET.IO ROOM-BASED ===
      io.on('connection', (socket) => {
        console.log('🟢 Nuova connessione socket:', socket.id);

        // Identificazione: client invia tipo e id
        socket.on('identify', (data) => {
          if (data.type === 'user') {
            socket.join(`user_${data.id}`);
            console.log(`Utente ${data.id} si è unito alla room user_${data.id}`);
          } else if (data.type === 'admin') {
            socket.join(`admin_${data.id}`);
            console.log(`Admin ${data.id} si è unito alla room admin_${data.id}`);
          }
        });

        // Messaggi privati (forward-only): la persistenza è gestita dalle route HTTP server-side
        socket.on('message:private', (data) => {
          try {
            const { fromType, fromId, toType, toId, message, subject, name, email, phone } = data;
            if (!fromType || !fromId) {
              console.warn('Socket message:private received without fromType/fromId, skipping forward:', data);
              return;
            }

            // Inoltra il messaggio alla room appropriata
            const payload = { fromType: fromType || null, fromId, message, name, email, created_at: new Date() };
            if (toType === 'admin') {
              const roomName = `admin_${toId}`;
              const room = io.sockets.adapter.rooms.get(roomName);
              console.log(`Socket forward to ${roomName} | exists=${!!room} | size=${room ? room.size : 0}`);
              io.to(roomName).emit('message:receive', payload);
            } else if (toType === 'user') {
              const roomName = `user_${toId}`;
              const room = io.sockets.adapter.rooms.get(roomName);
              console.log(`Socket forward to ${roomName} | exists=${!!room} | size=${room ? room.size : 0}`);
              io.to(roomName).emit('message:receive', payload);
            }
          } catch (err) {
            console.error('Errore forwarding message via socket:', err);
          }
        });

        socket.on('disconnect', () => {
          console.log('🔴 Disconnessione socket:', socket.id);
        });
      });

      // Rendi io disponibile alle route
      app.set('io', io);

      // DEBUG endpoint (dev only) - restituisce le room attive e la loro dimensione
      // Rimuovere o proteggere in produzione
      app.get('/socket/debug', (req, res) => {
        try {
          const rooms = [];
          for (const [roomName, s] of io.sockets.adapter.rooms) {
            rooms.push({ room: roomName, size: s.size });
          }
          return res.json({ ok: true, rooms });
        } catch (err) {
          return res.status(500).json({ ok: false, error: String(err) });
        }
      });

      httpServer.listen(PORT, () => {
        console.log(`\n✅ Server avviato su http://localhost:${PORT}`);
        console.log(`📧 Mittente SMTP: ${process.env.SMTP_USER}`);
        console.log(`🗄️ Database: ${process.env.DB_NAME}`);
        console.log(`👤 Utente DB: ${process.env.DB_USER}`);
        console.log(`🌐 Ambiente: ${process.env.NODE_ENV}`);
        console.log(`👁️ View Engine: EJS`);
        console.log('🟢 Socket.IO attivo');
      });

      process.on('SIGINT', () => {
        console.log('\n🔴 Server in chiusura...');
        httpServer.close(() => {
          console.log('Server chiuso correttamente');
          process.exit(0);
        });
      });
    } catch (error) {
      console.error('Errore avvio server:', error);
      process.exit(1);
    }
  }
  run();
}

module.exports = { startSocketServer };
