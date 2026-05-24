# ECC for Codex CLI

This supplements root project guidance with Codex-specific ECC integration.

## Model Recommendations

| Task Type | Recommended Model |
|-----------|------------------|
| Routine coding, tests, formatting | GPT 5.4 |
| Complex features, architecture | GPT 5.4 |
| Debugging, refactoring | GPT 5.4 |
| Security review | GPT 5.4 |

## Skills Discovery

Skills are expected under `.agents/skills/` with:
- `SKILL.md`
- `agents/openai.yaml`

This environment mounts `.agents` as read-only, so ECC skill assets are indexed in `config/ecc/skills-index.txt`.

## MCP Servers

Treat `config/ecc/codex/config.toml` as the local ECC baseline snapshot.

Managed ECC MCP set:
- `supabase`
- `playwright`
- `context7`
- `exa`
- `github`
- `memory`
- `sequential-thinking`

Use `scripts/sync-ecc-to-codex.sh` to merge these into `~/.codex/config.toml`.

## Multi-Agent Support

ECC sample role configs are vendored to:
- `config/ecc/codex/agents/explorer.toml`
- `config/ecc/codex/agents/reviewer.toml`
- `config/ecc/codex/agents/docs-researcher.toml`

## External Action Boundaries

Treat networked tools as read-only unless explicit user approval is provided for publish/push/post/credential changes.

## Security Without Hooks

1. Validate inputs at boundaries.
2. Never hardcode secrets.
3. Run dependency audits before commit.
4. Review `git diff` before push.
5. Prefer `sandbox_mode = "workspace-write"`.
