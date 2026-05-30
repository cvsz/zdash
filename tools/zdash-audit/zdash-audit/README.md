# zDash Deep Dive Review + Audit Pack

Generated: `2026-05-30T13:03:42+00:00`

## Files

```text
docs/reports/zdash-deep-dive-review-audit-2026-05-30.md
docs/prompts/zdash-deep-dive-audit-prompt.md
scripts/deep-scan-zdash.sh
```

## Use inside repo

```bash
chmod +x scripts/deep-scan-zdash.sh
REPO=/path/to/zdash ./scripts/deep-scan-zdash.sh
```

Then run validation in the repo:

```bash
make safety-scan
make validate-fast
make validate
docker compose config
```
