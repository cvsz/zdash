-- zDash Postgres initialization (safe, idempotent)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Keep default public schema grants explicit for predictable local/dev behavior.
GRANT USAGE ON SCHEMA public TO PUBLIC;
