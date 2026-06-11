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

```bash
# Run using published artifacts (CI publishes on push to main)
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx:latest --kit ghcr.io/thenickfish/docker-ai-sbx-kit:latest

# Build & publish manually (all-in-one)
docker build -t ghcr.io/thenickfish/docker-ai-sbx:latest . && docker push ghcr.io/thenickfish/docker-ai-sbx:latest && sbx kit push . ghcr.io/thenickfish/docker-ai-sbx-kit:latest

# Local run (without publishing)
docker build -t sbx:latest . && docker image save sbx:latest -o sbx.tar && sbx template load sbx.tar && sbx run claude --template sbx:latest --kit .

# Remove previous sandbox first if needed
sbx rm claude-sbx
```

## rtk usage

```bash
rtk gain          # token savings analytics
rtk discover      # find missed rtk opportunities in history
rtk read <file>   # token-optimized file read (use instead of cat)
```
