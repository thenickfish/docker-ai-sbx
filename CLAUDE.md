# sbx — Claude Code Sandbox

Custom Claude Code sandbox template with rtk and caveman pre-installed.

## Critical: settings.json is overwritten on startup

`spec.yaml` startup command overwrites `/home/agent/.claude/settings.json` and `/home/agent/.claude/CLAUDE.md` on every sandbox start. Any manual edits to these files inside the sandbox are lost on restart.

To make permanent changes, edit `spec.yaml` — the startup command is the source of truth.

### What the startup command writes

**settings.json:**
- `PreToolUse` Bash hook: rewrites commands through `rtk hook claude` (e.g. `ls` → `rtk ls`, `git` → `rtk git`)
- `skipDangerousModePermissionPrompt: true`
- Caveman plugin marketplace + enabled

**CLAUDE.md:**
- `On session start: activate /caveman full immediately`

## Installed tooling

- **rtk** — token-optimized CLI proxy. Hook auto-rewrites `ls`, `git`, `gh`, `tree` etc. through rtk. Use `rtk read <file>` instead of `cat`. `cat` is NOT intercepted.
- **caveman** — ultra-compressed communication mode for Claude. Activated automatically on session start.

## Build & run workflow

### Pi + Ollama (local LLM)

Pi is pre-configured with `OLLAMA_HOST=host.docker.internal:11434`. To use it:

1. **Start Ollama on host**, bound to all interfaces:
   ```bash
   OLLAMA_HOST=0.0.0.0 ollama serve
   ```
2. Switch models with `/model` inside Pi.

> `pi-ollama` is pre-installed in the image. Network access to `host.docker.internal` is allowed via `pi/spec.yaml` — no manual setup needed.

---

```bash
# Claude — run using published artifacts (CI publishes on push to main)
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest

# Pi — run using published artifacts
sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Build & publish both images (uses docker-bake.hcl)
docker buildx bake --push && sbx kit push ./claude ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest && sbx kit push ./pi ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest
# Claude — local run (without publishing)
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude

# Pi — local run (without publishing)
docker buildx bake pi-local --load && docker image save sbx-pi:latest -o sbx-pi.tar && sbx template load sbx-pi.tar && sbx run shell --template sbx-pi:latest --kit ./pi

# Remove previous sandboxes if needed
sbx rm claude-sbx
sbx rm shell-sbx
```

## GitHub Actions

When adding new actions, use the latest released version but pin to the full commit SHA:

```yaml
# Good — latest release, pinned to SHA for security
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# Bad — mutable tag, vulnerable to tag hijacking
- uses: actions/checkout@v4
```

Look up the SHA for the current latest release on GitHub (`git ls-remote` or the releases page), then add the version as a comment so it's human-readable.

## rtk usage

```bash
rtk gain          # token savings analytics
rtk discover      # find missed rtk opportunities in history
rtk read <file>   # token-optimized file read (use instead of cat)
```
