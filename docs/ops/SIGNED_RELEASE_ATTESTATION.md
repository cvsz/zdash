# Signed Release Attestation

## Overview

Release attestation provides cryptographic proof that a given release was produced by an authorized build process from a known source commit. Each release produces a signed attestation document and an accompanying JSON manifest.

## What Files Are Attested

| Category | Files |
|----------|-------|
| Version | `VERSION` |
| Reports | `docs/reports/generated/sbom-frontend.json`, `docs/reports/generated/sbom-backend.txt`, `docs/reports/generated/backup-restore-proof.md` |
| Attestation | `docs/reports/generated/release-attestation.json`, `docs/reports/generated/release-attestation.md` |
| Scripts | `scripts/release/generate-sbom.sh`, `scripts/release/backup-restore-proof.sh`, `scripts/release/create-release-attestation.sh`, `scripts/release/verify-p0-p2-completion.sh` |

## Attestation Process

1. **Generate SBOM** — `make sbom` produces `sbom-frontend.json` and `sbom-backend.txt`
2. **Run backup/restore proof** — `make backup-restore-proof` produces `backup-restore-proof.md`
3. **Create attestation** — `make release-attestation` produces:
   - `release-attestation.json` (machine-readable)
   - `release-attestation.md` (human-readable)
4. **Verify P0-P2 completion** — `make phase48-validate` checks all deliverables

## Verification

### Checksum Verification

```bash
cd /path/to/release
sha256sum -c docs/reports/generated/release-attestation.json
```

### GPG Signature Verification

When a GPG signing key is configured:

```bash
gpg --verify docs/reports/generated/release-attestation.json.sig
```

Expected output:

```
gpg: Good signature from "zDash Release Signing Key <releases@zdash.zeaz.dev>"
```

## GPG Signing Flow

### Key Generation (one-time)

```bash
gpg --full-generate-key
# Key type: RSA
# Key length: 4096
# Expiration: 2y
# Real name: zDash Release Signing Key
# Email: releases@zdash.zeaz.dev
```

### Export Public Key

```bash
gpg --armor --export releases@zdash.zeaz.dev > docs/ops/zdash-release-pubkey.asc
```

### Sign Attestation

```bash
gpg --detach-sign --armor \
  -o docs/reports/generated/release-attestation.json.sig \
  docs/reports/generated/release-attestation.json
```

### Verify Signature

```bash
gpg --verify docs/reports/generated/release-attestation.json.sig \
  docs/reports/generated/release-attestation.json
```

## CI Integration Notes

- Attestation runs as a post-build step in GitHub Actions (`release.yml`)
- If `GPG_SIGNING_KEY` is set as a CI secret, the attestation is signed automatically
- If no key is available, `signature_status` is set to `"unavailable"` (not an error)
- Checksums are always generated regardless of signing status
- Attestation JSON is uploaded as a release artifact alongside the frontend bundle

## Example Attestation (JSON)

```json
{
  "version": "0.42.0-rc1",
  "commit": "a1b2c3d4e5f6...",
  "branch": "main",
  "generated_at": "2026-06-02T12:00:00Z",
  "checksums": {
    "sbom-frontend.json": "sha256-hash...",
    "backup-restore-proof.md": "sha256-hash..."
  },
  "signature_status": "key_available",
  "signing_key": "ABCD1234EFGH5678"
}
```

## Security Notes

- Secret keys must never be stored in the repository
- CI signing uses repository secrets, not checked-in keys
- Attestation files in `docs/reports/generated/` are excluded from secret patterns
- Run `make phase48-validate` to verify no secrets leaked into generated reports
