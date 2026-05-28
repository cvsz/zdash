# Worker Queue Model

The worker queue handles asynchronous tasks (e.g., risk checks, data synchronization).

- **Backend**: Redis (with in-memory fallback for local development).
- **Tasks**: Represented by the `WorkerTask` model.
- **Workers**: Run in separate processes or containers, pulling tasks from the queue.

Tasks are tenant-scoped and emit audit events upon completion or failure.
