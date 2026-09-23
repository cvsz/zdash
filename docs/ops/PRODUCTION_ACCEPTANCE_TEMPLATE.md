# zDash Production Acceptance — Evidence Template

**Status:** PENDING_OPERATOR (do not interpret CI green as production approval)

| Gate | Evidence reference (non-secret) | Verified UTC | Operator | Result |
| --- | --- | --- | --- | --- |
| Release SHA and immutable image digests | TBD | TBD | TBD | PENDING |
| Protected `main`, required checks and reviewed release | TBD | TBD | TBD | PENDING |
| Credential rotation and secrets-manager ownership | TBD | TBD | TBD | PENDING |
| `verify_prod_env.py` against actual operator env | TBD | TBD | TBD | PENDING |
| External HTTPS, DNS, TLS and Cloudflare Access/WAF | TBD | TBD | TBD | PENDING |
| Backend auth, RBAC, tenant isolation and audit | TBD | TBD | TBD | PENDING |
| Synthetic CI PostgreSQL dump/restore/replay | CI run link | TBD | CI | PENDING |
| Isolated *target-host production-data* backup/restore | TBD | TBD | TBD | PENDING |
| Target-host observed RPO and RTO vs approved goals | TBD | TBD | TBD | PENDING |
| Immutable release rollback and post-rollback smoke | TBD | TBD | TBD | PENDING |
| Metrics, alerts, on-call route and incident drill | TBD | TBD | TBD | PENDING |
| No live trading, publishing or IoT mutations enabled | TBD | TBD | TBD | PENDING |
| Final operator sign-off | TBD | TBD | TBD | PENDING |

## Rules

1. Store only redacted non-sensitive evidence references here. Do not embed
   database dumps, customer records, passwords, access tokens, cookies,
   unredacted logs or `.env.production`.
2. Label measured restore times and recovery-point ages explicitly. Do not
   substitute CI's synthetic recovery test for the real target-host drill.
3. All P0 gates must be `PASS` with dated evidence before production
   exposure. A `BLOCKED` or `PENDING` item prevents release approval.
4. Live-execution controls remain disabled until separately approved and
   tested with domain-specific rollback and audit evidence.
5. Record release identifier, previous known-good image digest, maintenance
   window, rollback owner and incident contact **outside** public docs.
