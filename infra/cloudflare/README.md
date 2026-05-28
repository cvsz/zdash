# Cloudflare Configurations

This directory contains templates and examples for Cloudflare configurations.

**CRITICAL RULE:**
Cloudflare operator automation source of truth belongs in `cvsz/zeaz-platform`.
In `cvsz/zdash`, we only store safe templates, dry-run scripts, docs, and handoff notes.
**NEVER** add real Cloudflare credentials, account IDs, zone IDs, tunnel tokens, or origin certs here.

## Files
- `tunnel-config.example.yml`: Example cloudflared configuration
- `dns-records.example.json`: Example DNS record configuration
- `zero-trust-policy.example.json`: Example Zero Trust access policy
