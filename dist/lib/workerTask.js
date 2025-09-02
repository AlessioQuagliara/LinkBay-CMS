"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runTaskInWorker = runTaskInWorker;
const worker_threads_1 = require("worker_threads");
function runTaskInWorker(workerFile, workerData, timeoutMs = 10000) {
    return new Promise((resolve, reject) => {
        const worker = new worker_threads_1.Worker(workerFile, { workerData });
        let finished = false;
        const t = setTimeout(() => {
            if (!finished) {
                try {
                    worker.terminate();
                }
                catch (e) { }
                finished = true;
                reject(new Error('worker_timeout'));
            }
        }, timeoutMs);
        worker.on('message', (msg) => { if (!finished) {
            finished = true;
            clearTimeout(t);
            resolve(msg);
        } });
        worker.on('error', (err) => { if (!finished) {
            finished = true;
            clearTimeout(t);
            reject(err);
        } });
        worker.on('exit', (code) => { if (!finished) {
            finished = true;
            clearTimeout(t);
            if (code !== 0)
                reject(new Error('worker_exit_' + code));
            else
                resolve(null);
        } });
    });
}
