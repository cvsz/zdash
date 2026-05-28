# Backup and Restore Runbook

## Backup Procedure
1. Execute `infra/scripts/backup-postgres.sh`.
2. Verify the backup file exists in the designated S3 bucket or local storage.

## Restore Procedure
1. Halt the application to prevent data inconsistency.
2. Execute `infra/scripts/restore-postgres.sh <backup_file>`.
3. Verify data integrity.
4. Restart the application.
