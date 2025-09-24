import * as http from 'http';

const port = Number(process.env.PORT_BACKEND) || 3000;

const options: http.RequestOptions = {
  hostname: 'localhost',
  port,
  path: '/api/health',
  method: 'GET'
};

const req = http.request(options, (res: http.IncomingMessage) => {
  const status = res.statusCode ?? 0;
  console.log(`STATUS: ${status}`);
  process.exit(status === 200 ? 0 : 1);
});

req.on('error', (err: Error) => {
  console.error('ERROR:', err);
  process.exit(1);
});

req.setTimeout(2000, () => {
  console.error('ERROR: request timed out');
  req.destroy();
  process.exit(1);
});

req.end();