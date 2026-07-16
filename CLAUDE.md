# sbx — Claude Code Sandbox

Two Docker sandbox images with similar tools (rtk, caveman, renovate) pre-installed:
- **claude** — Claude Code agent (`docker/sandbox-templates:claude-code` base)
- **pi** — Pi coding agent (`docker/sandbox-templates:shell` base, Node 24, Pi CLI auto-starts)

## Meta: You Are Likely Running Inside This Sandbox

If you are a Claude Code agent reading this, you are probably running inside a sandbox built from this repository. If you encounter a missing tool, broken behavior, or want to suggest an improvement to the sandbox environment itself, you can propose changes to the source files in this repo (`claude/Dockerfile`, `pi/Dockerfile`, `AGENTS.md`, `claude/spec.yaml`, etc.). Changes take effect after the image is rebuilt and the sandbox is restarted.

## Adding Tools

When adding new tools, do the following:
- ensure the upgrade is managed by Renovate - prefer following the pattern that uses docker-bake.hcl
- update CLAUDE.md and README.md to reflect the new tool
- validate that the container builds still succeed after the change
- if there are tests, update them to test the new tool

## Kit vs Template

- **Template** — the Docker image (built via `docker-bake.hcl`, pushed to GHCR)
- **Kit** — the mixin overlay: `spec.yaml` + any config assets (no image build). Pushed separately via `sbx kit push`. Runs at sandbox start.

When `sbx run` is called: template image is pulled, then the kit's `startup` commands execute on top.

## Critical: spec.yaml is source of truth for sandbox config

`spec.yaml` startup commands overwrite `/home/agent/.claude/settings.json` and `/home/agent/.claude/CLAUDE.md` **on every sandbox start**. Never edit those files directly inside a running sandbox — changes are lost on restart.

**To change sandbox behavior: edit `spec.yaml`**, not the sandbox files.

### What the claude startup command writes

- `settings.json` — rtk `PreToolUse` hook, `skipDangerousModePermissionPrompt: true`, caveman plugin enabled

`AGENTS.md` (caveman activation) is baked into the image — spec.yaml no longer writes it.

## Pi agent config

Pi is a separate coding agent (not Claude Code). It auto-starts in the shell sandbox when an interactive terminal opens.

Key files in `pi/`:
- `spec.yaml` — network policy (allows `localhost` for Ollama), no startup commands needed
- `AGENTS.md` — Pi's equivalent of CLAUDE.md (caveman activation)
- `APPEND_SYSTEM.md` — appended to Pi's system prompt (accuracy/behavior instructions)
- `nebula.json` — Pi color theme (Catppuccin Mocha palette)
- `package.json` — Pi version and extensions (pi-ollama, pi-powerline-footer)
- `settings.json` — Pi agent settings

Pi + Ollama: start Ollama on host with `OLLAMA_HOST=0.0.0.0 ollama serve`, then switch models with `/model` inside Pi.

## Renovate version annotation convention

Renovate uses regex custom managers. Version variables **must** have the exact comment annotation on the line immediately above them — no blank lines between comment and variable.

### docker-bake.hcl — version + commit pair (git-cloned tools)

```hcl
# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.42.3" }
variable "RTK_COMMIT"  { default = "de78d70aee86fe6b7b5c2462820a1b6c250d425b" }
```

Both variables must stay adjacent. Renovate updates `RTK_VERSION` (currentValue) and `RTK_COMMIT` (currentDigest) together.

### docker-bake.hcl — single version (binary releases, no commit hash)

Use `tracking=single` when there's no commit to verify against:

```hcl
# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.13.7" }
```

### Dockerfile — single ARG tracking

```dockerfile
# renovate: datasource=node depName=node tracking=single
ARG NODE_VERSION="24.16.0"
```

### ci.yml — git-refs with currentValue + currentDigest

```yaml
# renovate: datasource=git-refs depName=https://github.com/docker/docker-install currentValue=master
git -C /tmp/docker-install checkout 153e238e1d876160ea4a2a1844ca7f2983bbdd5e
```

## GitHub Actions: always pin to commit SHA

Never use mutable tags (`@v4`). Pin to the full SHA of the latest release:

```yaml
# Good
- uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3

# Bad
- uses: actions/checkout@v4
```

Lookup: `git ls-remote https://github.com/actions/checkout` or the releases page. Add the version tag as a comment.

## Build & run commands

```bash
# Test (mirrors CI)
devbox run test

# Build & push both images + kits (requires GHCR login)
devbox run build

# Validate kits
devbox run kit-validate

# Run from published artifacts (CI pushes on merge to main)
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
sbx run shell  --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest    --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Local build + run
devbox run run-claude
devbox run run-pi

# Cleanup
sbx rm claude-sbx
sbx rm shell-sbx
```

## Testing

`claude/test.py` runs inside the Docker build. CI uses `claude-test` (multi-platform). Run locally:

```bash
devbox run test
```

`test.py` asserts: rtk installed, devbox installed, renovate installed, caveman skills/plugin present, AGENTS.md has caveman line, spec.yaml startup produces correct `settings.json`.

> Tests run inside the Docker build — `docker ps` won't work there (no daemon during build), but works in a running sandbox.

## rtk usage

```bash
rtk gain          # token savings analytics
rtk discover      # find missed rtk opportunities in history
rtk read <file>   # token-optimized file read (prefer over cat)
```

## Devbox

```bash
devbox run renovate-dry-run   # test Renovate config locally (LOG_LEVEL=debug, outputs to /tmp/renovate-dry-run.log)
```
