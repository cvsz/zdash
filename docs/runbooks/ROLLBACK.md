# ROLLBACK

## Purpose
Rollback app and DB safely.

## Prerequisites
- Recent backups
- Release artifact references

## Commands
```bash
./scripts/backup-db.sh
./scripts/rollback-db.sh
```

## Expected output
- DB revision moved back one step.

## Failure handling
- If rollback fails, restore from backup with `scripts/restore-db.sh`.

## Rollback steps
- Revert deployment to prior image/build.

## Safety notes
- Trigger emergency halt before rollback during incidents.
