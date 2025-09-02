import { Worker } from 'worker_threads';
import path from 'path';

export function runTaskInWorker(workerFile:string, workerData:any, timeoutMs = 10000): Promise<any> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerFile, { workerData });
    let finished = false;
    const t = setTimeout(() => {
      if (!finished) {
        try { worker.terminate(); } catch(e){}
        finished = true;
        reject(new Error('worker_timeout'));
      }
    }, timeoutMs);
    worker.on('message', (msg:any) => { if (!finished) { finished = true; clearTimeout(t); resolve(msg); } });
    worker.on('error', (err) => { if (!finished) { finished = true; clearTimeout(t); reject(err); } });
    worker.on('exit', (code) => { if (!finished) { finished = true; clearTimeout(t); if (code !== 0) reject(new Error('worker_exit_'+code)); else resolve(null); } });
  });
}
